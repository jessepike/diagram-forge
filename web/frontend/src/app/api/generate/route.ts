import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const apiUrl = process.env.RAILWAY_API_URL ?? "http://localhost:8000";
  const apiSecret = process.env.RAILWAY_API_SECRET ?? "";

  const body = await request.json();

  const res = await fetch(`${apiUrl}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Secret": apiSecret,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const error = await res.text();
    return NextResponse.json(
      { error: error || "Generation failed" },
      { status: res.status },
    );
  }

  const data = await res.json();
  return NextResponse.json(data);
}
