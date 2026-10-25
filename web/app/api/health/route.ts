export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const base = process.env.INFERENCE_API_URL || "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${base.replace(/\/$/, "")}/health`, {
      method: "GET", cache: "no-store", signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) throw new Error("API health endpoint unavailable");
    const result = await response.json();
    return Response.json(result, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return Response.json(
      { status: "offline", model_loaded: false, research_only: true },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }
}
