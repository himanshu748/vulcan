# AMD AI DevMaster submission checklist

Track 2, Private AI Agents. Deadline **2026-08-06, 21:29 GMT+5:30**.

## Mechanism

Fork `github.com/AMD-DEV-CONTEST/Radeon-hackathon-2026-07` and open a PR.

- PR title must be exactly the convention: `Track 2, <team name>, <application name>`
- Everything in **English**, PR body included.

Checked against the 27 PRs already open on that repo: the ones that read
cleanly put every file under **one top-level folder** named for the project
(for example `1bit-systems/`, `amd-inventory-agent/`, `parceltracking/`).
Several PRs dump files at repo root instead, which collides with other
entrants. Use a folder:

```
vulcan/
  README.md                     # setup + usage, the judge's entry point
  spec-document.md              # required Project Specification Document
  poster.md (or .pdf)           # required supplementary material
  demo-video.mp4                # 3 to 5 minutes
  bench-results/*.json          # raw ROCm evidence
  vulcan/ ...                   # source
```

## Required deliverables (Track 2)

| # | Item | State |
|---|---|---|
| 1 | Project Specification Document | `docs/spec.md`, written |
| 2 | Complete source code with README | written, tests 5/5 green |
| 3 | Demo video, 3 to 5 min | **NOT DONE**, needs a screen recording |
| 4 | Supplementary material (PPT or poster) | `docs/deck.md` drafted, needs export |

## Judging weights

- 60 pts functional completeness and value
- 40 pts Radeon/ROCm optimization, including local inference speed

The 40-point half is the one most entrants under-serve. Vulcan's evidence is
the measured `enable_thinking: false` result plus the same-model cross-hardware
table, both reproducible from `bench-results/` with `vulcan bench-compare`.

## Eligibility, already satisfied

- AMD AI Developer Program membership: done 2026-07-16 (required for prizes)
- Luma registration approved: 2026-07-16
- India is not on the excluded-countries list

## Open items

- [ ] Public GitHub repo for the source (no git remote exists yet)
- [ ] Record the demo video against the Radeon endpoint
- [ ] Export `docs/deck.md` to PDF or PPT
- [ ] Fork + PR
