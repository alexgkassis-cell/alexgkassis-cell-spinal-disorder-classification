# Stage 6 — Next.js research demo and private inference architecture

## System diagram

```text
[Browser, http://localhost:3000]
   |- Next.js 16 App Router / React 19 UI
   |   - drag/drop or browse to preview X-ray locally
   |   - consent checkbox before submission
   |   - scores shown as uncalibrated model outputs
   |
   +-> POST /api/predict  [Next.js same-origin, server-only proxy]
          | - validate PNG/JPEG, file size <=4 MiB (public proxy)
          | - forward raw bytes with correct content type
          v
       POST http://127.0.0.1:8000/predict [FastAPI]
          | - stream <=8 MiB into memory, no multipart temp files
          | - check actual JPEG/PNG encoding and image dimension limit
          | - EXIF transpose -> RGB -> LANCZOS pad to 128x128
          | - grayscale -> CLAHE clip 3.0, grid 8x8 -> float32/255
          | - trusted private .keras (C08, seed 456, epoch 11)
          +-> normal / scoliosis / spondylolisthesis softmax scores

GET /api/health -> GET FastAPI /health (offline status if model unavailable)
```

## Research provenance and locked preprocessing

`src/spinal_classifier/preprocessing.py` is used by the original CLI and API.
The input to the frozen CNN is **(1,128,128,1)**; output is the class-order
`[Normal, Scoliosis, Spondylolisthesis]`. Never change the preprocessing order,
normalization factor, output label order or model architecture post-test and
still claim the historical **92.16% final-test** accuracy. Stage 4 was a
one-time image-level evaluation; patient independence could not be verified.

- **Validation:** 50/52 = 96.15%, macro-F1 0.9528 (selected on this set)
- **Held-out test:** 47/51 = 92.16%, macro-F1 0.9152; 95% Wilson interval 81.50–96.91%
- Model: reference CNN with 4,287,491 parameters; seed 456; selected epoch 11
- Sources: `docs/RESULTS.md`, `results/final_test_metrics_public.json`

The model emits three softmax numbers, but they are **not calibrated clinical
confidence probabilities**. The UI calls them model scores, labels the result
as non-diagnostic and does not suggest treatment. Do not treat these results as
clinically meaningful without independent, patient-disjoint multi-site testing.

## Deployment and privacy precautions

- The private model stays **outside the GitHub repo** and is read from a trusted
  `SPINAL_MODEL_PATH` environment variable only. If configured,
  `SPINAL_MODEL_SHA256` verifies the original private Stage 4 lock.
- No model weights or patient images are bundled in this public ZIP.
- The browser creates only a local object-URL preview; it revokes the URL when
  the file is changed/removed. No browser localStorage/sessionStorage is used.
- Next.js's server route checks file format/size before forwarding raw bytes;
  FastAPI streams those bytes in memory (not through disk-spooling multipart).
  Images are not logged, persisted, or sent to analytics by application code.
- `Cache-Control: no-store` is set on the inference routes.
- API is bound to **127.0.0.1** for local development; browser connects only
  to same-origin Next.js routes, so no permissive CORS rules are necessary.
- Request logs may still include route paths and IPs; keep process logs private.
- **Do not deploy publicly yet.** Before offering it to anyone, add properly
  reviewed consent & privacy notice, TLS everywhere, authenticated access,
  reverse-proxy upload limits, rate limiting/abuse protection, retention policy,
  error reporting without PHI, and a clinical-risk assessment. Host the Python
  API on an appropriate private server; it does not run on Edge or as a normal
  Next.js/Vercel function.
- Consider removing Next.js's public access to `/api/predict` or placing both
  services behind VPN/auth in public environments.

## Checks and limitations

`api/tests/` uses synthetic image bytes and an injected fake test model;
never confuse this fixture with deployed real inference. The actual model is
only loaded when `SPINAL_MODEL_PATH` is configured on the API server. The
`tests/test_stage6_memory_preprocessing.py` regression verifies the on-disk
and in-memory preprocessing implementations produce identical bytewise arrays
for a synthetic image. Actual checkpoint inference requires the private model
and has not been executed in this packaging environment.

Use `python -m pytest -q api/tests tests` to run the tests. Use
`cd web && npm install && npm run typecheck && npm run build` to verify
Next.js in an environment with npm access.


## Public release note

The Stage 7 deployment adds bearer-token authorization and a private Railway
volume. See `docs/STAGE7_DEPLOY.md` for current publication instructions.
