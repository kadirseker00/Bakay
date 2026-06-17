"""KTMÜ web/PDF belge toplayıcı (İP1 — veri toplama).

Belirtilen alan adı içinde nazik (polite) bir BFS taraması yapar; HTML sayfalarını
ve PDF bağlantılarını indirip data/raw/web/ altına kaydeder. Sonraki adımda
`app.ingest.run` bu dosyaları temizleyip parçalayarak indeksler.

Nazik tarama ilkeleri:
  - robots.txt kurallarına uyar
  - istekler arasında bekleme (rate limit) uygular
  - yalnızca verilen alan adı (ve alt yollar) içinde gezer
  - aynı sayfayı iki kez indirmez

Kullanım:
    python -m app.ingest.crawl --seed https://www.manas.edu.kg --max-pages 100
    python -m app.ingest.crawl --seed https://www.manas.edu.kg/yonetmelikler --delay 1.5

Not: Bazı sayfalar JavaScript ile içerik yüklüyorsa (dinamik), bu basit tarayıcı
o içeriği göremez. O durumda Playwright tabanlı tarayıcıya geçilecek (formdaki
İP1 planı). Çoğu resmi belge/PDF için bu yöntem yeterlidir.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from app.config import ROOT

WEB_DIR = ROOT / "data" / "raw" / "web"
USER_AGENT = "BAKAY-Research-Bot/0.1 (KTMÜ BAP; akademik veri toplama)"
HEADERS = {"User-Agent": USER_AGENT}

# İndirilecek içerik türleri
HTML_TYPES = ("text/html",)
PDF_TYPES = ("application/pdf",)


def _safe_name(url: str, suffix: str) -> str:
    """URL'den çakışmayan, okunabilir bir dosya adı üretir."""
    parsed = urlparse(url)
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", (parsed.path or "index")).strip("_")
    slug = slug[:80] or "index"
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{slug}_{digest}{suffix}"


def _same_site(url: str, root_netloc: str) -> bool:
    netloc = urlparse(url).netloc
    return netloc == root_netloc or netloc.endswith("." + root_netloc)


def _normalize_url(url: str) -> str:
    """Aynı sayfanın farklı yazımlarını (sonda /, #parça) tekilleştirir."""
    url = url.split("#")[0]
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


class Crawler:
    def __init__(self, seed: str, max_pages: int, delay: float):
        self.seed = _normalize_url(seed)
        self.root_netloc = urlparse(self.seed).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.seen: set[str] = set()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.robots = self._load_robots()
        WEB_DIR.mkdir(parents=True, exist_ok=True)

    def _load_robots(self) -> RobotFileParser:
        rp = RobotFileParser()
        robots_url = urljoin(self.seed, "/robots.txt")
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception:
            pass  # robots erişilemezse temkinli devam (nazik gecikme zaten var)
        return rp

    def _allowed(self, url: str) -> bool:
        try:
            return self.robots.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    def _save(self, content: bytes, url: str, suffix: str) -> Path:
        path = WEB_DIR / _safe_name(url, suffix)
        path.write_bytes(content)
        return path

    def run(self) -> None:
        queue: deque[str] = deque([self.seed])
        downloaded = 0

        while queue and downloaded < self.max_pages:
            url = queue.popleft()
            if url in self.seen:
                continue
            self.seen.add(url)

            if not self._allowed(url):
                print(f"⏭  robots engelledi: {url}")
                continue

            try:
                resp = self.session.get(url, timeout=20)
            except requests.RequestException as e:
                print(f"⚠  hata ({url}): {e}")
                continue

            time.sleep(self.delay)  # nazik bekleme
            if resp.status_code != 200:
                continue

            ctype = resp.headers.get("content-type", "").split(";")[0].strip()

            if ctype in PDF_TYPES or url.lower().endswith(".pdf"):
                path = self._save(resp.content, url, ".pdf")
                downloaded += 1
                print(f"✓ PDF  [{downloaded}] {path.name}")
                continue

            if ctype in HTML_TYPES:
                path = self._save(resp.content, url, ".html")
                downloaded += 1
                print(f"✓ HTML [{downloaded}] {path.name}  ({url})")
                # Sayfadaki bağlantıları kuyruğa ekle
                for link in self._extract_links(resp.text, url):
                    if link not in self.seen:
                        queue.append(link)

        print(f"\nBitti. {downloaded} belge indirildi → {WEB_DIR}")

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            absolute = _normalize_url(urljoin(base_url, a["href"]))
            if absolute.startswith(("http://", "https://")) and _same_site(
                absolute, self.root_netloc
            ):
                links.append(absolute)
        return links


def main() -> None:
    parser = argparse.ArgumentParser(description="KTMÜ belge toplayıcı (İP1)")
    parser.add_argument(
        "--seed",
        default="https://www.manas.edu.kg",
        help="Tarama başlangıç adresi (varsayılan: KTMÜ ana sayfa)",
    )
    parser.add_argument("--max-pages", type=int, default=50, help="Maks. indirme sayısı")
    parser.add_argument(
        "--delay", type=float, default=1.0, help="İstekler arası bekleme (sn)"
    )
    args = parser.parse_args()

    print(f"Tarama başlıyor: {args.seed}  (maks {args.max_pages} belge)")
    Crawler(args.seed, args.max_pages, args.delay).run()


if __name__ == "__main__":
    main()
