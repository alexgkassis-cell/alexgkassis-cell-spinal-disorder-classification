# Dataset description and ethics

- Classes: Normal, Scoliosis, Spondylolisthesis. Images are spinal radiographs (X-rays).
- Total: 338, counts 71/188/79 respectively.
- Frozen v1 split: 235 train, 52 validation, 51 final test.
- The Stage 1 audit found two files with `.png` suffix but JPEG bytes; the older `.jpg`-only loader omitted them.
- Two visually near-duplicate candidate pairs were grouped for splitting. Actual patient IDs were unavailable, **so image-level split ≠ patient-independent split**.
- RGB channel differences between images/classes may reflect processing or acquisition rather than spinal pathology; this is a potential shortcut-learning concern.
- External institutional, demographic, imaging-equipment and site coverage are unverified. The class labels and annotation quality have not been independently clinically adjudicated.

Do not publish original filenames, images, paths to identified patients, hashes of private files, image-level prediction rows, or training checkpoints without legitimate rights and ethical approval. Aggregated counts and result tables are provided without those records. The output cannot be used to guide treatment or triage.
