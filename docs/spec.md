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

## 4. ROCm optimization (to be filled during GPU phase)

- [ ] Baseline: model X fp16 on vLLM-ROCm, TTFT and tokens/sec (bench harness)
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
