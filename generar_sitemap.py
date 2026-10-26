#!/usr/bin/env python3
"""
generar_sitemap.py — VectorGarage
---------------------------------------------------------------
Lee las páginas YA generadas (diseno/*/index.html y modelo/*/index.html)
y crea:

  1. sitemap.xml  -> solo URLs que realmente son indexables
                     (salta las que tienen <meta name="robots" content="noindex">,
                      para que Search Console no marque "enviada pero noindex").
                     Incluye <image:image> con la miniatura de cada página.
  2. robots.txt   -> permite todo y apunta al sitemap.
  3. Bloque de enlaces a las páginas /modelo/ dentro de index.html
     (entre <!-- MODELOS:START --> y <!-- MODELOS:END -->), para que Google
     pueda descubrir las páginas rastreando enlaces normales y no solo
     por el sitemap.

USO (parado en la carpeta raíz del sitio, donde está index.html):

    python generar_sitemap.py
    python generar_sitemap.py --dominio https://vectorgarage.vercel.app
    python generar_sitemap.py --lastmod 2026-10-26

Corre este script DESPUÉS de generar_seo.py cada vez que agregues diseños,
y luego sube sitemap.xml, robots.txt e index.html al repo.
---------------------------------------------------------------
"""

import argparse
import html
import re
import sys
from datetime import date, datetime
from pathlib import Path

DOMINIO_POR_DEFECTO = "https://vectorgarage.vercel.app"
MAX_URLS_POR_SITEMAP = 50000  # límite oficial de Google

RE_ROBOTS = re.compile(r'<meta\s+name="robots"\s+content="([^"]*)"', re.I)
RE_CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"', re.I)
RE_OGIMG = re.compile(r'<meta\s+property="og:image"\s+content="([^"]*)"', re.I)
RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
RE_TITLE = re.compile(r"<title>(.*?)</title>", re.I | re.S)


def leer_pagina(ruta: Path):
    txt = ruta.read_text(encoding="utf-8", errors="replace")
    rob = RE_ROBOTS.search(txt)
    can = RE_CANON.search(txt)
    img = RE_OGIMG.search(txt)
    return txt, (rob.group(1).lower() if rob else ""), (can.group(1) if can else None), (img.group(1) if img else None)


def fecha_archivo(ruta: Path, forzada: str | None) -> str:
    if forzada:
        return forzada
    return datetime.fromtimestamp(ruta.stat().st_mtime).date().isoformat()


def recolectar(raiz: Path, dominio: str, lastmod_forzado: str | None):
    """Devuelve (urls, saltadas, modelos)."""
    urls, saltadas, modelos = [], [], []

    # Home
    home = raiz / "index.html"
    urls.append({"loc": dominio + "/", "lastmod": fecha_archivo(home, lastmod_forzado), "img": None})

    for seccion in ("modelo", "diseno"):
        base = raiz / seccion
        if not base.is_dir():
            continue
        for carpeta in sorted(base.iterdir()):
            pagina = carpeta / "index.html"
            if not pagina.is_file():
                continue
            txt, robots, canon, img = leer_pagina(pagina)
            if "noindex" in robots:
                saltadas.append(f"{seccion}/{carpeta.name} (noindex)")
                continue
            esperada = f"{dominio}/{seccion}/{carpeta.name}/"
            loc = canon or esperada
            if canon and canon != esperada:
                print(f"AVISO: canonical distinto en {pagina}: {canon}", file=sys.stderr)
            # solo incluir imagen si el archivo existe de verdad
            img_ok = None
            if img and img.startswith(dominio + "/"):
                if (raiz / img[len(dominio) + 1:]).is_file():
                    img_ok = img
            urls.append({"loc": loc, "lastmod": fecha_archivo(pagina, lastmod_forzado), "img": img_ok})

            if seccion == "modelo":
                h1 = RE_H1.search(txt)
                tit = RE_TITLE.search(txt)
                nombre = re.sub(r"^Diseños para\s+", "", re.sub(r"<[^>]+>", "", h1.group(1)).strip()) if h1 else carpeta.name
                m = re.search(r"\((\d+)\)", tit.group(1)) if tit else None
                modelos.append((carpeta.name, nombre, int(m.group(1)) if m else 0))
    return urls, saltadas, modelos


