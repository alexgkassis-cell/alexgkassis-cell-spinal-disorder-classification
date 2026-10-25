export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const MAX_BYTES = 4 * 1024 * 1024; // Vercel Functions allow 4.5 MB bodies

const responseHeaders = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
function error(message: string, status: number) {
  return Response.json({ detail: message }, { status, headers: responseHeaders });
}

export async function POST(request: Request) {
  const length = request.headers.get("content-length");
  // Early rejection; actual file size checked below even when length is missing.
  if (length && Number(length) > MAX_BYTES + 32_768) return error("Image exceeds 4 MiB limit", 413);

  let form: FormData;
  try { form = await request.formData(); }
  catch { return error("Expected a multipart image upload", 400); }
  const file = form.get("file");
  if (!(file instanceof File)) return error("Select an image first", 400);
  if (!file.size || file.size > MAX_BYTES) return error("Image must be smaller than 4 MiB", 413);
  if (!["image/jpeg", "image/png"].includes(file.type)) return error("Only JPEG and PNG images are supported", 415);

  // In production, require TLS and a server-only shared token. Never
  // forward user images to an unconfigured or plaintext remote service.
  const base = process.env.INFERENCE_API_URL || "http://127.0.0.1:8000";
  const token = process.env.SPINAL_API_TOKEN;
  if (process.env.VERCEL_ENV === "production") {
    if (!base.startsWith("https://") || !token || token.length < 32) {
      return error("The private inference service is not configured.", 503);
    }
  }
  // Send raw image bytes to the private API. The token stays on Next.js.
  const raw = await file.arrayBuffer();
  try {
    const upstream = await fetch(`${base.replace(/\/$/, "")}/predict`, {
      method: "POST", body: raw, cache: "no-store",
      headers: {
        "Content-Type": file.type,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      signal: AbortSignal.timeout(60_000),
    });
    const data: unknown = await upstream.json().catch(() => ({ detail: "Inference server returned invalid JSON" }));
    return Response.json(data, { status: upstream.status, headers: responseHeaders });
  } catch {
    return error("Inference service is unavailable. Check that FastAPI and the private model are running.", 503);
  }
}
