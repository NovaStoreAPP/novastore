#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera, a partir de apps.json, una página estática share/<slug>.html por cada app.

Cada página lleva las etiquetas Open Graph / Twitter Card necesarias para que,
al pegar su enlace en WhatsApp o Telegram, aparezca el banner de NovaStore
(banner.png) junto con:

    Título      -> nombre de la app   (va en og:title, es el titular del preview)
    Peso        -> primera línea de la descripción
    Descripción -> segunda línea
    Enlace      -> la propia URL de esta página (tu web), NO el enlace a
                   Play Store / GitHub, para que la gente entre primero a NovaStore.

>>> EDITA ESTA CONSTANTE con el dominio real donde subirás la carpeta <<<
"""
import json
import re
import unicodedata
from pathlib import Path

BASE_URL = "https://novastore-apps.netlify.app"   # <-- si compras un dominio propio, cámbialo aquí y vuelve a ejecutar el script

ROOT = Path(__file__).parent
APPS_JSON = ROOT / "apps.json"
SHARE_DIR = ROOT / "share"
SHARE_DIR.mkdir(exist_ok=True)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "app"


def esc(s):
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def format_peso(peso):
    p = str(peso or "").strip()
    if re.fullmatch(r"\d+([.,]\d+)?", p):
        return f"{p} MB"
    return p or "—"


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nombre} - NovaStore</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{page_url}">

<!-- Vista previa al compartir (WhatsApp, Telegram, etc.) -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="NovaStore">
<meta property="og:url" content="{page_url}">
<meta property="og:title" content="{nombre}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{banner_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{nombre}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image" content="{banner_url}">

<meta name="theme-color" content="#7b5cff">
<meta http-equiv="refresh" content="0; url={redirect_url}">
<script>location.replace("{redirect_url}");</script>
<style>
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
       background:#f6f8f7;color:#1a1c1e;text-align:center;padding:24px}}
  a{{color:#7b5cff;font-weight:600}}
</style>
</head>
<body>
  <p>Abriendo <strong>{nombre}</strong> en NovaStore…<br>
  Si no ocurre nada, <a href="{redirect_url}">toca aquí</a>.</p>
</body>
</html>
"""


def build():
    data = json.loads(APPS_JSON.read_text(encoding="utf-8"))
    apps = data["apps"] if isinstance(data, dict) else data

    for app in apps:
        nombre = app.get("nombre", "App")
        slug = app.get("slug") or slugify(nombre)
        peso = format_peso(app.get("peso"))
        descripcion = app.get("descripcion", "")

        page_url = f"{BASE_URL}/share/{slug}.html"
        banner_url = f"{BASE_URL}/share/banner.png"
        redirect_url = f"{BASE_URL}/index.html?app={slug}"

        # Formato pedido: Peso / Descripción / Enlace (el título ya ocupa el
        # hueco de og:title, así que no se repite dentro de la descripción).
        og_desc = f"Peso: {peso}\nDescripción: {descripcion}\nEnlace: {page_url}"

        html = PAGE_TEMPLATE.format(
            nombre=esc(nombre),
            meta_desc=esc(descripcion or f"Descarga {nombre} en NovaStore"),
            page_url=esc(page_url),
            og_desc=esc(og_desc),
            banner_url=esc(banner_url),
            redirect_url=esc(redirect_url),
        )
        out_path = SHARE_DIR / f"{slug}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"  ✔ share/{slug}.html")

    print(f"\nListo: {len(apps)} páginas generadas en {SHARE_DIR}")
    print(f"Recuerda: BASE_URL está puesto a '{BASE_URL}'.")
    print("Si aún no lo has cambiado por tu dominio real, edítalo al principio de este script y vuelve a ejecutarlo.")


if __name__ == "__main__":
    build()
