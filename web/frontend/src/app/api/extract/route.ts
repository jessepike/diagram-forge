import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const apiUrl = process.env.RAILWAY_API_URL ?? "http://localhost:8000";
  const apiSecret = process.env.RAILWAY_API_SECRET ?? "";

  const formData = await request.formData();

  let res: Response;
  try {
    res = await fetch(`${apiUrl}/extract`, {
      method: "POST",
      headers: { "X-API-Secret": apiSecret },
      body: formData,
    });
  } catch {
    return NextResponse.json(
      { error: "Backend unavailable" },
      { status: 502 },
    );
  }

  if (!res.ok) {
    let errorMsg = "Extraction failed";
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
