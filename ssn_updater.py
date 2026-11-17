"""
SSN Sinensup - Actualizador Automático y Monitor de Balances
============================================================
Monitorea periódicamente el portal de la SSN (https://sinensup.ssn.gob.ar/Sinensup/),
descarga el archivo ZIP del nuevo período contable según el calendario regulatorio (40-45 días post-cierre),
descomprime el archivo .mdb de Access y ejecuta automáticamente el pipeline de cálculo y despliegue.

Uso:
  python ssn_updater.py                 # Ejecución inteligente según calendario
  python ssn_updater.py --check         # Solo consulta períodos disponibles en la web de la SSN
  python ssn_updater.py --force         # Fuerza la descarga y actualización del último período
  python ssn_updater.py --period 2026-2 # Descarga y procesa un período específico
"""

import os
import re
import sys
import glob
import time
import shutil
import zipfile
import argparse
import datetime
import subprocess
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTAL_URL = "https://sinensup.ssn.gob.ar/Sinensup/menu.faces?idSession=reportes"
FRAME_CENTRAL_URL = "https://sinensup.ssn.gob.ar/Sinensup/sinesup_frame_central.html"
MENU2_URL = "https://sinensup.ssn.gob.ar/Sinensup/menu2.faces"
PERIOD_MDB_RE = re.compile(r"^(\d{4})-(\d+)\.mdb$", re.IGNORECASE)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def parse_period_tuple(period_str):
    """Convierte 'YYYY-Q' en una tupla (year, quarter) ordenable cronológicamente."""
    if not period_str:
        return (0, 0)
    match = re.match(r"^\s*(\d{4})-(\d+)\s*$", str(period_str))
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))

def notify_system(title, message, is_error=False):
    """Muestra una notificación nativa en macOS (osascript) o Windows (Toast PowerShell)."""
    try:
        if sys.platform == "darwin":
            safe_title = str(title).replace("\\", "\\\\").replace('"', '\\"')
            safe_msg = str(message).replace("\\", "\\\\").replace('"', '\\"')
            apple_script = f'display notification "{safe_msg}" with title "{safe_title}"'
            subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
        elif sys.platform == "win32":
            ps_title = str(title).replace('"', '`"').replace("$", "`$")
            ps_msg = str(message).replace('"', '`"').replace("$", "`$")
            ps_script = f"""
            [reflection.assembly]::loadwithpartialname('System.Windows.Forms') | Out-Null
            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.BalloonTipTitle = "{ps_title}"
            $notify.BalloonTipText = "{ps_msg}"
            $notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::{"Error" if is_error else "Info"}
            $notify.Visible = $True
            $notify.ShowBalloonTip(10000)
            Start-Sleep -Seconds 1
            $notify.Dispose()
            """
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        else:
            print(f"[Notificación {'ERROR' if is_error else 'INFO'}] {title}: {message}")
    except Exception as e:
        print(f"[Aviso] No se pudo emitir notificación del sistema: {e}")

notify_windows = notify_system

def get_current_local_period():
    """Identifica cuál es el período más reciente cargado localmente."""
    mdb_files = glob.glob(os.path.join(BASE_DIR, "*.mdb"))
    periods = []
    for f in mdb_files:
        fname = os.path.basename(f)
        match = PERIOD_MDB_RE.match(fname)
        if match:
            periods.append(f"{match.group(1)}-{match.group(2)}")
    if not periods:
        return "2026-2"
    periods.sort(key=parse_period_tuple)
    return periods[-1]

