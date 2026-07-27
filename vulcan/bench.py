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


def compare(baseline_path: Path, candidate_path: Path) -> str:
    """Markdown table contrasting two bench-results runs, for the ROCm
    optimization writeup: same prompts, different backend/config, so the
    only variable is what changed.
    """
    baseline = json.loads(Path(baseline_path).read_text())
    candidate = json.loads(Path(candidate_path).read_text())
    lines = [
        f"| prompt | {baseline['label']} ttft (s) | {candidate['label']} ttft (s) | "
        f"{baseline['label']} tok/s | {candidate['label']} tok/s | speedup |",
        "|---|---|---|---|---|---|",
    ]
    for name in PROMPTS:
        b = baseline["runs"].get(name, {})
        c = candidate["runs"].get(name, {})
        b_tps, c_tps = b.get("chunks_per_s_median"), c.get("chunks_per_s_median")
        speedup = f"{c_tps / b_tps:.2f}x" if b_tps and c_tps else "n/a"
        lines.append(
            f"| {name} | {b.get('ttft_s_median', 'n/a')} | {c.get('ttft_s_median', 'n/a')} | "
            f"{b_tps or 'n/a'} | {c_tps or 'n/a'} | {speedup} |"
        )
    return "\n".join(lines)