def escribir_sitemaps(raiz: Path, dominio: str, urls: list):
    def bloque(u):
        s = f"  <url>\n    <loc>{html.escape(u['loc'])}</loc>\n    <lastmod>{u['lastmod']}</lastmod>\n"
        if u["img"]:
            s += f"    <image:image>\n      <image:loc>{html.escape(u['img'])}</image:loc>\n    </image:image>\n"
        return s + "  </url>\n"

    cabecera = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    )
    partes = [urls[i:i + MAX_URLS_POR_SITEMAP] for i in range(0, len(urls), MAX_URLS_POR_SITEMAP)]
    archivos = []
    for n, parte in enumerate(partes, 1):
        nombre = "sitemap.xml" if len(partes) == 1 else f"sitemap-{n}.xml"
        (raiz / nombre).write_text(cabecera + "".join(bloque(u) for u in parte) + "</urlset>\n", encoding="utf-8")
        archivos.append(nombre)

    if len(partes) > 1:  # índice de sitemaps (solo si se supera el límite)
        hoy = date.today().isoformat()
        idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        idx += "".join(f"  <sitemap>\n    <loc>{dominio}/{a}</loc>\n    <lastmod>{hoy}</lastmod>\n  </sitemap>\n" for a in archivos)
        (raiz / "sitemap.xml").write_text(idx + "</sitemapindex>\n", encoding="utf-8")
        archivos.insert(0, "sitemap.xml")
    return archivos


def escribir_robots(raiz: Path, dominio: str):
    (raiz / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {dominio}/sitemap.xml\n",
        encoding="utf-8",
    )


def actualizar_home(raiz: Path, modelos: list, dominio: str):
    """Añade canonical a la home e inserta/actualiza el bloque de enlaces a /modelo/."""
    home = raiz / "index.html"
    txt = home.read_text(encoding="utf-8")

    if not RE_CANON.search(txt) and "</title>" in txt:
        txt = txt.replace(
            "</title>",
            "</title>\n"
            f'<link rel="canonical" href="{dominio}/">\n'
            '<meta name="robots" content="index,follow">\n'
            '<meta property="og:site_name" content="VectorGarage">\n'
            '<meta property="og:locale" content="es_EC">\n'
            '<meta property="og:type" content="website">\n'
            f'<meta property="og:url" content="{dominio}/">\n'
            f'<meta property="og:image" content="{dominio}/assets/logo.png">',
            1,
        )
    enlaces = "\n".join(
        f'      <a href="/modelo/{slug}/">{html.escape(nombre)} ({n})</a>'
        for slug, nombre, n in sorted(modelos, key=lambda m: m[1].lower())
    )
    bloque = (
        "<!-- MODELOS:START (generado por generar_sitemap.py) -->\n"
        '  <nav class="modelos-nav" aria-label="Diseños por modelo" '
        'style="max-width:1100px;margin:0 auto;padding:24px;font-size:14px;line-height:2;">\n'
        '    <h2 style="font-size:16px;margin:0 0 8px;">Diseños por modelo de moto</h2>\n'
        '    <div style="display:flex;flex-wrap:wrap;gap:4px 16px;color:var(--texto-tenue);">\n'
        f"{enlaces}\n"
        "    </div>\n  </nav>\n"
        "  <!-- MODELOS:END -->"
    )
    patron = re.compile(r"<!-- MODELOS:START.*?<!-- MODELOS:END -->", re.S)
    if patron.search(txt):
        txt = patron.sub(lambda m: bloque, txt)
    elif "<footer" in txt:
        txt = txt.replace("<footer", bloque + "\n\n  <footer", 1)
    else:
        print("AVISO: index.html no tiene <footer>; no se insertó el bloque de modelos.", file=sys.stderr)
        return
    home.write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Genera sitemap.xml y robots.txt para VectorGarage")
    ap.add_argument("--dominio", default=DOMINIO_POR_DEFECTO, help="URL base sin barra final")
    ap.add_argument("--lastmod", default=None, help="Fecha fija AAAA-MM-DD (por defecto: fecha de cada archivo)")
    ap.add_argument("--sin-home", action="store_true", help="No tocar index.html")
    args = ap.parse_args()

    raiz = Path(".").resolve()
    if not (raiz / "index.html").is_file():
        sys.exit("Ejecuta este script dentro de la carpeta raíz del sitio (donde está index.html).")
    dominio = args.dominio.rstrip("/")

    urls, saltadas, modelos = recolectar(raiz, dominio, args.lastmod)
    archivos = escribir_sitemaps(raiz, dominio, urls)
    escribir_robots(raiz, dominio)
    if not args.sin_home:
        actualizar_home(raiz, modelos, dominio)

    print(f"OK: {len(urls)} URLs en {', '.join(archivos)}")
    print(f"    {len(modelos)} páginas de modelo enlazadas desde la home")
    print(f"    {len(saltadas)} páginas noindex NO incluidas en el sitemap")
    print(f"    robots.txt -> Sitemap: {dominio}/sitemap.xml")


if __name__ == "__main__":
    main()
