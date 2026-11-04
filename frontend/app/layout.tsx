import type { Metadata } from "next";
import "./globals.css";
import { PROJECT } from "./lib/project";

export const metadata: Metadata = {
  metadataBase: new URL("https://bakai.manas.edu.kg"),
  title: `${PROJECT.name} | ${PROJECT.institution} Kurumsal Bilgi Asistanı`,
  description: `${PROJECT.institution} resmî belgelerine dayalı, kaynak gösteren kurumsal bilgi asistanı`,
  authors: [{ name: PROJECT.author }],
  openGraph: {
    type: "website",
    locale: "tr_TR",
    url: "/",
    siteName: PROJECT.name,
    title: `${PROJECT.name} | ${PROJECT.institution}`,
    description: "Resmî üniversite belgelerine dayalı, kaynak gösteren kurumsal bilgi asistanı.",
    images: [{ url: "/bak-ai-social.png", width: 1200, height: 630, alt: PROJECT.name }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${PROJECT.name} | ${PROJECT.institution}`,
    description: "Resmî üniversite belgelerine dayalı, kaynak gösteren kurumsal bilgi asistanı.",
    images: ["/bak-ai-social.png"],
  },
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