def get_expected_next_period():
    """
    Calcula el siguiente período esperado y evalúa si estamos dentro de la ventana
    de sondeo (a partir de los 40 días posteriores al cierre del trimestre).

    Codificación oficial de archivos ZIP en SINENSUP (año y trimestre calendario):
      - Cierre 31-12 (Q2 del ejercicio): sondeo desde 10-Feb -> Período (YYYY-1)-4
      - Cierre 31-03 (Q3 del ejercicio): sondeo desde 10-May -> Período YYYY-1
      - Cierre 30-06 (Q4 anual):         sondeo desde 10-Ago -> Período YYYY-2
      - Cierre 30-09 (Q1 del ejercicio): sondeo desde 10-Nov -> Período YYYY-3
    """
    today = datetime.date.today()
    current_year = today.year

    # Fechas clave de sondeo (día 40 post-cierre)
    check_dates = [
        (datetime.date(current_year, 2, 10), f"{current_year - 1}-4", "Segundo Trimestre del Ejercicio (cierre 31-12)"),
        (datetime.date(current_year, 5, 10), f"{current_year}-1", "Tercer Trimestre del Ejercicio (cierre 31-03)"),
        (datetime.date(current_year, 8, 10), f"{current_year}-2", "Cierre de Ejercicio Anual (cierre 30-06)"),
        (datetime.date(current_year, 11, 10), f"{current_year}-3", "Primer Trimestre del Ejercicio (cierre 30-09)")
    ]

    # Determinar si hoy cae dentro de alguna ventana activa de sondeo
    for date_start, period_code, desc in check_dates:
        # Ventana activa de 50 días a partir de date_start
        date_end = date_start + datetime.timedelta(days=50)
        if date_start <= today <= date_end:
            days_since = (today - date_start).days + 40
            return {
                "in_window": True,
                "period": period_code,
                "description": desc,
                "days_since_close": days_since,
                "deadline_passed": days_since > 45
            }

    return {
        "in_window": False,
        "period": None,
        "description": "Fuera de ventana de presentación",
        "days_since_close": 0,
        "deadline_passed": False
    }

def connect_ssn_portal():
    """Inicia sesión en el portal SSN y navega hasta el formulario de descarga de balances."""
    s = requests.Session()
    s.headers.update(HEADERS)

    # 1. Menú principal
    s.get(PORTAL_URL, verify=False, timeout=20)
    s.get(FRAME_CENTRAL_URL, verify=False, timeout=20)
    r_menu2 = s.get(MENU2_URL, verify=False, timeout=20)

    soup = BeautifulSoup(r_menu2.text, 'html.parser')
    view_state_el = soup.find('input', {'name': 'javax.faces.ViewState'})
    if not view_state_el:
        raise Exception("No se pudo obtener el ViewState de la sesión en el menú de la SSN.")
    
    view_state = view_state_el['value']

    # 2. Navegar a 'Archivo Zip Balances'
    post_data = {
        'j_id6': 'j_id6',
        'j_id6_SUBMIT': '1',
        'javax.faces.ViewState': view_state,
        'jscook_action': 'j_id6_j_id19_menu:A]archivozipbalances'
    }
    r_zip_page = s.post(MENU2_URL, data=post_data, verify=False, timeout=20)
    soup2 = BeautifulSoup(r_zip_page.text, 'html.parser')

    form_dl = soup2.find('form', {'id': 'j_id33'}) or soup2.find_all('form')[-1]
    action = form_dl.get('action') or '/Sinensup/facelets/archivoZipBalances.faces'
    view_state_dl = soup2.find('input', {'name': 'javax.faces.ViewState'})['value']
    select_el = soup2.find('select')
    select_name = select_el.get('name') if select_el else 'j_id33:periodo'

    # Extraer lista de períodos disponibles
    available_periods = [opt.get('value') for opt in soup2.find_all('option') if opt.get('value')]

    return {
        "session": s,
        "action_url": f"https://sinensup.ssn.gob.ar{action}",
        "form_id": form_dl.get('id', 'j_id33'),
        "view_state": view_state_dl,
        "select_name": select_name,
        "available_periods": available_periods
    }

