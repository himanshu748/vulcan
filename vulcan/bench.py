"""Benchmark harness for the 40-point ROCm optimization story.

Measures time-to-first-token and tokens/sec across prompt sizes, writes
JSON results per backend/config so runs on the Mac and the Radeon box are
directly comparable in the demo video.
"""
from __future__ import annotations

import json
import platform
import statistics
import time
from pathlib import Path

from .config import Config
from .llm import LLM

PROMPTS = {
    "short": "Explain what a race condition is in two sentences.",
    "medium": "Write a Python function that parses a CSV file and returns rows grouped by a key column, with error handling. Explain each part.",
    "long": "Review this design: a local RAG agent indexes a codebase with embeddings in SQLite, then answers questions with a ReAct loop over search/read/grep/test tools. Discuss failure modes, latency bottlenecks and how you would optimize inference on a single consumer GPU. Be thorough.",
}


def run(cfg: Config, label: str, repeats: int = 3, out_dir: Path | None = None) -> dict:
    llm = LLM(cfg)
    results: dict = {
        "label": label,
        "base_url": cfg.base_url,
        "model": cfg.model,
        "platform": platform.platform(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runs": {},
    }
    for name, prompt in PROMPTS.items():
        ttfts, tps = [], []
        for _ in range(repeats):
            r = llm.chat([{"role": "user", "content": prompt}], stream=True)
            gen_time = r.total_s - (r.ttft_s or 0)
            if r.completion_tokens and gen_time > 0:
                tps.append(r.completion_tokens / gen_time)
            if r.ttft_s:
                ttfts.append(r.ttft_s)
        results["runs"][name] = {
            "ttft_s_median": round(statistics.median(ttfts), 3) if ttfts else None,
            "chunks_per_s_median": round(statistics.median(tps), 1) if tps else None,
            "repeats": repeats,
        }
    out_dir = out_dir or Path("bench-results")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{label}.json"
    out_path.write_text(json.dumps(results, indent=2))
    return results
