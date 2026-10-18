# Spinal disorder classification from X-ray images

**Reproducible ML research · Three-class CNN · Image-level held-out evaluation**

This project explores classification of spinal radiographs into **Normal**, **Scoliosis**, and **Spondylolisthesis** using an iterative, validation-guided CNN workflow. It preserves the original research notebook and the subsequent dataset audit, preprocessing, architecture, CLAHE, stability, and final test notebooks.

> [!IMPORTANT]
> **Research/educational prototype only. Not a medical device, not clinically validated, and not intended for diagnosis or treatment.** Performance is on a small historical dataset; patient identities and patient-independent split status could not be verified. No raw medical images, private identifiers, model weights, or per-image predictions are distributed.

## Final results — model locked before testing

| Metric | Validation (used for selection) | Final held-out test (evaluated once) |
|:--|--:|--:|
| Images | 52 | 51 |
| Correct | 50 | 47 |
| **Accuracy** | **96.15%** | **92.16%** |
| Macro F1 | 0.9528 | 0.9152 |
| Balanced accuracy | 0.9603 | 0.9156 |

**Selected model:** reference CNN, grayscale + CLAHE (`clipLimit=3.0`, `tileGridSize=(8,8)`), 128×128 images, training seed **456**, checkpoint at epoch **11**, selected by maximum validation accuracy (lower loss breaks ties). No retraining or reselection occurred after inspecting the final held-out test.

**Final-test confusion matrix** (rows = true labels, columns = predictions):

| | Pred. Normal | Pred. Scoliosis | Pred. Spondylolisthesis |
|:--|--:|--:|--:|
| **Normal** | 9 | 2 | 0 |
| **Scoliosis** | 1 | 26 | 1 |
| **Spondylolisthesis** | 0 | 0 | 12 |

Class recalls: Normal **81.82%** (9/11); Scoliosis **92.86%** (26/28); Spondylolisthesis **100%** (12/12). Descriptive 95% Wilson accuracy interval **81.50–96.91%**, subject to the important dataset and patient-independence limitations below. These results are not an independent clinical assessment. See [`results/`](results/) and [`docs/RESULTS.md`](docs/RESULTS.md).

## Dataset and protocol

- **338 images**, classes: 71 Normal, 188 Scoliosis, 79 Spondylolisthesis.
- Frozen split: **235 training / 52 validation / 51 test** (seed 42).
- Frozen manifest includes file hashes and grouped potential near duplicates; actual patient identities were **not** available, and the split is **not demonstrated to be patient-disjoint**.
- Selection used only validation data; the 51-image test partition was used for a **single locked final evaluation**.
- Prior exploratory work optimized several hyperparameters and seeds using the same 52 validation images, so the best observed validation accuracy is optimistic and should not be treated as external generalization.

See [`docs/DATASET_AND_ETHICS.md`](docs/DATASET_AND_ETHICS.md) and [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Research timeline

| Stage | Contents | Status |
|:--|:--|:--|
| 1 | Dataset audit, class distribution, images, duplicates and color differences | Complete |
| 2 | Persist and hash-lock the v1 train/validation/test split | Complete |
| 3A | Baseline CNN, BatchNorm and GroupNorm CNNs | Complete |
| 3B | RGB, grayscale, grayscale + CLAHE | Complete |
| 3C | CLAHE clip limits and tile grids | Complete |
| 3D | Dual checkpoints (best loss / best accuracy) | Complete |
| 3E | Reproduce C08's 96.15% validation peak with a saved model | Complete |
| 3F | Multi-seed stability check of C08, C01 and grayscale | Complete |
| 4 | Lock C08/seed 456 and evaluate 51-image test once | Complete |
| 5 | Archive research source, code, docs and aggregate metrics | This repository |
| 6–7 | Optional experimental upload-to-classify demo and deployment | Not implemented |

## Repository contents

```text
notebooks/                 Original research + Stage 1–4 Colab notebooks (outputs stripped)
src/spinal_classifier/     Exact locked preprocessing, model topology, private local inference
results/                   Aggregate results only: no images, paths or per-image predictions
docs/                      Method, limitations, dataset, migration, reproducibility and roadmap
tests/                     Synthetic-data regression tests
scripts/                   Public artifact/privacy preflight checker
.github/workflows/         Synthetic-data CI, no dataset or model required
```

## Reproduce on Colab (authorized data required)

1. Obtain **authorized access** to the original private data in Google Drive; nothing is bundled here. Expected private Drive folder: `MyDrive/224/{Normal,Scol,Spond}`.
2. Run notebook `01_dataset_audit_and_frozen_split.ipynb` to create/verify the **original frozen Stage 2 split**. **Do not create a fresh split and compare it to the published results.** If you cannot access the original split manifest, the exact reported run cannot be reproduced.
3. The ordered Stage 3 notebooks show architecture/preprocessing comparisons, CLAHE parameter searches and seed stability tests. They write experiment artifacts privately to `MyDrive/Spinal_Classification_Optimization/`.
4. `08_stage4_FINAL_heldout_evaluation.ipynb` documents the already-completed one-time final evaluation. **Do not rerun it on the original 51-image test set to tune/select models.** Use its saved locked aggregate results.

Original private selected checkpoint: `Spinal_Classification_Optimization/experiments/stage3/stability_v1/C08/seed_456/best_accuracy_model.keras` under the owner's `MyDrive`. It is **not included** in this repo.

## Local code and synthetic-data tests

Python 3.10+:

```bash
python -m venv .venv
# Activate the environment:
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e '.[dev]'
pytest -q
python scripts/check_public_repository.py
```

TensorFlow is deliberately optional. With **your own authorized local copy** of the selected `.keras` checkpoint, install `pip install -e '.[inference]'`, then use:

```bash
python -m spinal_classifier.inference --model /path/to/private/best_accuracy_model.keras --image /path/to/authorized/image.jpg
```

This prints experimental class scores and a **non-diagnostic** label. The CLI does not transmit images or save predictions. For fully reproducible testing, use the matching TensorFlow/OpenCV environment noted in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Historical notebook caveat

`00_legacy_original_research_ARCHIVE.ipynb` is **archived for provenance, not for rigorous evaluation**. That notebook reused its test partition to tune classical models and as CNN validation, so historical ~92.65% results should **not** be conflated with the locked 2026 final test score. The original code is retained, but outputs are stripped for privacy and to avoid confusion.

## Publishing and responsible reuse

Review every file before making this repository public. `.gitignore` excludes raw X-rays, checkpoint formats, private manifests, local logs, and other artifacts, but **Git ignore rules cannot protect files explicitly force-added**. Do not commit patient data, protected health information, Google Drive exports, private IDs or model weights. Licensing and rights to images/weights have not been established; no dataset or model-weights license is granted here.

See [`docs/PRIVACY_CHECKLIST.md`](docs/PRIVACY_CHECKLIST.md). Source-code licensing can be chosen by the repository owner before public release.
