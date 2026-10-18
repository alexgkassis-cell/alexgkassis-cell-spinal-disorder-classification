# Experimental methodology and chronology

**Stage 1 — Audit.** Verified 338 decodable, 224×224 images: 71 Normal, 188 Scoliosis, 79 Spondylolisthesis. Identified two PNG-named files with JPEG-encoded content; found zero exact duplicate pairs and two potential near-duplicate pairs. Many images were visually grayscale even when encoded as RGB; this raised potential acquisition/processing shortcut concerns.

**Stage 2 — Frozen split.** Training 235; validation 52; test 51. Stratified split with special grouping of candidate near-duplicates, seed 42. Manifest and SHA256 fingerprint were saved privately and checked throughout. Filenames reuse apparent numeric identifiers across people/classes, so they cannot establish true patient independence.

**Stage 3A — Architecture.** Reference CNN E0 reached 49/52 (94.23%) validation; BatchNorm-based E1 collapsed to a single predicted class at inference (12/52, 23.08%); GroupNorm-based E1b reached 44/52 (84.62%). Failure mechanism was not conclusively isolated.

**Stage 3B — Preprocessing.** E0 RGB, E0-G1 grayscale and E0-C1 CLAHE all produced 49/52 on validation at their minimum-loss checkpoints. Validation losses: RGB 0.4373, grayscale 0.3812, CLAHE (clipLimit=2, tiles=8x8) 0.4616.

**Stage 3C–D — CLAHE tuning.** Tested selected clip limits 1, 2, 3 and tile grids 4x4, 8x8, 16x16. C08 (clip=3, 8x8) transiently reached 50/52 at epochs 10 and 13, while minimum-loss checkpoint was 49/52 at epoch 12. Retrospective examination of peaks constitutes validation-directed exploration.

**Stage 3E — C08 reproducibility/dual checkpoints.** Repeated C08 with seed 42 and saved BOTH the best-loss and best-accuracy models. Best-accuracy checkpoint achieved 50/52 (96.15%) validation; macro F1 0.9528. This is a seed-repeat, not an independent patient cohort.

**Stage 3F — Multi-seed.** Compared grayscale E0-G1, CLAHE C01 (clip=1, 4x4), and CLAHE C08 (clip=3, 8x8) across seeds 123, 456, 777 using the identical frozen development split. See [`../results/stability_multiseed_public.csv`](../results/stability_multiseed_public.csv). For best-accuracy checkpoints, C08 mean accuracy 94.23%, C01 93.59%, grayscale 92.95%. C08/seed 456 had 50/52 validation with macro F1 0.9528 and loss ~0.4027, and was chosen over the original seed-42 best-accuracy model because of the lower validation loss.

**Stage 4 — Final once-only held-out evaluation.** Locked checkpoint path, file SHA256 and dataset fingerprint were recorded before decoding the held-out 51 images. Final test: 47/51 = 92.16%, macro F1 0.9152. No model tuning/reselection after the test outcome.

### Why a fixed test set matters

The validation set was examined repeatedly throughout development and used for selection, making it an optimized target. The final test provides a distinct image-level holdout result, but because independence at patient level was unverified and the sample small, it should not be called independent-patient or clinically validated evaluation.
