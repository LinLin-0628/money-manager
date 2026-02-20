import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const config = await getProxyConfig();
    const { id } = await params;
    const body = await request.json();
    const response = await api.put(`/api/budgets/${id}`, body, config);
    return NextResponse.json(response.data);
  } catch (error: unknown) {
    const err = error as any;
    return NextResponse.json(
      { error: err.response?.data || "Failed to update budget" },
      { status: err.response?.status || 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const config = await getProxyConfig();
    const { id } = await params;
    const response = await api.delete(`/api/budgets/${id}`, config);
    return NextResponse.json(response.data);
  } catch (error: unknown) {
    const err = error as any;
    return NextResponse.json(
      { error: err.response?.data || "Failed to delete budget" },
      { status: err.response?.status || 500 }
    );
  }
}
