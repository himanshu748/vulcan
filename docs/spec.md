# Vulcan, project specification (Track 2, Agentic AI)

> Submission requirement: project specification document with scenarios, architecture, capabilities and optimization details.

## 1. Scenario and users

Developers working on private or regulated codebases cannot send source code to cloud LLM APIs. Vulcan is a developer-productivity agent that runs entirely on a local AMD Radeon GPU: codebase Q&A with citations, bug localization, test execution and code edits, with zero data egress.

## 2. Architecture

```
user ── CLI (typer) ── Agent (ReAct loop, JSON tool protocol)
                          ├─ RAG index (SQLite + cosine, embeddings from GPU backend)
                          ├─ Tools (search_code, read_file, grep, run_cmd*, write_file)   *allowlisted
                          ├─ Memory (durable per-project notes)
                          └─ LLM client ── OpenAI-compatible endpoint
                                             └─ vLLM on ROCm / Radeon GPU
```

## 3. Capabilities

- Multi-turn codebase Q&A with file:line citations
- Autonomous tool use: semantic search, file reading, grep, test runs, edits
- Persistent memory across sessions per project
- Backend-agnostic: same agent on Ollama, llama.cpp or vLLM-ROCm

## 4. ROCm optimization

### 4.1 Measurement methodology

Every number below comes from `vulcan bench`, which streams three fixed
prompts (short, medium, long) and records time-to-first-token and generation
rate, taking the median of 5 repeats. The harness is the same code on both
platforms, so the only variable is the backend.

Two honesty caveats that shape how the numbers should be read:

- **The Radeon runs are measured over an HTTPS proxy, not on the box.** The
  instance's SSH port is not reachable from the client network, so the client
  talks to vLLM through the Radeon Cloud spaces proxy. Median round-trip to
  that proxy was measured at **0.216s** immediately before the run, and that
  RTT sits inside every reported TTFT. GPU-side TTFT is therefore roughly
  `reported - 0.216`.
- **"Tokens/sec" is really content-deltas/sec.** The harness counts streamed
  SSE deltas, not tokenizer tokens. Deltas can coalesce in transit, so the
  proxied Radeon figure is a slight undercount relative to the local run.

Cold start matters and is reported rather than hidden: the first two
repetitions of each prompt carry cache-warming cost, and the run is only
stable from roughly the third repetition. Taking the median of 5 keeps a
single cold outlier from dominating while still not discarding it.

### 4.2 Hardware comparison

Same model, both platforms, so the comparison isolates hardware. See
`bench-results/` for the raw JSON and Section 4.3 for the generated table.

### 4.3 Results

<!-- filled from: vulcan bench-compare bench-results/<baseline>.json bench-results/<candidate>.json -->

### 4.4 Remaining sweeps

- [ ] Quantization sweep: fp16 vs int8/awq, quality vs speed
- [ ] vLLM tuning: gpu-memory-utilization, max-num-seqs, chunked prefill
- [ ] Embedding throughput on GPU vs CPU
- [ ] Before/after charts for the demo video

## 5. Demo video outline (3 to 5 min)

1. Problem: private code, no cloud (20s)
2. Index a real repo live, show GPU utilization (40s)
3. Multi-turn session: locate a bug, run tests, fix, re-run (2 min)
4. Benchmark screen: optimization journey on Radeon (1 min)
5. Architecture slide and close (30s)
