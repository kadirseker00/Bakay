import type { Metadata } from "next";
import "./globals.css";
import { PROJECT } from "./lib/project";

export const metadata: Metadata = {
  title: `${PROJECT.name} | ${PROJECT.institution} Kurumsal Bilgi Asistanı`,
  description: `${PROJECT.institution} resmî belgelerine dayalı, kaynak gösteren kurumsal bilgi asistanı`,
  authors: [{ name: PROJECT.author }],
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
