# Planned work beyond this repository

## Stage 6 — Experimental web interface (not implemented)

Proposed architecture: Python/FastAPI private inference service + Next.js frontend. Upload an authorized spine radiograph, run the **locked C08 preprocessing** (not a newly improvised transform), return three *uncalibrated* model scores, display conspicuous research-only / non-diagnostic messaging, and never imply regulatory approval.

Before any deployment, establish a legitimate dataset/model distribution basis; keep weights server-side and secured; do not log uploaded medical images or identifiers; implement explicit retention policy, access controls and appropriate security review. Consider deploying with synthetic/demo images only until privacy and legal requirements are established.

## Stage 7 — Deployment, validation and documentation

Deploy only after privacy/security reviews and independent external/patient-level evaluation. Do not use the reported image-level 92.16% test accuracy as evidence of clinical safety. Optional further research requires truly new external testing or prospectively collected patient-disjoint cohorts, not iterative selection on the frozen final test partition.

## Stage 6 update

Local Next.js/React website and private FastAPI server are implemented. See `STAGE6_QUICKSTART.md`. Public deployment (Stage 7) is intentionally pending privacy/security review; model weights and patient images remain private.
