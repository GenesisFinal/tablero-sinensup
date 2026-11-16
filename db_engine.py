import io
import logging
import os
import re
import sys
import tempfile
import pandas as pd

try:
    import pyodbc
except ImportError:
    pyodbc = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PARQUET = os.path.join(BASE_DIR, "balance_cache.parquet")
PERIOD_MDB_RE = re.compile(r"^(\d{4})-(\d+)\.mdb$", re.IGNORECASE)
DEFAULT_BALANCE_COLUMNS = [
    "cod_cia",
    "razon_social",
    "periodo",
    "cod_subramo",
    "desc_subramo",
    "importe",
    "cod_cuenta",
    "desc_cuenta",
    "nivel",
    "id_padre",
]


def parse_period_tuple(period_str):
    """Converts 'YYYY-Q' string into a sortable (year, quarter) tuple."""
    if not period_str:
        return (0, 0)
    match = re.match(r"^\s*(\d{4})-(\d+)\s*$", str(period_str))
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def list_local_periods():
    """Returns local SSN period strings (YYYY-Q) sorted chronologically."""
    periods = []
    if not os.path.isdir(BASE_DIR):
        return periods
    for fname in os.listdir(BASE_DIR):
        match = PERIOD_MDB_RE.match(fname)
        if match:
            periods.append(f"{match.group(1)}-{match.group(2)}")
    periods.sort(key=parse_period_tuple)
    return periods


def get_latest_mdb_path(period=None):
    """Resolves the .mdb file path for a specific period or the latest local one."""
    if period:
        return os.path.join(BASE_DIR, f"{str(period).strip()}.mdb")
    periods = list_local_periods()
    target = periods[-1] if periods else "2026-2"
    return os.path.join(BASE_DIR, f"{target}.mdb")


MDB_PATH = get_latest_mdb_path()


def read_parquet_safe(path):
    """Reads a Parquet file sequentially via BytesIO (macOS CloudStorage safe)."""
    with open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    return pd.read_parquet(buf)


def write_parquet_safe(df, path):
    """Writes a Parquet file sequentially via BytesIO (macOS CloudStorage safe)."""
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    with open(path, "wb") as f:
        f.write(buf.getvalue())


def _ensure_access_parser_patched():
    """Patches access_parser Jet4 dynamic column ordering and memo edge cases."""
    import access_parser.access_parser as ap

    logging.getLogger("access_parser").setLevel(logging.CRITICAL)

    if not getattr(ap.AccessTable, "_jet4_varcol_patched", False):
        orig_parse_dyn = ap.AccessTable._parse_dynamic_length_data

        def _parse_dynamic_length_data_sorted(
            self, original_record, relative_record_metadata, relative_records_column_map, null_table
        ):
            if self.version > 3:
                relative_records_column_map = dict(
                    sorted(
                        relative_records_column_map.items(),
                        key=lambda kv: kv[1].variable_column_number,
                    )
                )
            return orig_parse_dyn(
                self, original_record, relative_record_metadata, relative_records_column_map, null_table
            )

        ap.AccessTable._parse_dynamic_length_data = _parse_dynamic_length_data_sorted
        ap.AccessTable._jet4_varcol_patched = True

    if not getattr(ap.AccessTable, "_memo_safe_patched", False):
        orig_parse_memo = ap.AccessTable._parse_memo

        def _parse_memo_safe(self, relative_obj_data, return_raw=False):
            try:
                return orig_parse_memo(self, relative_obj_data, return_raw=return_raw)
            except Exception:
                return b"" if return_raw else ""

        ap.AccessTable._parse_memo = _parse_memo_safe
        ap.AccessTable._memo_safe_patched = True

    return ap


