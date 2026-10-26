"""
Script para SUBIR / ACTUALIZAR los archivos de tu carpeta local al
repositorio de GitHub, manteniendo la misma estructura.

- Si el archivo ya existe en GitHub y CAMBIÓ  -> lo actualiza.
- Si el archivo ya existe y es IGUAL           -> lo salta.
- Si el archivo no existe en GitHub            -> lo crea.

REQUISITOS:
    pip install requests
    gh auth login   (una sola vez)

CÓMO USARLO (parado dentro de tu carpeta "tienda"):
    python subir_carpeta_a_repo.py

No necesitas escribir nada más: ya viene configurado con tu repo y con
las carpetas/archivos que quieres actualizar (ver CONFIGURACIÓN abajo).

Si quieres usar otro repo o carpeta, también funciona así:
    python subir_carpeta_a_repo.py usuario/repo carpeta_local carpeta_destino
"""

import sys
import time
import base64
import hashlib
import subprocess
from pathlib import Path

import requests

# ===================== CONFIGURACIÓN =====================
REPO = "softwaremarketingdigital90-ux/WEB-ANUNCIOS-"

# Qué subir/actualizar (carpetas y archivos de tu carpeta local).
# "assets" NO está aquí a propósito: ya está en GitHub y no lo tocamos.
# Si dejas la lista vacía [], sube TODO lo que haya en la carpeta.
ELEMENTOS = [
    "css",
    "data",
    "diseno",
    "js",
    "modelo",
    "generar_sitemap.py",
    "googlea1fb8db3a133bfd8.html",
    "index.html",
    "README.md",
    "robots.txt",
    "sitemap.xml",
    "subir_carpeta_a_repo.py",
]

# Carpetas que nunca se suben
IGNORAR = {".git", "__pycache__", ".vscode", "node_modules"}

PAUSA_ENTRE_ARCHIVOS = 0.3  # segundos
# =========================================================


def obtener_token():
    resultado = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if resultado.returncode != 0:
        print("No se pudo obtener el token de gh. Corre primero: gh auth login")
        sys.exit(1)
    return resultado.stdout.strip()


def sha_git_blob(contenido_bytes):
    """Mismo hash que usa Git, para saber si el archivo ya está igual."""
    encabezado = f"blob {len(contenido_bytes)}\0".encode()
    return hashlib.sha1(encabezado + contenido_bytes).hexdigest()


def subir_archivo(sesion, repo, ruta_repo, ruta_local):
    contenido_bytes = ruta_local.read_bytes()
    contenido_b64 = base64.b64encode(contenido_bytes).decode()

    url = f"https://api.github.com/repos/{repo}/contents/{ruta_repo}"

    resp_get = sesion.get(url)
    sha_existente = None
    if resp_get.status_code == 200:
        sha_existente = resp_get.json().get("sha")
        if sha_existente == sha_git_blob(contenido_bytes):
            return "sin_cambios"

    body = {
        "message": f"Actualizar {ruta_repo}" if sha_existente else f"Subir {ruta_repo}",
        "content": contenido_b64,
    }
    if sha_existente:
        body["sha"] = sha_existente

    resp_put = sesion.put(url, json=body)

    if resp_put.status_code in (200, 201):
        return "actualizado" if sha_existente else "nuevo"
    return f"error: {resp_put.status_code} {resp_put.text[:200]}"


def listar_archivos(carpeta_base, elementos):
    """Devuelve la lista de archivos a procesar."""
    if elementos:
        candidatos = []
        for nombre in elementos:
            ruta = carpeta_base / nombre
            if not ruta.exists():
                print(f"  (aviso) No existe en tu carpeta, se omite: {nombre}")
            elif ruta.is_file():
                candidatos.append(ruta)
            else:
                candidatos.extend(p for p in ruta.rglob("*") if p.is_file())
    else:
        candidatos = [p for p in carpeta_base.rglob("*") if p.is_file()]

    return [
        p for p in candidatos
        if not any(parte in IGNORAR for parte in p.relative_to(carpeta_base).parts)
    ]


def main():
    repo = REPO
    carpeta_local = Path(".")
    carpeta_destino = ""
    elementos = ELEMENTOS

    # Modo manual (opcional): python script.py usuario/repo carpeta_local carpeta_destino
    if len(sys.argv) >= 4:
        repo = sys.argv[1]
        carpeta_local = Path(sys.argv[2])
        carpeta_destino = sys.argv[3].strip("/")
        if carpeta_destino == ".":
            carpeta_destino = ""
        elementos = []

    if not carpeta_local.exists():
        print(f"No se encontró la carpeta local: {carpeta_local}")
        sys.exit(1)

    token = obtener_token()
    sesion = requests.Session()
    sesion.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })

    archivos = listar_archivos(carpeta_local, elementos)
    total = len(archivos)
    print(f"Repo: {repo}")
    print(f"Archivos a revisar: {total}\n")

    nuevos = 0
    actualizados = 0
    sin_cambios = 0
    fallidos = []

    for i, archivo in enumerate(archivos, start=1):
        ruta_relativa = archivo.relative_to(carpeta_local).as_posix()
        ruta_repo = f"{carpeta_destino}/{ruta_relativa}" if carpeta_destino else ruta_relativa

        resultado = subir_archivo(sesion, repo, ruta_repo, archivo)

        if resultado == "nuevo":
            nuevos += 1
            print(f"  [NUEVO]       {ruta_repo}")
        elif resultado == "actualizado":
            actualizados += 1
            print(f"  [ACTUALIZADO] {ruta_repo}")
        elif resultado == "sin_cambios":
            sin_cambios += 1
        else:
            fallidos.append((ruta_relativa, resultado))
            print(f"  [ERROR]       {ruta_repo}")

        if i % 50 == 0 or i == total:
            print(f"  ... {i}/{total} revisados")

        time.sleep(PAUSA_ENTRE_ARCHIVOS)

    print("\n" + "=" * 50)
    print("PROCESO TERMINADO")
    print("=" * 50)
    print(f"Nuevos:       {nuevos}")
    print(f"Actualizados: {actualizados}")
    print(f"Sin cambios:  {sin_cambios}")
    print(f"Fallidos:     {len(fallidos)}")

    if fallidos:
        print("\nLos que fallaron (primeros 10):")
        for ruta, error in fallidos[:10]:
            print(f"  - {ruta}: {error}")
        print("\nVuelve a correr el mismo comando para reintentar solo esos.")


if __name__ == "__main__":
    main()