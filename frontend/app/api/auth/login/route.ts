import { NextResponse } from "next/server";
import api from "@/lib/api";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const response = await api.post("/api/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    const res = NextResponse.json(response.data);

    // Forward the set-cookie header from the backend (refresh_token)
    const setCookie = response.headers["set-cookie"];
    if (setCookie) {
      setCookie.forEach((cookie) => {
        res.headers.append("set-cookie", cookie);
      });
    }

    return res;
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.error || "Login failed" },
      { status: error.response?.status || 500 }
    );
  }
}
