#!/usr/bin/env python3
"""Optional image processor (run locally when source files are added).
Requires Pillow (`pip install pillow`) — NOT a dependency of the core build.
Reads assets/source/*.jpg named per data/gallery.json expected_path, strips EXIF,
generates thumb/medium/large WebP + JPEG fallback into assets/img/, and writes the
resolved `src`/`srcset`/dimensions back into data/gallery.json. Rebuild afterwards.
"""
import json, pathlib, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required: pip install pillow")
ROOT = pathlib.Path(__file__).resolve().parent.parent
gal = json.load(open(ROOT/"data/gallery.json", encoding="utf-8"))
outdir = ROOT/"assets/img"; outdir.mkdir(parents=True, exist_ok=True)
SIZES = {"thumb":400, "medium":800, "large":1600}
changed = 0
for im in gal["images"]:
    srcfile = ROOT/im.get("expected_path","")
    if not srcfile.exists():
        continue
    img = Image.open(srcfile)
    img = img.convert("RGB")  # drops EXIF/alpha
    w0, h0 = img.size
    base = im["id"]
    srcset = []
    for name, w in SIZES.items():
        if w > w0: w = w0
        h = round(h0 * w / w0)
        r = img.resize((w, h))
        r.save(outdir/f"{base}-{name}.webp", "WEBP", quality=82, method=6)
        r.save(outdir/f"{base}-{name}.jpg", "JPEG", quality=85, optimize=True)
        srcset.append(f"assets/img/{base}-{name}.webp {w}w")
    im["src"] = f"assets/img/{base}-medium.jpg"
    im["srcset"] = ", ".join(srcset)
    im["w"], im["h"] = SIZES["medium"], round(h0*SIZES["medium"]/w0)
    im["status"] = "published"
    changed += 1
json.dump(gal, open(ROOT/"data/gallery.json","w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"processed {changed} image(s); rebuild with scripts/build.py")
