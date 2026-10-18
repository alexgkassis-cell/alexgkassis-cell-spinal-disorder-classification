# Data are intentionally absent

The original private dataset has 338 image files under `224/Normal/`, `224/Scol/`, `224/Spond/`. Frozen Stage 2 counts:

| Class | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Normal | 48 | 12 | 11 | 71 |
| Scoliosis | 132 | 28 | 28 | 188 |
| Spondylolisthesis | 55 | 12 | 12 | 79 |
| Total | 235 | 52 | 51 | 338 |

Raw files, filenames, split manifest, hash lists, and patient-linked metadata are **not** public. The original split and manifest reside only in the authorized Google Drive. The repository notebooks expect `MyDrive/224` and `MyDrive/Spinal_Classification_Optimization/splits/v1`.

The dataset is **not confirmed patient-disjoint**; grouping near duplicates is not a substitute for patient identifiers. Do not claim medical generalization or add images to this repository without authorization and rights review.
