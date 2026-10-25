import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SpineLab | X-ray Classification Research",
  description: "Explore an experimental, non-diagnostic CNN for spinal radiograph classification.",
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
