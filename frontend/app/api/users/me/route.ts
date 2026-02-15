// frontend/app/api/users/me/route.ts
import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function GET() {
  try {
    const config = await getProxyConfig();
    const response = await api.get("/api/users/me", config);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data || "Failed to fetch user" },
      { status: error.response?.status || 500 },
    );
  }
}
