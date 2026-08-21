import os
import pyodbc
import pandas as pd

MDB_PATH = r"g:\Mi unidad\IA\Sinensup\2026-2.mdb"
CACHE_PARQUET = r"g:\Mi unidad\IA\Sinensup\balance_cache.parquet"

def get_connection_string():
    drivers = [d for d in pyodbc.drivers() if 'Access' in d or 'ACE' in d]
    if 'Microsoft Access Driver (*.mdb, *.accdb)' in drivers:
        return f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={MDB_PATH};"
    elif 'Microsoft Access Driver (*.mdb)' in drivers:
        return f"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={MDB_PATH};"
    return None

def load_data_from_mdb():
    conn_str = get_connection_string()
    if conn_str:
        try:
            conn = pyodbc.connect(conn_str)
            query = "SELECT cod_cia, razon_social, periodo, cod_subramo, desc_subramo, importe, cod_cuenta, desc_cuenta, nivel, id_padre FROM Balance"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"pyodbc connection error: {e}")

    # Fallback to PowerShell / OLEDB export
    print("Falling back to ADODB / OleDb extraction...")
    import subprocess
    ps_script = f"""
    $connStr = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source={MDB_PATH};Persist Security Info=False;"
    $conn = New-Object System.Data.OleDb.OleDbConnection($connStr)
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT cod_cia, razon_social, periodo, cod_subramo, desc_subramo, importe, cod_cuenta, desc_cuenta, nivel, id_padre FROM Balance"
    $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($cmd)
    $dt = New-Object System.Data.DataTable
    $adapter.Fill($dt) | Out-Null
    $conn.Close()
    $csvPath = "$env:TEMP\\sinensup_export.csv"
    $dt | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    Write-Output $csvPath
    """
    tmp_ps = os.path.join(os.environ.get('TEMP', '.'), 'export_mdb.ps1')
    with open(tmp_ps, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', tmp_ps], check=True)
    csv_file = os.path.join(os.environ.get('TEMP', '.'), 'sinensup_export.csv')
    df = pd.read_csv(csv_file, encoding='utf-8')
    return df

def get_balance_data(force_reload=False):
    if not force_reload and os.path.exists(CACHE_PARQUET):
        try:
            return pd.read_parquet(CACHE_PARQUET)
        except Exception:
            pass

    df = load_data_from_mdb()
    # Clean and standardize strings
    df['cod_cia'] = df['cod_cia'].astype(str).str.strip().str.zfill(4)
    df['razon_social'] = df['razon_social'].astype(str).str.strip()
    df['cod_cuenta'] = df['cod_cuenta'].astype(str).str.strip()
    df['desc_cuenta'] = df['desc_cuenta'].astype(str).str.strip()
    df['cod_subramo'] = df['cod_subramo'].fillna('').astype(str).str.strip()
    df['desc_subramo'] = df['desc_subramo'].fillna('').astype(str).str.strip()
    df['importe'] = pd.to_numeric(df['importe'], errors='coerce').fillna(0.0)
    df['nivel'] = pd.to_numeric(df['nivel'], errors='coerce').fillna(0).astype(int)

    # Actuarial classification by company production structure & license
    cias = df[['cod_cia', 'razon_social']].drop_duplicates()
    seg_map = {}

    for _, row in cias.iterrows():
        c = row['cod_cia']
        name = row['razon_social']
        sub = df[df['cod_cia'] == c]
        
        # Production by subramo (cuentas 5.01)
        sub_ramos = sub[(sub['desc_subramo'] != '') & (sub['desc_subramo'].notna()) & (sub['cod_cuenta'].str.startswith('5.01'))]
        
        patrim = sub_ramos[sub_ramos['cod_subramo'].str.startswith('1.') & (~sub_ramos['cod_subramo'].str.startswith('1.050'))]['importe'].sum()
        art = sub_ramos[sub_ramos['cod_subramo'].str.startswith('1.050')]['importe'].sum()
        personas = sub_ramos[sub_ramos['cod_subramo'].str.startswith('2.01') | sub_ramos['cod_subramo'].str.startswith('2.02') | sub_ramos['cod_subramo'].str.startswith('2.03') | sub_ramos['cod_subramo'].str.startswith('2.05')]['importe'].sum()
        retiro = sub_ramos[sub_ramos['cod_subramo'].str.startswith('2.06') | sub_ramos['cod_subramo'].str.startswith('2.07')]['importe'].sum()
        
        tot_primas = patrim + art + personas + retiro
        rs_upper = name.upper()

        if 'RETIRO' in rs_upper or retiro > 0.5 * max(1, tot_primas):
            seg = 'Seguros de Retiro'
        elif 'RIESGOS DEL TRABAJO' in rs_upper or ' ART' in rs_upper or 'A.R.T.' in rs_upper or art > 0.5 * max(1, tot_primas):
            seg = 'Riesgos del Trabajo (ART)'
        elif personas > 0.5 * max(1, tot_primas) or any(w in rs_upper for w in ['PERSONAS', 'VIDA', 'LIFE', 'SALUD', 'SEPELIO', 'CARDIF', 'METLIFE', 'CNP', 'PRUDENTIAL', 'ZURICH INTERNATIONAL LIFE']):
            seg = 'Seguros de Personas'
        else:
            seg = 'Patrimoniales y Mixtas'

        seg_map[c] = seg

    df['tipo_entidad'] = df['cod_cia'].map(seg_map)

    # Save to Parquet cache for ultra-fast loading
    try:
        df.to_parquet(CACHE_PARQUET, index=False)
        print(f"Data cached to {CACHE_PARQUET} ({len(df)} rows)")
    except Exception as e:
        print(f"Parquet save error: {e}")

    return df

if __name__ == '__main__':
    print("Testing get_balance_data()...")
    df = get_balance_data(force_reload=True)
    print(f"Loaded {len(df)} records for {df['cod_cia'].nunique()} companies.")
    print("Segments:\n", df[['cod_cia', 'tipo_entidad']].drop_duplicates()['tipo_entidad'].value_counts())
