"""
Script de SUBIDA de una carpeta completa (ej. assets/previews) al
CÓDIGO del repositorio de GitHub, manteniendo la misma estructura de
carpetas. A diferencia de subir_a_github.py (que sube ZIPs como
"Release assets"), este sube archivos normales del sitio (como tus
imágenes de previsualización) directo al repositorio, en la ruta
exacta que tú indiques.

REQUISITOS:
    pip install requests
    Ya debes tener "gh auth login" hecho (usamos su mismo token,
    no hace falta instalar Git por separado).

Cómo usarlo:
    python subir_carpeta_a_repo.py usuario/repo assets assets

    - "usuario/repo"  -> tu repo, ej: softwaremarketingdigital90-ux/WEB-ANUNCIOS-
    - "assets"        -> carpeta LOCAL que quieres subir (con subcarpetas adentro)
    - "assets"        -> carpeta DESTINO dentro del repo (mismo nombre normalmente)

Ejemplo real para tu caso (parado dentro de tu carpeta "tienda"):
    python subir_carpeta_a_repo.py softwaremarketingdigital90-ux/WEB-ANUNCIOS- assets assets

Qué hace:
1. Recorre la carpeta local que le indiques, con todas sus subcarpetas.
2. Por cada archivo, lo sube al repo en la misma ruta relativa
   (ej. assets/previews/xr-150.png -> queda en esa misma ruta en GitHub).
3. Si el archivo ya existe en el repo, lo actualiza; si no, lo crea.
4. Se puede volver a correr sin problema si se corta a la mitad — los
   archivos que no cambiaron se detectan y se saltan (comparando el
   contenido), así no pierdes tiempo re-subiendo todo de nuevo.
5. Pausa breve entre archivos para no saturar la API de GitHub.
"""

import sys
import time
import base64
import hashlib
import subprocess
from pathlib import Path

import requests

PAUSA_ENTRE_ARCHIVOS = 0.3  # segundos


def obtener_token():
    resultado = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if resultado.returncode != 0:
        print("No se pudo obtener el token de gh. Corre primero: gh auth login")
        sys.exit(1)
    return resultado.stdout.strip()


def sha_git_blob(contenido_bytes):
    """Calcula el mismo hash que usa Git internamente, para saber si
    un archivo ya está igual en el repo y así saltarlo."""
    encabezado = f"blob {len(contenido_bytes)}\0".encode()
    return hashlib.sha1(encabezado + contenido_bytes).hexdigest()


def subir_archivo(sesion, repo, ruta_repo, ruta_local):
    contenido_bytes = ruta_local.read_bytes()
    contenido_b64 = base64.b64encode(contenido_bytes).decode()

    url = f"https://api.github.com/repos/{repo}/contents/{ruta_repo}"

    # Revisamos si el archivo ya existe (para actualizar en vez de crear,
    # y para saltarlo si no cambió)
    resp_get = sesion.get(url)
    sha_existente = None
    if resp_get.status_code == 200:
        datos_existentes = resp_get.json()
        sha_existente = datos_existentes.get("sha")
        # Si el contenido es idéntico al que ya está subido, lo saltamos
        if sha_existente == sha_git_blob(contenido_bytes):
            return "sin_cambios"

    body = {
        "message": f"Subir {ruta_repo}",
        "content": contenido_b64,
    }
    if sha_existente:
        body["sha"] = sha_existente

    resp_put = sesion.put(url, json=body)

    if resp_put.status_code in (200, 201):
        return "subido"
    else:
        return f"error: {resp_put.status_code} {resp_put.text[:200]}"


def main():
    if len(sys.argv) < 4:
        print("Uso: python subir_carpeta_a_repo.py usuario/repo carpeta_local carpeta_destino_en_repo")
        sys.exit(1)

    repo = sys.argv[1]
    carpeta_local = Path(sys.argv[2])
    carpeta_destino = sys.argv[3].strip("/")

    if not carpeta_local.exists():
        print(f"No se encontró la carpeta local: {carpeta_local}")
        sys.exit(1)

    token = obtener_token()
    sesion = requests.Session()
    sesion.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })

    archivos = [p for p in carpeta_local.rglob("*") if p.is_file()]
    total = len(archivos)
    print(f"Encontrados {total} archivos en {carpeta_local}\n")

    subidos = 0
    sin_cambios = 0
    fallidos = []

    for i, archivo in enumerate(archivos, start=1):
        ruta_relativa = archivo.relative_to(carpeta_local).as_posix()
        ruta_repo = f"{carpeta_destino}/{ruta_relativa}"

        resultado = subir_archivo(sesion, repo, ruta_repo, archivo)

        if resultado == "subido":
            subidos += 1
        elif resultado == "sin_cambios":
            sin_cambios += 1
        else:
            fallidos.append((ruta_relativa, resultado))

        if i % 50 == 0 or i == total:
            print(f"  {i}/{total} procesados... "
                  f"({subidos} subidos, {sin_cambios} sin cambios, {len(fallidos)} fallidos)")

        time.sleep(PAUSA_ENTRE_ARCHIVOS)

    print("\n" + "=" * 50)
    print("PROCESO TERMINADO")
    print("=" * 50)
    print(f"Subidos:      {subidos}")
    print(f"Sin cambios:  {sin_cambios}")
    print(f"Fallidos:     {len(fallidos)}")

    if fallidos:
        print("\nAlgunos que fallaron (primeros 10):")
        for ruta, error in fallidos[:10]:
            print(f"  - {ruta}: {error}")
        print("\nPuedes volver a correr este mismo comando para reintentar")
        print("solo los que fallaron (los que ya subieron bien se saltan).")


if __name__ == "__main__":
    main()
