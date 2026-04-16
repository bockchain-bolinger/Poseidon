# Poseidon Roadmap

This roadmap describes the recommended evolution path for Poseidon from its legacy architecture toward a modernized, testable, operator-friendly toolkit.

---

## Phase 1 — Stabilize the upgrade path

Status: **in progress**

### Goals
- establish clean entrypoints
- add a usable headless CLI
- introduce monitoring and OCR service layers
- improve repository professionalism and maintainer workflow

### Current outputs
- `main_v5.py`
- `cli_v4.py`
- `core/adb_handler_v2.py`
- `services/monitoring_service_v2.py`
- `services/vision_service_v2.py`
- `TESTING.md`
- `scripts/smoke_test_v4.sh`

---

## Phase 2 — Validate on real devices

### Goals
- run repeated smoke tests on real Android devices
- verify export paths
- verify OCR behavior across different screens and densities
- tighten failure handling when no device is connected

### Deliverables
- stable operator test matrix
- sample screenshots and OCR test cases
- validated Raspberry Pi workflow

---

## Phase 3 — Consolidate canonical files

### Goals
- promote the new runtime path into the canonical filenames

### Planned promotions
- `main_v5.py` → `main.py`
- `cli_v4.py` → `cli.py`
- `README_v4.md` → `README.md`
- `core/adb_handler_v2.py` → `core/adb_handler.py`

### Outcome
- remove duplicate transitional entrypoints
- reduce ambiguity for operators and contributors

---

## Phase 4 — Deep runtime hardening

### Goals
- safer command execution
- clearer error surfaces
- stronger device state handling
- more consistent structured results

### Focus areas
- device disconnect handling
- timeout behavior
- logging quality
- destructive action safeguards

---

## Phase 5 — Monitoring maturity

### Goals
- expand metrics and exports
- prepare anomaly detection

### Planned items
- richer CPU metrics
- storage metrics
- network metrics where practical
- optional rolling log strategy
- long-running monitoring reliability

---

## Phase 6 — OCR / Vision maturity

### Goals
- improve OCR quality and match selection
- reduce false positives
- support more realistic UI text workflows

### Planned items
- better word grouping
- confidence threshold tuning
- optional preprocessing pipeline
- improved annotation UX
- optional icon / template matching later

---

## Phase 7 — Release readiness

### Goals
- cleaner public release surface
- easier onboarding
- confidence for new users

### Deliverables
- polished canonical README
- release notes
- stable dependency guidance
- reproducible smoke-test workflow
- clearly marked supported path

---

## Long-term direction

Poseidon should evolve into a professional Android operations toolkit with:
- terminal-first diagnostics
- headless automation
- structured monitoring
- OCR-assisted UI workflows
- Raspberry Pi friendly deployment
- staged, safe runtime upgrades
