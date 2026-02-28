import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const apiUrl = process.env.RAILWAY_API_URL ?? "http://localhost:8000";
  const apiSecret = process.env.RAILWAY_API_SECRET ?? "";

  const formData = await request.formData();

  const res = await fetch(`${apiUrl}/extract`, {
    method: "POST",
    headers: { "X-API-Secret": apiSecret },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.text();
    return NextResponse.json(
      { error: error || "Extraction failed" },
      { status: res.status },
    );
  }

  const data = await res.json();
  return NextResponse.json(data);
}
