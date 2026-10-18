# Publish to GitHub (after privacy review)

Choose repository name: `spinal-disorder-classification`. For your first upload, a **private GitHub repository is recommended** until you confirm licenses and inspect the staged file list.

1. Extract this ZIP locally.
2. Open a terminal in the extracted `spinal-disorder-classification` folder.
3. Install dependencies and run `pytest -q` and `python scripts/check_public_repository.py`.
4. Initialize the repository and inspect the staged file names:

```bash
git init
git branch -M main
git add .
git status --short
```

5. Confirm no private images or weight files were staged. Create an **empty** GitHub repository of the same name (without a README; this package already has one).
6. Run (replace `YOUR_USERNAME`):

```bash
git commit -m "Publish research notebooks and held-out evaluation"
git remote add origin https://github.com/YOUR_USERNAME/spinal-disorder-classification.git
git push -u origin main
```

If Git asks for authentication, use GitHub's supported browser/CLI authentication rather than pasting credentials into a notebook or this chat. No repository has been created or pushed automatically by this package.

Before making the GitHub repository public, choose a code license and review `docs/PRIVACY_CHECKLIST.md`.
