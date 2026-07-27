import json
from pathlib import Path

from vulcan import bench, tools


def test_read_file_blocks_escape(tmp_path: Path):
    assert "escapes" in tools.read_file(tmp_path, "../secrets.txt")


def test_run_cmd_allowlist(tmp_path: Path):
    assert "not in allowlist" in tools.run_cmd(tmp_path, "rm -rf /")


def test_write_and_read_roundtrip(tmp_path: Path):
    tools.write_file(tmp_path, "a/b.txt", "hello")
    assert "hello" in tools.read_file(tmp_path, "a/b.txt")


def test_grep(tmp_path: Path):
    (tmp_path / "x.py").write_text("needle = 1\n")
    assert "x.py:1" in tools.grep(tmp_path, "needle")


def test_bench_compare(tmp_path: Path):
    base = {"label": "laptop", "runs": {
        "short": {"ttft_s_median": 1.0, "chunks_per_s_median": 20.0},
        "medium": {"ttft_s_median": 1.5, "chunks_per_s_median": 18.0},
        "long": {"ttft_s_median": 2.0, "chunks_per_s_median": 15.0}}}
    cand = {"label": "radeon", "runs": {
        "short": {"ttft_s_median": 0.25, "chunks_per_s_median": 60.0},
        "medium": {"ttft_s_median": 0.4, "chunks_per_s_median": 54.0}}}
    b, c = tmp_path / "b.json", tmp_path / "c.json"
    b.write_text(json.dumps(base))
    c.write_text(json.dumps(cand))
    out = bench.compare(b, c)
    assert "3.00x" in out
    assert out.count("|") > 10
    assert "n/a" in out
