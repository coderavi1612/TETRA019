"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("App Error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <h2 className="text-2xl font-bold text-foreground">Something went wrong!</h2>
      <p className="mt-2 text-sm text-muted-foreground">{error.message || "An unexpected error occurred."}</p>
      <Button onClick={() => reset()} className="mt-4 rounded-xl text-xs font-bold">
        Try Again
      </Button>
    </div>
  );
}
