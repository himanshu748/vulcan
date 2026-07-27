# Vulcan

A fully local developer-productivity agent. It indexes your codebase, then reasons, searches, reads, runs tests and answers with cited context, with **every token generated on-device**. Built for the AMD AI DevMaster Hackathon, Track 2 (Agentic AI): local inference on AMD Radeon GPUs via ROCm.

## Why local

Your code never leaves machines you control. Agent reasoning and generation run
on one OpenAI-compatible endpoint you own: Ollama on a laptop during
development, vLLM on ROCm for production. Switching backends is one environment
variable.

Embeddings are configured separately, and on the Radeon they are not served by
the same process. `vllm serve Qwen/Qwen3-8B` starts with task=generate, so the
server exposes `/v1/chat/completions` but **no `/v1/embeddings`** (verified:
that route returns 404). Serving embeddings from vLLM needs a second process
started with `--task embed` on an embedding model, and Radeon Cloud allows one
active instance per account. So in the measured setup generation runs on the
Radeon while `VULCAN_EMBED_MODEL` points at a local embedding model. Both are
endpoints you control, and no source ever reaches a third party, but only
generation is GPU-served in this configuration. Point `VULCAN_EMBED_MODEL` at
an `--task embed` vLLM instance to move embeddings onto the GPU as well.

Model sizing matters more than backend flags on a laptop: on a 16GB machine pick a model that leaves headroom (a 4B instruct model runs a full agent turn in ~26s where a 12B thinking model swaps and takes minutes). Prefer non-thinking instruct variants for the agent loop; reasoning preambles multiply per-step latency.

## Quick start

```bash
pip install -e .

# Point at any OpenAI-compatible server (default: Ollama on localhost)
export VULCAN_BASE_URL=http://localhost:11434/v1
export VULCAN_MODEL=qwen3:4b-instruct
export VULCAN_EMBED_MODEL=mxbai-embed-large

vulcan index ~/code/myproject        # build the semantic index
cd ~/code/myproject
vulcan ask "where is auth token validation done?"
vulcan chat                          # multi-turn session with persistent memory
```

## On the Radeon box (ROCm)

```bash
# vLLM with ROCm serves the same API
export VULCAN_BASE_URL=http://localhost:8000/v1
export VULCAN_MODEL=Qwen/Qwen3-8B
vulcan bench --label radeon-vllm-fp16   # TTFT + tokens/sec, saved to bench-results/
```

`vulcan bench` produces comparable JSON across backends and configs (quantization, batch size, ROCm flags), which drives the optimization section of the submission.

## Architecture

- `vulcan/llm.py`: one thin client for chat + embeddings against any OpenAI-compatible server
- `vulcan/rag.py`: line-chunked codebase index, embeddings in SQLite, cosine search (no vector-DB dependency)
- `vulcan/agent.py`: ReAct loop with a JSON tool protocol (works on backends without native tool-calling)
- `vulcan/tools.py`: sandboxed tools, path-jail on file access, allowlisted commands only
- `vulcan/memory.py`: durable per-project notes that survive across sessions
- `vulcan/bench.py`: TTFT / throughput harness for the ROCm optimization writeup

## Tests

```bash
pip install -e ".[dev]"
pytest
```
