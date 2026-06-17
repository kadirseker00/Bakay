"""Concept-C ham görselini uygulamaya hazır logo + favicon'a dönüştürür.

Adımlar: beyaz arka planı şeffaflaştır → içeriğe göre kırp → kare tuvale ortala →
istenen boyutlara yeniden boyutlandır.
"""
from pathlib import Path

from PIL import Image, ImageChops

SRC = Path(__file__).parent / "concept-C-bubble-tunduk.png"
PUBLIC = Path(__file__).parents[2] / "frontend" / "public"
APPDIR = Path(__file__).parents[2] / "frontend" / "app"
PUBLIC.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC).convert("RGB")

# 1) İçeriğe göre kırp — beyazdan farkı eşikle (soft glow hâlelerini yok say)
bg = Image.new("RGB", img.size, (255, 255, 255))
diff = ImageChops.difference(img, bg).convert("L")
mask = diff.point(lambda p: 255 if p > 35 else 0)
bbox = mask.getbbox()
if bbox:
    pad = 24
    l, t, r, b = bbox
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(img.width, r + pad), min(img.height, b + pad)
    img = img.crop((l, t, r, b))

# 2) Beyazı şeffaflaştır (line-art için eşik)
img = img.convert("RGBA")
px = img.getdata()
new = [
    (r, g, b, 0) if (r > 240 and g > 240 and b > 240) else (r, g, b, a)
    for (r, g, b, a) in px
]
img.putdata(new)

# 3) Kare tuvale ortala (şeffaf dolgu)
side = max(img.size)
square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
square.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)

# 4) Boyutlar
square.resize((512, 512), Image.LANCZOS).save(PUBLIC / "logo.png")
square.resize((256, 256), Image.LANCZOS).save(APPDIR / "icon.png")
print("Kaydedildi:")
print(" -", PUBLIC / "logo.png", "(512x512)")
print(" -", APPDIR / "icon.png", "(256x256, favicon)")
