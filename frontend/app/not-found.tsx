import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <h2 className="text-2xl font-bold text-foreground">404 - Page Not Found</h2>
      <p className="mt-2 text-sm text-muted-foreground">The requested page could not be found.</p>
      <Link href="/" className="mt-4 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-primary-foreground">
        Return Home
      </Link>
    </div>
  );
}
