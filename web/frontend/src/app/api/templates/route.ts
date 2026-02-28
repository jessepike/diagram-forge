import { NextResponse } from "next/server";

export async function GET() {
  const apiUrl = process.env.RAILWAY_API_URL ?? "http://localhost:8000";
  const apiSecret = process.env.RAILWAY_API_SECRET ?? "";

  const res = await fetch(`${apiUrl}/templates`, {
    headers: { "X-API-Secret": apiSecret },
  });

  if (!res.ok) {
    return NextResponse.json(
      { error: "Failed to fetch templates" },
      { status: res.status },
    );
  }

  const data = await res.json();
  return NextResponse.json(data);
}
