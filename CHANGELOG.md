# Changes

## 2026-10-20 — Blindspot Harvester & Universal Agent Support

- Added **`Blindspot Harvester` (`scripts/blindspot_harvester.py`)** for Phase 2 live candidate discovery (`--discover`) and deep-read `README.md` / model-card technical-fit digestion (`install_commands`, `hardware_and_vram_notes`, `benchmark_and_perf_notes`, `platform_and_license_caveats`).
- Updated `README.md`, `SKILL.md`, and `references/harvest.md` to make `Blindspot` provider-universal across any AI coding agent or assistant and to document the three-part Phase 2 pipeline (`blindspot_harvester.py` + `verify_repos.py` + `build_dashboard.py`).
- Added offline unit tests for `blindspot_harvester.py` in `tests/test_helpers.py` (`10/10` passing).

## 2026-09-23 — Strict verification flags and HTML escaping tests

- Added `--strict` exit codes (`1` on unverified lookup, `2` on invalid/empty input) to `scripts/verify_repos.py`.
- Added offline unit test suite (`tests/test_helpers.py`) covering slug validation, strict mode, license labels, and safe HTML rendering.
