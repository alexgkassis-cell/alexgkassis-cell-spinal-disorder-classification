# Public repository preflight

Before publication:

- [ ] Confirm that every `.ipynb` has empty code-cell `outputs`, `execution_count=null`, and no embedded attachments.
- [ ] Never upload `224/`, `Normal/`, `Scol/`, `Spond/`, private manifest files, private SHA256 lists, or row-level predictions.
- [ ] Never upload `.keras`, `.h5`, `.onnx`, `.pt`, `.pkl`, `.npy`, `.npz` checkpoints or sensitive logs.
- [ ] Check author and history (`git log`, staged files, and GitHub repository visibility) for exposed personal or medical data.
- [ ] Use only aggregated counts/confusion matrices in public results; remove raw examples and filename-level mistakes.
- [ ] Ensure dataset provenance, licensing, data rights and model-weight usage permissions before distributing any medical images or model weights.
- [ ] Review any future website for upload handling, retention, authentication, and the requirement that this is **not a diagnosis**.
- [ ] Run `python scripts/check_public_repository.py` and `git status --short` before the initial push.

`.gitignore` is a convenience **not** a security boundary. Never use `git add -f` for private files.