def download_and_extract_period(portal_info, target_period):
    """Descarga el archivo ZIP del período y extrae el archivo .mdb en el directorio base."""
    s = portal_info['session']
    action_url = portal_info['action_url']
    form_id = portal_info['form_id']
    view_state = portal_info['view_state']
    select_name = portal_info['select_name']

    print(f"[SSN Crawler] Iniciando descarga del período {target_period} desde la SSN...")
    dl_data = {
        form_id: form_id,
        f"{form_id}_SUBMIT": "1",
        'javax.faces.ViewState': view_state,
        select_name: target_period,
        f'{form_id}:j_id39': 'Descargar'
    }

    r_file = s.post(action_url, data=dl_data, verify=False, stream=True, timeout=60)
    if r_file.status_code != 200:
        raise Exception(f"Error HTTP {r_file.status_code} al solicitar el archivo ZIP.")

    zip_filename = os.path.join(BASE_DIR, f"{target_period}.zip")
    with open(zip_filename, 'wb') as f:
        for chunk in r_file.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)

    file_size = os.path.getsize(zip_filename)
    print(f"[SSN Crawler] Archivo ZIP descargado: {zip_filename} ({file_size:,} bytes)")

    if file_size < 1000:
        raise Exception("El archivo descargado es demasiado pequeño o no es un ZIP válido.")

    # Descomprimir .mdb y normalizar nombre a <target_period>.mdb
    target_mdb_path = os.path.join(BASE_DIR, f"{target_period}.mdb")
    extracted_mdb = None
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.lower().endswith('.mdb'):
                extracted_raw = zip_ref.extract(member, BASE_DIR)
                if os.path.abspath(extracted_raw) != os.path.abspath(target_mdb_path):
                    shutil.move(extracted_raw, target_mdb_path)
                    # Limpiar subcarpeta vacía si el zip contenía directorios
                    parent_dir = os.path.dirname(extracted_raw)
                    if os.path.abspath(parent_dir) != os.path.abspath(BASE_DIR):
                        try:
                            os.removedirs(parent_dir)
                        except OSError:
                            pass
                extracted_mdb = target_mdb_path
                print(f"[SSN Crawler] Archivo .mdb extraído: {extracted_mdb}")
                break

    if not extracted_mdb or not os.path.exists(extracted_mdb) or os.path.getsize(extracted_mdb) < 1000:
        raise Exception(f"No se pudo extraer un archivo .mdb válido desde {zip_filename}.")

    # Eliminar el archivo ZIP temporal tras verificar la extracción
    try:
        os.remove(zip_filename)
    except OSError as e:
        print(f"[Aviso] No se pudo eliminar el ZIP temporal {zip_filename}: {e}")

    # Eliminar caché Parquet previo para evitar lecturas obsoletas del mismo período
    cache_parquet = os.path.join(BASE_DIR, "balance_cache.parquet")
    if os.path.exists(cache_parquet):
        try:
            os.remove(cache_parquet)
        except OSError as e:
            print(f"[Aviso] No se pudo invalidar balance_cache.parquet: {e}")

    return extracted_mdb

