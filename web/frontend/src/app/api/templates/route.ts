import { NextResponse } from "next/server";

export async function GET() {
  const apiUrl = process.env.RAILWAY_API_URL ?? "http://localhost:8000";
  const apiSecret = process.env.RAILWAY_API_SECRET ?? "";

  let res: Response;
  try {
    res = await fetch(`${apiUrl}/templates`, {
      headers: { "X-API-Secret": apiSecret },
    });
  } catch {
    return NextResponse.json(
      { error: "Backend unavailable" },
      { status: 502 },
    );
  }

  if (!res.ok) {
    let errorMsg = "Failed to fetch templates";
    try {
      const json = await res.json();
      errorMsg = json.detail ?? errorMsg;
    } catch {
      const text = await res.text();
      if (text) errorMsg = text;
    }
    return NextResponse.json({ error: errorMsg }, { status: res.status });
  }

  const data = await res.json();
  return NextResponse.json(data);
}
