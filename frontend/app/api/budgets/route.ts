import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function GET() {
  try {
    const config = await getProxyConfig();
    const response = await api.get("/api/budgets", config);
    // The backend returns a PaginatedResponse[BudgetRead] which has an 'items' field
    return NextResponse.json(response.data.items || []);
  } catch (error: unknown) {
    const err = error as any;
    return NextResponse.json(
      { error: err.response?.data || "Failed to fetch budgets" },
      { status: err.response?.status || 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const config = await getProxyConfig();
    const body = await request.json();
    const response = await api.post("/api/budgets", body, config);
    return NextResponse.json(response.data);
  } catch (error: unknown) {
    const err = error as any;
    return NextResponse.json(
      { error: err.response?.data || "Failed to create budget" },
      { status: err.response?.status || 500 }
    );
  }
}
