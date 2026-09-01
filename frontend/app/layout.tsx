import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BAKAY | KTMÜ Kurumsal Bilgi Asistanı",
  description: "KTMÜ resmî belgelerine dayalı, kaynak gösteren kurumsal bilgi asistanı",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
