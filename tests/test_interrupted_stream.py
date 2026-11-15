import json

import httpx
import pytest

from vulcan import agent, bench
from vulcan.config import Config
from vulcan.llm import LLM, ChatResult


class BrokenStream(httpx.SyncByteStream):
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        if self.text:
            frame = {"choices": [{"delta": {"content": self.text}}]}
            yield ("data: " + json.dumps(frame) + "\n\n").encode()
        raise httpx.ReadError("synthetic dropped connection")


def broken_llm(text, monkeypatch):
    calls = []
    monkeypatch.setattr("vulcan.llm.time.sleep", lambda _: None)
    llm = LLM(Config())
    llm._client.close()

    def handler(request):
        calls.append(request)
        return httpx.Response(200, stream=BrokenStream(text))

    llm._client = httpx.Client(base_url="http://synthetic.invalid/v1", transport=httpx.MockTransport(handler))
    return llm, calls


def test_partial_output_raises_without_retry(monkeypatch):
    llm, calls = broken_llm("partial answer", monkeypatch)
    with llm._client:
        with pytest.raises(RuntimeError, match="incomplete") as exc:
            llm.chat([{"role": "user", "content": "q"}], stream=True)
    assert exc.value.partial_text == "partial answer"
    assert isinstance(exc.value.__cause__, httpx.ReadError)
    assert len(calls) == 1


def test_empty_output_keeps_bounded_retries(monkeypatch):
    llm, calls = broken_llm("", monkeypatch)
    with llm._client:
        with pytest.raises(RuntimeError, match="failed after 3 attempts"):
            llm.chat([], stream=True)
    assert len(calls) == 3


def test_interrupted_tool_json_is_not_dispatched(tmp_path, monkeypatch):
    text = '{"tool":"write_file","args":{"path":"x","content":"oops"}}'
    llm, _ = broken_llm(text, monkeypatch)
    monkeypatch.setattr(agent, "LLM", lambda _: llm)
    a = agent.Agent(Config(data_dir=tmp_path / "data"), tmp_path, "t")
    monkeypatch.setattr(a.index, "search", lambda *args, **kwargs: [])
    dispatched = []
    monkeypatch.setattr(a, "_dispatch", lambda *args: dispatched.append(args))
    with llm._client:
        with pytest.raises(RuntimeError, match="incomplete"):
            a.run("synthetic task")
    assert dispatched == []


@pytest.mark.parametrize("axis", ["decode", "concurrency", "prefill"])
def test_benchmarks_count_interrupted_samples_without_scoring(axis, tmp_path, monkeypatch):
    llm, _ = broken_llm("partial", monkeypatch)
    monkeypatch.setattr(bench, "LLM", lambda _: llm)
    with llm._client:
        if axis == "decode":
            report = bench.run(Config(), "interrupted", repeats=2, out_dir=tmp_path)
        elif axis == "concurrency":
            report = bench.run_concurrency(Config(), "interrupted", levels=(2,), out_dir=tmp_path)
        else:
            report = bench.run_prefill(Config(), "interrupted", word_counts=(8,), out_dir=tmp_path)
    for result in report["runs"].values():
        assert result["interrupted"] > 0
        assert result["completed"] == 0
        assert result["ttft_s_median"] is None
        if axis == "decode":
            assert result["chunks_per_s_median"] is None
        if axis == "concurrency":
            assert result["aggregate_chunks_per_s"] is None
            assert result["per_request_chunks_per_s"] is None
    assert json.loads((tmp_path / "interrupted.json").read_text()) == report


def test_decode_benchmark_keeps_only_successful_samples(tmp_path, monkeypatch):
    from vulcan.llm import InterruptedStreamError

    class MixedLLM:
        def __init__(self, cfg):
            self.calls = 0

        def chat(self, messages, stream):
            self.calls += 1
            if self.calls % 2:
                raise InterruptedStreamError("must not count these chunks")
            return ChatResult("ok", 0, 10, 0.1, 1.1)

    monkeypatch.setattr(bench, "LLM", MixedLLM)
    result = bench.run(Config(), "mixed", repeats=2, out_dir=tmp_path)
    for row in result["runs"].values():
        assert row["completed"] == 1
        assert row["interrupted"] == 1
        assert row["chunks_per_s_median"] == 10.0
        assert row["ttft_s_median"] == 0.1
