import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function GET() {
  try {
    const config = await getProxyConfig();
    const response = await api.get("/api/accounts", config);
    // The backend returns a PaginatedResponse[AccountRead] which has an 'items' field
    return NextResponse.json(response.data.items || []);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data || "Failed to fetch accounts" },
      { status: error.response?.status || 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const config = await getProxyConfig();
    const body = await request.json();
    const response = await api.post("/api/accounts", body, config);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data || "Failed to create account" },
      { status: error.response?.status || 500 }
    );
  }
}