def get_connection_string(mdb_path=None):
    if pyodbc is None:
        return None
    target_mdb = mdb_path or get_latest_mdb_path()
    drivers = [d for d in pyodbc.drivers() if "Access" in d or "ACE" in d]
    if "Microsoft Access Driver (*.mdb, *.accdb)" in drivers:
        return f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={target_mdb};"
    if "Microsoft Access Driver (*.mdb)" in drivers:
        return f"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={target_mdb};"
    return None


def load_data_from_mdb(mdb_path=None, columns=None):
    """Loads the Balance table from an Access .mdb file across Windows and macOS."""
    target_mdb = mdb_path or get_latest_mdb_path()
    if not os.path.exists(target_mdb):
        raise FileNotFoundError(f"Access database not found: {target_mdb}")

    cols = list(columns) if columns else list(DEFAULT_BALANCE_COLUMNS)
    select_clause = ", ".join(cols)

    # Option A: Windows pyodbc
    conn_str = get_connection_string(target_mdb)
    if conn_str and pyodbc is not None:
        try:
            conn = pyodbc.connect(conn_str)
            query = f"SELECT {select_clause} FROM Balance"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"pyodbc connection error: {e}")

    # Option B: Windows PowerShell / OLEDB export
    if sys.platform == "win32":
        print("Falling back to ADODB / OleDb extraction...")
        import subprocess

        ps_mdb = target_mdb.replace("'", "''")
        ps_script = f"""
        $connStr = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source={ps_mdb};Persist Security Info=False;"
        $conn = New-Object System.Data.OleDb.OleDbConnection($connStr)
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT {select_clause} FROM Balance"
        $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($cmd)
        $dt = New-Object System.Data.DataTable
        $adapter.Fill($dt) | Out-Null
        $conn.Close()
        $csvPath = "$env:TEMP\\sinensup_export.csv"
        $dt | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
        Write-Output $csvPath
        """
        tmp_ps = os.path.join(os.environ.get("TEMP", "."), "export_mdb.ps1")
        try:
            with open(tmp_ps, "w", encoding="utf-8") as f:
                f.write(ps_script)
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", tmp_ps], check=True)
            csv_file = os.path.join(os.environ.get("TEMP", "."), "sinensup_export.csv")
            return pd.read_csv(csv_file, encoding="utf-8")
        except Exception as e:
            print(f"PowerShell / OLEDB extraction error: {e}")

    # Option C: Cross-platform pure Python access_parser
    ap = _ensure_access_parser_patched()
    with open(target_mdb, "rb") as f:
        mdb_bytes = f.read()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mdb", delete=False) as tmp:
            tmp.write(mdb_bytes)
            tmp_path = tmp.name
        db = ap.AccessParser(tmp_path)
        table_data = db.parse_table("Balance")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    missing_cols = [c for c in cols if c not in table_data]
    if missing_cols:
        raise KeyError(f"Columns {missing_cols} not found in Balance table of {target_mdb}")

    return pd.DataFrame({c: table_data[c] for c in cols})