def run_update_pipeline():
    """Ejecuta en secuencia build_data.py, generate_html.py y deploy_to_github.py."""
    print("\n=======================================================")
    print(" EJECUTANDO PIPELINE COMPLETO DE PROCESAMIENTO Y DESPLIEGUE")
    print("=======================================================\n")

    steps = [
        ("1. Procesamiento de balances y consolidación de grupos", "build_data.py"),
        ("2. Generación del tablero interactivo index.html", "generate_html.py"),
        ("3. Despliegue automático a GitHub Pages", "deploy_to_github.py")
    ]

    for desc, script_name in steps:
        script_path = os.path.join(BASE_DIR, script_name)
        print(f"\n>> {desc} ({script_name})...")
        res = subprocess.run([sys.executable, script_path], cwd=BASE_DIR, capture_output=False)
        if res.returncode != 0:
            raise Exception(f"El paso '{script_name}' falló con código de salida {res.returncode}.")

    print("\n=======================================================")
    print(" ACTUALIZACIÓN Y DESPLIEGUE FINALIZADOS CON ÉXITO")
    print("=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Monitor y Actualizador Automático de Balances SSN")
    parser.add_argument("--check", action="store_true", help="Solo consultar los períodos disponibles en el portal")
    parser.add_argument("--force", action="store_true", help="Forzar la descarga del último período disponible")
    parser.add_argument("--period", type=str, help="Descargar y procesar un período específico (ej: 2026-2)")
    args = parser.parse_args()

    local_current = get_current_local_period()
    cal_info = get_expected_next_period()

    print(f"=======================================================")
    print(f" SSN SINENSUP - ACTUALIZADOR AUTOMÁTICO DE BALANCES")
    print(f" Fecha actual: {datetime.date.today()}")
    print(f" Último período procesado localmente: {local_current}")
    print(f" Estado de calendario: {cal_info['description']}")
    print(f"=======================================================")

    try:
        portal_info = connect_ssn_portal()
        available = portal_info['available_periods']
        latest_on_web = available[0] if available else None
        print(f"[SSN Portal] Períodos disponibles en la web: {', '.join(available[:6])}...")

        if args.check:
            print(f"\n[Resultado Check] Último período publicado en SSN: {latest_on_web}")
            return

        target = args.period
        if not target and args.force:
            target = latest_on_web

        if not target:
            # Lógica inteligente según calendario y novedades
            if latest_on_web and parse_period_tuple(latest_on_web) > parse_period_tuple(local_current):
                print(f"[¡Novedad detectada!] La SSN publicó el período '{latest_on_web}' (Local: '{local_current}').")
                target = latest_on_web
            elif cal_info['in_window']:
                expected = cal_info['period']
                if expected in available and parse_period_tuple(expected) > parse_period_tuple(local_current):
                    print(f"[¡Período esperado disponible!] Se encontró '{expected}' en el portal.")
                    target = expected
                else:
                    print(f"[En espera] Estamos en ventana de sondeo ({cal_info['days_since_close']} días post-cierre), pero el período '{expected}' aún no fue subido por la SSN.")
                    return
            else:
                print("[Al día] El sistema ya cuenta con el último balance publicado y no hay nuevos períodos vencidos para sondeo.")
                return

        # Si tenemos un target para descargar
        print(f"\n>> Procesando período objetivo: {target}...")
        download_and_extract_period(portal_info, target)

        # Verificar y descargar el período comparativo interanual si falta localmente
        target_yr, target_qtr = parse_period_tuple(target)
        if target_yr > 0:
            comp_period = f"{target_yr - 1}-{target_qtr}"
            comp_mdb_path = os.path.join(BASE_DIR, f"{comp_period}.mdb")
            if not os.path.exists(comp_mdb_path) and comp_period in available:
                print(f"\n>> Descargando período comparativo interanual faltante: {comp_period}...")
                download_and_extract_period(portal_info, comp_period)
        
        # Ejecutar pipeline completo
        run_update_pipeline()

        # Notificar éxito
        msg = f"El balance SSN del período {target} fue descargado y publicado exitosamente en el tablero."
        notify_system("SINENSUP Actualizado con Éxito", msg, is_error=False)

    except Exception as e:
        err_msg = str(e)
        print(f"\n[ERROR] {err_msg}")
        
        # Si venció el plazo de presentación (>45 días) y falló la actualización automática
        if cal_info.get('deadline_passed', False) or args.force:
            alerta = f"Atención: Venció el plazo de presentación del balance SSN y la descarga automática tuvo un inconveniente. Por favor descarga el archivo ZIP manualmente desde https://sinensup.ssn.gob.ar/"
            print(f"\n[ALERTA AL USUARIO] {alerta}")
            notify_system("Alerta SINENSUP - Descarga Manual Requerida", alerta, is_error=True)

if __name__ == '__main__':
    main()
