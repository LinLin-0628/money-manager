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
    const response = await api.put(`/api/transactions/${id}`, body, config);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data || "Failed to update transaction" },
      { status: error.response?.status || 500 }
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
    const response = await api.delete(`/api/transactions/${id}`, config);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data || "Failed to delete transaction" },
      { status: error.response?.status || 500 }
    );
  }
}
