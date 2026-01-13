// app/(auth)/layout.tsx
import GuestGuard from "@/components/auth/GuestGuard";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <GuestGuard>
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md p-4">
          {/* Optional: Add a shared logo or branding here */}
          <div className="flex justify-center mb-8">
             <h1 className="text-2xl font-bold tracking-tight">Your App Name</h1>
          </div>
          {children}
        </div>
      </div>
    </GuestGuard>
  );
}
