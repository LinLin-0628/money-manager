import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function POST() {
  try {
    const config = await getProxyConfig();
    const response = await api.post("/api/auth/refresh", {}, config);

    const res = NextResponse.json(response.data);

    // Forward the set-cookie header from the backend (new refresh_token)
    const setCookie = response.headers["set-cookie"];
    if (setCookie) {
      setCookie.forEach((cookie) => {
        res.headers.append("set-cookie", cookie);
      });
    }

    return res;
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.error || "Refresh failed" },
      { status: error.response?.status || 500 }
    );
  }
}
