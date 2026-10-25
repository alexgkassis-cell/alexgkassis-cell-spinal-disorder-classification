# Stage 6 — Launch the Next.js site + C08 inference API

**Research prototype only; not for medical diagnosis.** For public deployment use `docs/STAGE7_DEPLOY.md`; the directions below are for local development.

This website is *not* powered by an online model by default. For predictions,
you must have the original **private, trusted C08 / seed 456 / best-accuracy**
`best_accuracy_model.keras` checkpoint saved in Google Drive during Stage 3F.
Do not publish the checkpoint or patient scans in GitHub.

## Requirements

- **Node.js 20.9+** (Next.js 16)
- **Python 3.11** recommended (TensorFlow-compatible environment)
- The private C08 checkpoint (only for running live predictions)
- Two terminal windows; one runs FastAPI, the other Next.js

## 1 — Prepare the private model

Download this exact file from your OWN Google Drive (it is not in the repo):

`MyDrive/Spinal_Classification_Optimization/experiments/stage3/stability_v1/C08/seed_456/best_accuracy_model.keras`

Save it **outside the Git repository**, e.g. `C:\SpinalModel\best_accuracy_model.keras`
or `~/SpinalModel/best_accuracy_model.keras`.

Optionally look up the selected checkpoint's SHA-256 in your original private Stage 4 file:
`final_evaluation/v1/selection_LOCKED_PRIVATE.json`.

## 2 — Run FastAPI (Terminal 1, from project root)

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[inference]"
python -m pip install -r api/requirements.txt
$env:SPINAL_MODEL_PATH="C:\SpinalModel\best_accuracy_model.keras"
# Optional integrity check using the PRIVATE Stage 4 selection lock:
# $env:SPINAL_MODEL_SHA256="your_64_character_hash"
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

**macOS/Linux/WSL:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[inference]'
python -m pip install -r api/requirements.txt
export SPINAL_MODEL_PATH="$HOME/SpinalModel/best_accuracy_model.keras"
# Optional: export SPINAL_MODEL_SHA256="your_private_sha256_from_stage4"
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Without the checkpoint, omit `SPINAL_MODEL_PATH` and install just `pip install -e .`.
FastAPI starts but indicates `model_unavailable`; the site displays the design
and the research, but analysis is disabled. **It never fabricates scores.**

Check `http://127.0.0.1:8000/health` — `"model_loaded": true` means your model loaded.
Do not use an arbitrary `.keras` checkpoint from the internet.

## 3 — Run Next.js (Terminal 2)

```bash
cd web
npm install
```

Create `web/.env.local` from `web/.env.example` (copy the file or run
`cp .env.example .env.local` on macOS/Linux or
`Copy-Item .env.example .env.local` on Windows PowerShell).

```bash
npm run dev
```

Open **http://localhost:3000**. The **Model connected** pill becomes green
when the FastAPI server is running with the real locked C08 checkpoint.
Select an authorized JPEG or PNG, confirm permission, and analyze it.

## 4 — Add Stage 6 to your existing GitHub repo

Your current repository:
https://github.com/alexgkassis-cell/alexgkassis-cell-spinal-disorder-classification

This ZIP includes the previous Stage 5 repository plus all Stage 6 files in the
*correct* `spinal-disorder-classification/` directory structure.

1. **Don't delete the GitHub repository again.** Clone it to your computer.
2. Extract this archive; open **inside** the `spinal-disorder-classification/` folder.
3. Copy its **contents** into the local clone, preserving the existing `.git/` directory
   and any `LICENSE` you already have. Confirm overwrite of research README/source
   files — Stage 6 updates the preprocessing module without changing its output.
4. `git status` then review changes. Never commit images, `.keras` weights or
   private Google Drive manifests.
5. Commit and push:

```bash
git add README.md STAGE6_QUICKSTART.md .gitignore .github src api web docs tests
git commit -m "Add Stage 6 Next.js research demo and private FastAPI inference"
git push origin main
```

If you are on another branch, replace `main` accordingly.

## Local tests (no private model or images required)

```bash
python -m pip install -e .
python -m pip install -r api/requirements.txt
python -m pip install pytest httpx
python -m pytest -q api/tests tests
cd web && npm run typecheck && npm run build
```

**Privacy warning:** The app is intended first for local demonstration. Do not
publish a public image-uploading endpoint until you have secured auth, HTTPS,
request-size limits at your reverse proxy, rate limits, monitoring and a
proper privacy/clinical-risk review. Details: `docs/STAGE6_WEBAPP.md`.
