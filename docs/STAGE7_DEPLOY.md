# Stage 7 — Publish SpineLab (Vercel + Railway)

This runbook publishes the **already-tested, unchanged** C08 seed-456 model.
Validation = **96.15% (50/52)**; frozen held-out test = **92.16% (47/51)**.
These are image-level results on a small dataset; independent patients could not be verified.
**No clinical decision-making, diagnosis or patient care use.**

## 0. Before you publish

- Be the authorized owner/operator of this research demo. Confirm you have
  permission to run the original trained model on your chosen hosting provider.
- No X-rays, identifying filenames, `.keras` weights, private manifests,
  `.env.local` or patient-level predictions in a public repo or Docker image.
- Read your providers' data handling and logging policies before accepting any
  uploaded medical images. The public Next.js route limits uploaded files to 4 MiB (below Vercel’s
  4.5 MB function payload limit). The app processes images in memory and does not
  intentionally store them, but intermediaries/providers may handle request data.
- Only upload *de-identified, explicitly authorized images*. A checkbox is not
  a substitute for medical data compliance or informed consent.
- **Configure Vercel Firewall rate limiting on `/api/predict` before sharing
  publicly.** Consider an authentication or invite gate for a first release.
  Do not treat an unrestricted public upload service as safe by default.

## 1. Update the existing GitHub repository (no deletion)

Repository: https://github.com/alexgkassis-cell/alexgkassis-cell-spinal-disorder-classification

Extract the accompanying Stage 7 ZIP and copy **contents of its inner
`spinal-disorder-classification/` folder** into your local Git clone; keep `.git/`
and the original LICENSE. Preserve any other repo-specific files, review diffs,
then:

```powershell
git status
git add README.md STAGE6_QUICKSTART.md Dockerfile .dockerignore .gitignore .github api docs src tests web results
git diff --cached --stat
git commit -m "Deploy-ready SpineLab web and protected C08 inference service"
git push origin main
```

*If your default branch isn't `main`, use its actual name.*
Run `git ls-files | findstr /i ".keras .dcm _PRIVATE .env.local"` and review
its output before pushing. The supplied repository passes a privacy preflight
in the packaging environment; **review your own working directory too**.

## 2. Deploy the Python API to Railway

Official references:
- https://docs.railway.com/guides/fastapi
- https://docs.railway.com/cli/volume
- https://docs.railway.com/volumes

1. Sign in to https://railway.com/ with GitHub, create a project → **Deploy from
   GitHub Repo**, choose this repository. Use the root **`Dockerfile`**.
   Keep **Root Directory = repository root** (not `web`).
2. Set service variables in Railway:
   - `SPINAL_REQUIRE_TOKEN=1`
   - `SPINAL_API_TOKEN=<a long random server-only secret>`
   - `SPINAL_MODEL_SHA256=<original hash from private Stage 4 selection lock>`
   - Initially **omit** `SPINAL_MODEL_PATH` until the private model is uploaded.
3. Generate a secret locally, for example:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Copy its value to a private password manager. Do **not** commit it.
4. In the Railway service, attach a **private persistent volume** mounted at
   `/models`. Do not use a public bucket or public GitHub for the checkpoint.
5. Install Railway CLI (see https://docs.railway.com/guides/cli), authenticate
   with `railway login`, then run `railway link` within your local clone and
   choose this project/service.
6. From the Windows machine that already has the private Stage 3F checkpoint:

   ```powershell
   railway volume files upload "C:\SpinalModel\best_accuracy_model.keras" /best_accuracy_model.keras
   ```

   If multiple Railway volumes exist, specify the correct one with the
   documented `--volume` selector; volume commands address the **volume root**,
   so `/best_accuracy_model.keras` is accessible at `/models/best_accuracy_model.keras`
   inside the container.
7. Confirm uploaded bytes/hash against your private Stage 4 selection lock.
   Then set `SPINAL_MODEL_PATH=/models/best_accuracy_model.keras` and redeploy.
   Confirm startup logs show the app healthy. If it fails the hash, **stop**.
8. Under Railway **Settings → Networking**, generate the API's HTTPS domain.
   Verify `https://<api-domain>/health` reports `model_loaded: true`.
9. Verify **direct anonymous POST `/predict` receives HTTP 401**. Railway
   should only serve requests authenticated with the shared token sent by the
   Next.js server route; never expose that token in the browser.

The backend uses one CPU TensorFlow process and may require a paid Railway plan
with enough RAM for TensorFlow. Monitor container memory and prediction latency.

## 3. Deploy Next.js on Vercel

Official reference: https://vercel.com/docs/monorepos

1. Sign in to https://vercel.com/ with GitHub → **Add New → Project** → Import
   the same repository.
2. **Root Directory = `web`**. Framework Preset = **Next.js**.
3. Under Vercel **Project Settings → Environment Variables**, set these
   **server-only** variables in the **Production** environment:
   - `INFERENCE_API_URL=https://<your-railway-api-domain>`
   - `SPINAL_API_TOKEN=<the SAME long token set on Railway>`
4. Never prefix the token with `NEXT_PUBLIC_`. Never add secrets to `.env.example`
   or commit `.env.local`.
5. Deploy production. The web app talks server-to-server to the Railway HTTPS
   endpoint. Browser users only reach the Next.js same-origin `/api/predict`.
6. In **Vercel → Firewall**, set a **rate-limiting rule** for requests to
   `/api/predict` before sharing. Start with a low number of requests per
   minute per visitor; tune to your hosting budget. Consider bot protections
   and an invite gate for initial launch.

**Important:** Simply deploying the frontend without a working Railway backend
will show a public website with analysis unavailable; it will **not** fabricate
predictions. Do not claim the classifier is publicly running unless the public
frontend health and authorized inference flow both work.

## 4. Check your live site before announcing it

- Home page renders with the updated heading **“Research results.”**
- `/api/health` from the site reports C08 seed 456 and `model_loaded: true`.
- A *synthetic or otherwise properly authorized, de-identified* image can be
  uploaded and returns a model score. Do not use private patient data for
  a production smoke test.
- Rate limits work; repeated requests above your threshold are blocked.
- Direct unauthenticated Railway POST returns `401`.
- Browser developer tools / page source expose **neither checkpoint bytes,
  server tokens nor original private patient images**.
- HTTPS is enabled on both Vercel and Railway. Verify cache disabled.
- The README shows the actual live URL **only after the deployment exists**.
- Privacy and research-only notices remain clearly visible. No treatment advice.

After the public deployment, update the repository README with your live Vercel
URL and (optionally) a screenshot of the UI containing no patient data.

## Troubleshooting

- Health says `model_unavailable`: the Railway volume file isn't present or
  `SPINAL_MODEL_PATH` is unset. Verify mounted volume and redeploy.
- Railway startup fails with token error: make `SPINAL_API_TOKEN` 32+ characters.
- Railway startup fails with model error: verify file location, SHA256, trusted
  checkpoint and TensorFlow compatibility. Never download arbitrary `.keras` files.
- Next.js says inference service unavailable: check `INFERENCE_API_URL`, token
  equality, provider environment, and Railway logs (without image bytes).
- Vercel build error: confirm Root Directory is precisely `web` and Node.js 22.
