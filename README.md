# Vulcan

A fully local developer-productivity agent. It indexes your codebase, then reasons, searches, reads, runs tests and answers with cited context, with **every token generated on-device**. Built for the AMD AI DevMaster Hackathon, Track 2 (Agentic AI): local inference on AMD Radeon GPUs via ROCm.

## Why local

Your code never leaves the machine. RAG embeddings, agent reasoning and generation all run on one OpenAI-compatible endpoint you control: Ollama on a laptop during development, vLLM on ROCm for production. Switching backends is one environment variable.

## Quick start

```bash
pip install -e .

# Point at any OpenAI-compatible server (default: Ollama on localhost)
export VULCAN_BASE_URL=http://localhost:11434/v1
export VULCAN_MODEL=qwen3:8b
export VULCAN_EMBED_MODEL=nomic-embed-text

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
