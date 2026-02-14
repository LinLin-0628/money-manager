import { NextResponse } from "next/server";
import api, { getProxyConfig } from "@/lib/api";

export async function POST() {
  try {
    const config = await getProxyConfig();
    const response = await api.post("/api/auth/logout", {}, config);

    const res = NextResponse.json(response.data);

    // Forward the set-cookie header from the backend (clear refresh_token)
    const setCookie = response.headers["set-cookie"];
    if (setCookie) {
      setCookie.forEach((cookie) => {
        res.headers.append("set-cookie", cookie);
      });
    }

    return res;
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.error || "Logout failed" },
      { status: error.response?.status || 500 }
    );
  }
}
