import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Inter } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-display-loaded",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-sans-loaded",
});

export const metadata: Metadata = {
  title: "Duelens — Cross-Document Financial Consistency Checker",
  description:
    "Duelens verifies financial consistency across pitch decks, MIS, projections and cap tables so investors can decide faster.",
  authors: [{ name: "Duelens" }],
  openGraph: {
    title: "Duelens — Financial Consistency Checker",
    description:
      "Upload fundraising documents and instantly verify financial consistency before investing.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    site: "@Duelens",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${plusJakarta.variable} ${inter.variable}`}>
      <body>{children}</body>
    </html>
  );
}
