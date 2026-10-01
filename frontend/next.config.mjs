import { readFileSync } from "node:fs";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Doğrulama derlemesini çalışan geliştirme servisinden ayrı tut.
  distDir: process.env.BAKAY_BUILD_DIR || ".next",
  env: {
    NEXT_PUBLIC_APP_VERSION: readFileSync(new URL("../VERSION", import.meta.url), "utf8").trim(),
  },
  // Backend adresi NEXT_PUBLIC_API_URL ile değiştirilebilir (varsayılan: yerel FastAPI)
};

export default nextConfig;
