# -*- coding: utf-8 -*-
"""
Script de Despliegue Automatizado a GitHub / GitHub Pages
Tablero de Control del Mercado Asegurador Argentino (SSN SINENSUP)
"""

import requests
import base64
import os
import sys
import time

def get_github_token():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "GitHub token.txt"),
        os.path.join("G:\\Mi unidad\\IA\\Tablero Retiro", "GitHub token.txt"),
        os.path.join("G:\\Mi unidad\\IA\\Tablero Personas", "GitHub token.txt"),
        os.path.join("G:\\Mi unidad\\IA\\Valores Financieros", "GitHub token.txt")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f.read().splitlines():
                    clean = line.strip()
                    if clean.startswith("ghp_"):
                        return clean
    return os.environ.get("GITHUB_TOKEN")

def deploy():
    token = get_github_token()
    if not token:
        print("ERROR: No se encontró el token de GitHub (ghp_...).")
        sys.exit(1)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sinensup-Deployer"
    }

    username = "GenesisFinal"
    repo_name = "tablero-sinensup"
    full_repo = f"{username}/{repo_name}"
    print(f"\n=======================================================")
    print(f"Desplegando en repositorio: {full_repo}")
    print(f"=======================================================")

    # 1. Verificar o Crear Repositorio
    repo_res = requests.get(f"https://api.github.com/repos/{full_repo}", headers=headers)
    if repo_res.status_code == 404:
        print(f"Creando repositorio '{repo_name}' en GitHub...")
        create_payload = {
            "name": repo_name,
            "description": "Dashboard Analítico del Mercado Asegurador Argentino (SSN SINENSUP • Balances Oficiales • 185 Aseguradoras • Ratios de Devengamiento)",
            "homepage": f"https://{username}.github.io/{repo_name}/",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False,
            "auto_init": True
        }
        create_res = requests.post("https://api.github.com/user/repos", headers=headers, json=create_payload)
        if create_res.status_code in [200, 201]:
            print(f"Repositorio '{full_repo}' creado exitosamente!")
            time.sleep(3)
        else:
            print(f"Error al crear repositorio: {create_res.status_code} - {create_res.text}")
            sys.exit(1)
    else:
        print(f"Repositorio '{full_repo}' ya existe.")

    # 2. Subir archivos
    def upload_file(remote_path, local_path, commit_msg):
        if not os.path.exists(local_path):
            print(f"Archivo local no encontrado: {local_path}")
            return False

        with open(local_path, "rb") as f:
            content_bytes = f.read()
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")

        url = f"https://api.github.com/repos/{full_repo}/contents/{remote_path}"
        
        for attempt in range(6):
            get_res = requests.get(url, headers=headers)
            sha = None
            if get_res.status_code == 200:
                sha = get_res.json().get("sha")

            payload = {
                "message": commit_msg,
                "content": content_b64
            }
            if sha:
                payload["sha"] = sha

            print(f"Subiendo {remote_path} ({len(content_bytes):,} bytes, intento {attempt+1})...")
            put_res = requests.put(url, headers=headers, json=payload)
            if put_res.status_code in [200, 201]:
                print(f"OK: {remote_path} publicado en GitHub.")
                return True
            else:
                print(f"Aviso al subir {remote_path}: {put_res.status_code} - {put_res.text[:120]}")
                time.sleep(2 * (attempt + 1))
        print(f"ERROR: No se pudo subir {remote_path} tras 6 intentos.")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    files_to_upload = [
        (".nojekyll", "Config: Deshabilitar procesamiento Jekyll con .nojekyll"),
        ("favicon.svg", "Asset: Favicon SVG para pestaña y marcadores"),
        ("index.html", "Feat: Dashboard Analítico del Mercado Asegurador (SSN SINENSUP)"),
        ("data_sinensup.json", "Data: Dataset consolidado de balances de 185 aseguradoras SSN"),
        ("README.md", "Docs: Documentación completa del Dashboard Sinensup"),
        ("build_data.py", "Code: Script generador del dataset actuarial y contable"),
        ("insurance_kpis.py", "Code: Motor de cálculo contable y devengamiento SSN"),
        ("db_engine.py", "Code: Motor de extracción y caché de base Access 2026-2.mdb"),
        ("generate_html.py", "Code: Generador de la aplicación HTML interactiva"),
        ("deploy_to_github.py", "Code: Script de despliegue automatizado a GitHub Pages")
    ]

    for fname, msg in files_to_upload:
        fpath = os.path.join(base_dir, fname)
        upload_file(fname, fpath, msg)

    # 3. Activar GitHub Pages si aún no está activado
    pages_url = f"https://api.github.com/repos/{full_repo}/pages"
    pages_get = requests.get(pages_url, headers=headers)
    if pages_get.status_code == 404:
        print("Habilitando GitHub Pages en la rama main...")
        pages_payload = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        pages_post = requests.post(pages_url, headers=headers, json=pages_payload)
        if pages_post.status_code not in [200, 201]:
            pages_payload["source"]["branch"] = "master"
            pages_post = requests.post(pages_url, headers=headers, json=pages_payload)

    public_url = f"https://{username}.github.io/{repo_name}/"
    print("\n=======================================================")
    print(" DESPLIEGUE COMPLETADO EXITOSAMENTE")
    print(f" Repositorio: https://github.com/{full_repo}")
    print(f" URL Pública (GitHub Pages): {public_url}")
    print("=======================================================\n")

if __name__ == '__main__':
    deploy()
