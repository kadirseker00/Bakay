"""KTMÜ web/belge toplayıcı ve site haritalayıcı (İP1 — veri toplama).

Belirtilen alan adı içinde nazik (polite) bir BFS taraması yapar; HTML sayfalarını
ve belge (PDF/DOC/DOCX) bağlantılarını indirip data/raw/web/ altına kaydeder,
gezilen siteyi data/sitemap.json'a haritalar. Sonraki adımda `app.ingest.run`
bu dosyaları temizleyip parçalayarak indeksler.

Nazik tarama ilkeleri:
  - robots.txt kurallarına uyar
  - istekler arasında bekleme (rate limit) uygular
  - yalnızca verilen alan adı (ve alt alan adları) içinde gezer
  - aynı sayfayı/belgeyi iki kez indirmez (URL + içerik özeti tekilleştirme)

Kullanım:
    # Türkçe siteyi haritala, Türkçe belgeleri indir:
    python -m app.ingest.crawl --seed https://manas.edu.kg/tr --contains /tr --lang tr

    python -m app.ingest.crawl --seed https://www.manas.edu.kg --max-pages 100
    python -m app.ingest.crawl --seed https://manas.edu.kg/tr --delay 1.5

Not: Bazı sayfalar JavaScript ile içerik yüklüyorsa (dinamik), bu basit tarayıcı
o içeriği göremez. O durumda Playwright tabanlı tarayıcıya geçilecek (formdaki
İP1 planı). Çoğu resmi belge/PDF için bu yöntem yeterlidir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from app.config import ROOT

WEB_DIR = ROOT / "data" / "raw" / "web"
MAP_PATH = ROOT / "data" / "sitemap.json"
USER_AGENT = "BAKAI-Research-Bot/0.1 (KTMÜ BAP; akademik veri toplama)"
HEADERS = {"User-Agent": USER_AGENT}

HTML_TYPES = ("text/html",)
DOC_EXTS = (".pdf", ".doc", ".docx")
DOC_TYPES = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

# Türkçe olmayan belgeleri elemek için: Kiril harfler ya da KG/RU dil imleri
_CYRILLIC = re.compile(r"[Ѐ-ӿ]")
_NON_TR_TOKEN = re.compile(r"(?i)(^|[\W_])(kg|kgz|kirg|kyrgyz|rus?|eng?)([\W_]|$)")


def _safe_name(url: str, suffix: str) -> str:
    """URL'den çakışmayan, okunabilir bir dosya adı üretir."""
    parsed = urlparse(url)
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", (parsed.path or "index")).strip("_")
    slug = slug[:80] or "index"
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{slug}_{digest}{suffix}"


def _same_site(url: str, root_netloc: str) -> bool:
    netloc = urlparse(url).netloc
    root = root_netloc.removeprefix("www.")
    return netloc == root_netloc or netloc == root or netloc.endswith("." + root)


def _normalize_url(url: str) -> str:
    """Aynı sayfanın farklı yazımlarını (sonda /, #parça) tekilleştirir."""
    url = url.split("#")[0]
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


def _doc_suffix(url: str) -> str | None:
    path = url.lower().split("?")[0]
    for ext in DOC_EXTS:
        if path.endswith(ext):
            return ext
    return None


def _looks_turkish_doc(url: str) -> bool:
    """Belge URL'sinin (yol+ad) Türkçe olmadığına dair güçlü işaret var mı?"""
    path = unquote(urlparse(url).path)
    if _CYRILLIC.search(path):
        return False
    name = path.rsplit("/", 1)[-1]
    return not _NON_TR_TOKEN.search(name)


