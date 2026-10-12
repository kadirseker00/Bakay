import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "BAKAY | Yönetim ve izleme",
  robots: { index: false, follow: false },
};

export default function MonitorLayout({ children }: { children: React.ReactNode }) {
  return children;
}