def get_balance_data(force_reload=False, period=None):
    """Loads, cleans, classifies, and caches Balance data for the target or latest period."""
    mdb_path = get_latest_mdb_path(period)
    expected_period = os.path.splitext(os.path.basename(mdb_path))[0]

    if not force_reload and os.path.exists(CACHE_PARQUET):
        try:
            df_cached = read_parquet_safe(CACHE_PARQUET)
            if (
                not df_cached.empty
                and "periodo" in df_cached.columns
                and str(df_cached["periodo"].iloc[0]).strip() == expected_period
            ):
                return df_cached
        except Exception:
            pass

    df = load_data_from_mdb(mdb_path)
    # Clean and standardize strings
    df["cod_cia"] = df["cod_cia"].fillna("").astype(str).str.strip().str.zfill(4)
    df["razon_social"] = df["razon_social"].fillna("").astype(str).str.strip()
    df["periodo"] = df["periodo"].fillna(expected_period).astype(str).str.strip()
    df["cod_cuenta"] = df["cod_cuenta"].fillna("").astype(str).str.strip()
    df["desc_cuenta"] = df["desc_cuenta"].fillna("").astype(str).str.strip()
    df["cod_subramo"] = df["cod_subramo"].fillna("").astype(str).str.strip()
    df["desc_subramo"] = df["desc_subramo"].fillna("").astype(str).str.strip()
    df["importe"] = pd.to_numeric(df["importe"], errors="coerce").fillna(0.0)
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce").fillna(0).astype(int)
    if "id_padre" in df.columns:
        df["id_padre"] = df["id_padre"].apply(
            lambda v: str(v).strip() if pd.notna(v) and str(v).strip() != "" else None
        )

    # Actuarial classification by company production structure & license
    cias = df[["cod_cia", "razon_social"]].drop_duplicates()
    seg_map = {}

    for _, row in cias.iterrows():
        c = row["cod_cia"]
        name = row["razon_social"]
        sub = df[df["cod_cia"] == c]

        # Production by subramo (cuentas 5.01)
        sub_ramos = sub[
            (sub["desc_subramo"] != "")
            & (sub["desc_subramo"].notna())
            & (sub["cod_cuenta"].str.startswith("5.01"))
        ]

        patrim = sub_ramos[
            sub_ramos["cod_subramo"].str.startswith("1.") & (~sub_ramos["cod_subramo"].str.startswith("1.050"))
        ]["importe"].sum()
        art = sub_ramos[sub_ramos["cod_subramo"].str.startswith("1.050")]["importe"].sum()
        personas = sub_ramos[
            sub_ramos["cod_subramo"].str.startswith("2.01")
            | sub_ramos["cod_subramo"].str.startswith("2.02")
            | sub_ramos["cod_subramo"].str.startswith("2.03")
            | sub_ramos["cod_subramo"].str.startswith("2.05")
        ]["importe"].sum()
        retiro = sub_ramos[
            sub_ramos["cod_subramo"].str.startswith("2.06") | sub_ramos["cod_subramo"].str.startswith("2.07")
        ]["importe"].sum()

        tot_primas = patrim + art + personas + retiro
        rs_upper = name.upper()

        if "RETIRO" in rs_upper or retiro > 0.5 * max(1, tot_primas):
            seg = "Seguros de Retiro"
        elif (
            "RIESGOS DEL TRABAJO" in rs_upper
            or " ART" in rs_upper
            or "A.R.T." in rs_upper
            or art > 0.5 * max(1, tot_primas)
        ):
            seg = "Riesgos del Trabajo (ART)"
        elif personas > 0.5 * max(1, tot_primas) or any(
            w in rs_upper
            for w in ["PERSONAS", "VIDA", "LIFE", "SALUD", "SEPELIO", "CARDIF", "METLIFE", "CNP", "PRUDENTIAL", "ZURICH INTERNATIONAL LIFE"]
        ):
            seg = "Seguros de Personas"
        else:
            seg = "Patrimoniales y Mixtas"

        seg_map[c] = seg

    df["tipo_entidad"] = df["cod_cia"].map(seg_map)

    # Save to Parquet cache for ultra-fast loading (for the latest local period)
    latest_period = os.path.splitext(os.path.basename(get_latest_mdb_path()))[0]
    if expected_period == latest_period:
        try:
            write_parquet_safe(df, CACHE_PARQUET)
            print(f"Data cached to {CACHE_PARQUET} ({len(df)} rows)")
        except Exception as e:
            print(f"Parquet save error: {e}")

    return df


if __name__ == "__main__":
    print("Testing get_balance_data()...")
    df = get_balance_data(force_reload=True)
    print(f"Loaded {len(df)} records for {df['cod_cia'].nunique()} companies (period: {df['periodo'].iloc[0]}).")
    print("Segments:\n", df[["cod_cia", "tipo_entidad"]].drop_duplicates()["tipo_entidad"].value_counts())