class Crawler:
    def __init__(
        self,
        seed: str,
        max_pages: int,
        max_docs: int,
        delay: float,
        contains: str = "",
        exclude: tuple[str, ...] = (),
        lang: str = "",
        map_out: Path | None = None,
    ):
        self.map_path = map_out or MAP_PATH
        self.seed = _normalize_url(seed)
        self.root_netloc = urlparse(self.seed).netloc
        self.max_pages = max_pages
        self.max_docs = max_docs
        self.delay = delay
        # Yalnızca bu metni içeren URL'leri takip et (ör. "/tr" -> Türkçe odak).
        # Belge bağlantıları bu filtreden muaftır (asıl belgeler).
        self.contains = contains
        # Bu metinlerden birini içeren URL'leri atla (ör. "burs" -> PII isim listeleri).
        self.exclude = tuple(e.lower() for e in exclude if e)
        # "tr": Kiril harfli ya da KG/RU/EN imli belgeleri indirme
        self.lang = lang
        self.seen: set[str] = set()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.robots = self._load_robots()
        WEB_DIR.mkdir(parents=True, exist_ok=True)
        # İçerik özeti tekilleştirme: aynı belge farklı URL'lerden gelirse atla
        self.content_hashes = {
            hashlib.md5(p.read_bytes()).hexdigest()
            for p in WEB_DIR.iterdir()
            if p.is_file()
        }
        self.map_pages: list[dict] = []
        self.map_docs: list[dict] = []

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

    def _save(self, content: bytes, url: str, suffix: str) -> Path | None:
        digest = hashlib.md5(content).hexdigest()
        if digest in self.content_hashes:
            return None  # aynı içerik zaten diskte
        self.content_hashes.add(digest)
        path = WEB_DIR / _safe_name(url, suffix)
        path.write_bytes(content)
        return path

    def _write_map(self) -> None:
        self.map_path.write_text(
            json.dumps(
                {
                    "seed": self.seed,
                    "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pages": self.map_pages,
                    "docs": self.map_docs,
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )

    def run(self) -> None:
        queue: deque[str] = deque([self.seed])
        pages = docs = 0

        while queue and pages < self.max_pages and docs < self.max_docs:
            url = queue.popleft()
            if url in self.seen:
                continue
            self.seen.add(url)

            if not self._allowed(url):
                print(f"⏭  robots engelledi: {url}")
                continue

            suffix = _doc_suffix(url)
            if suffix and self.lang == "tr" and not _looks_turkish_doc(url):
                continue
            if suffix and (WEB_DIR / _safe_name(url, suffix)).exists():
                continue  # bu URL daha önce indirilmiş

            try:
                resp = self.session.get(url, timeout=30)
            except requests.RequestException as e:
                print(f"⚠  hata ({url}): {e}")
                continue

            time.sleep(self.delay)  # nazik bekleme
            if resp.status_code != 200:
                continue

            ctype = resp.headers.get("content-type", "").split(";")[0].strip()

            if suffix or ctype in DOC_TYPES:
                path = self._save(resp.content, url, suffix or ".pdf")
                if path is None:
                    continue
                docs += 1
                self.map_docs.append({"url": url, "file": path.name, "kb": len(resp.content) // 1024})
                print(f"✓ DOC  [{docs}] {path.name}")
                continue

            if ctype in HTML_TYPES:
                path = self._save(resp.content, url, ".html")
                pages += 1
                self.map_pages.append({"url": url, "file": path.name if path else None})
                if pages % 50 == 0:
                    self._write_map()  # ara kayıt (kesinti güvenliği)
                    print(f"…  {pages} sayfa, {docs} belge, kuyruk: {len(queue)}")
                for link in self._extract_links(resp.text, url):
                    if link not in self.seen:
                        queue.append(link)

        self._write_map()
        print(f"\nBitti. {pages} sayfa + {docs} belge indirildi → {WEB_DIR}")
        print(f"Site haritası: {self.map_path}")

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            absolute = _normalize_url(urljoin(base_url, a["href"]))
            if not absolute.startswith(("http://", "https://")):
                continue
            if not _same_site(absolute, self.root_netloc):
                continue
            # exclude filtresi: istenmeyen (ör. PII isim listesi) URL'leri tamamen atla
            if any(x in absolute.lower() for x in self.exclude):
                continue
            # contains filtresi: belgeler muaf, sayfalar filtreden geçmeli
            if self.contains and not _doc_suffix(absolute) and self.contains not in absolute:
                continue
            links.append(absolute)
        return links


def main() -> None:
    parser = argparse.ArgumentParser(description="KTMÜ belge toplayıcı + haritalayıcı (İP1)")
    parser.add_argument(
        "--seed",
        default="https://manas.edu.kg/tr",
        help="Tarama başlangıç adresi (varsayılan: KTMÜ Türkçe site)",
    )
    parser.add_argument("--max-pages", type=int, default=10000, help="Maks. gezilecek sayfa")
    parser.add_argument("--max-docs", type=int, default=3000, help="Maks. indirilecek belge")
    parser.add_argument(
        "--delay", type=float, default=0.5, help="İstekler arası bekleme (sn)"
    )
    parser.add_argument(
        "--contains",
        default="",
        help="Yalnızca bu metni içeren URL'leri takip et (ör. /tr). Belgeler muaf.",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Bu metinleri içeren URL'leri atla (ör. --exclude burs liste). PII koruması.",
    )
    parser.add_argument(
        "--lang",
        default="",
        help='"tr": Kiril harfli ya da KG/RU/EN imli belgeleri indirme',
    )
    parser.add_argument(
        "--map-out",
        default="",
        help="Site haritası çıktı yolu (varsayılan: data/sitemap.json)",
    )
    args = parser.parse_args()

    print(f"Tarama başlıyor: {args.seed}  (maks {args.max_pages} sayfa, {args.max_docs} belge)")
    Crawler(
        args.seed,
        args.max_pages,
        args.max_docs,
        args.delay,
        args.contains,
        tuple(args.exclude),
        args.lang,
        Path(args.map_out) if args.map_out else None,
    ).run()


if __name__ == "__main__":
    main()
