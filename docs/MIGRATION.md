# Research history / migration notes

This repository consolidates source notebooks from the original experimental project and Stages 1–4 of the controlled follow-up study.

- `00_legacy_original_research_ARCHIVE.ipynb` demonstrates earlier classical classification, SVM and CNN attempts. **Its legacy test partition was used during model tuning and validation.** The historical ~92.65% peak cannot be treated as an independent test measurement; newer Stage 4 results use a separate frozen protocol.
- Stage 1–2 notebooks audit the complete 338-image collection and create the frozen manifest and split privately.
- Stage 3 notebooks represent actual research experiment definitions and their checkpointing strategies. Intermediate failures and explored settings remain part of the record.
- Stage 4 code applies the frozen selection to the held-out 51 images and saves the result once. Aggregate final numbers are copied into public results; private outputs are not.
- The new `src/` utility has the **same C08 image preprocessing**, isolated from Colab. It does **not** retrain the archived checkpoint or imply that model weights are freely distributable.
- Original notebook cells were not substantively rewritten; notebook outputs, execution counts and environment-specific cell metadata were removed for a cleaner privacy-conscious public source archive.
