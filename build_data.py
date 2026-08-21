import json
import os
import pandas as pd
import numpy as np
from db_engine import get_balance_data
from insurance_kpis import (
    compute_all_companies_summary,
    get_company_waterfall_data,
    get_company_subramos,
    get_company_investments_breakdown
)

def build_complete_dataset():
    print("Loading balance raw data...")
    df_raw = get_balance_data(force_reload=True)
    print("Computing company summary...")
    df_summary = compute_all_companies_summary(df_raw)

    # Market-wide subramos
    market_subramos_list = get_company_subramos(df_raw)

    # Macro Branch Totals
    sub_valid = df_raw[(df_raw['desc_subramo'] != '') & (df_raw['desc_subramo'].notna()) & (df_raw['cod_cuenta'].str.startswith('5.01'))]
    
    patrim_total = float(sub_valid[sub_valid['cod_subramo'].str.startswith('1.') & (~sub_valid['cod_subramo'].str.startswith('1.050'))]['importe'].sum())
    art_total = float(sub_valid[sub_valid['cod_subramo'].str.startswith('1.050')]['importe'].sum())
    personas_total = float(sub_valid[sub_valid['cod_subramo'].str.startswith('2.01') | sub_valid['cod_subramo'].str.startswith('2.02') | sub_valid['cod_subramo'].str.startswith('2.03') | sub_valid['cod_subramo'].str.startswith('2.05')]['importe'].sum())
    retiro_total = float(sub_valid[sub_valid['cod_subramo'].str.startswith('2.06') | sub_valid['cod_subramo'].str.startswith('2.07')]['importe'].sum())
    mercado_total = patrim_total + art_total + personas_total + retiro_total

    macro_ramos = {
        "patrimoniales": round(patrim_total, 2),
        "art": round(art_total, 2),
        "personas_vida": round(personas_total, 2),
        "retiro": round(retiro_total, 2),
        "total_mercado": round(mercado_total, 2)
    }

    # Convert summary to list of dicts with deep dive details
    companies_dict = {}
    print("Building detailed profiles for each company...")

    for idx, row in df_summary.iterrows():
        c_code = row['cod_cia']
        df_cia_raw = df_raw[df_raw['cod_cia'] == c_code]

        waterfall = get_company_waterfall_data(df_cia_raw)
        subramos = get_company_subramos(df_raw, cod_cia=c_code)
        investments = get_company_investments_breakdown(df_cia_raw)

        c_data = row.to_dict()
        # Clean NaNs and infinite values
        for k, v in c_data.items():
            if isinstance(v, float):
                if np.isnan(v) or np.isinf(v):
                    c_data[k] = 0.0
                else:
                    c_data[k] = round(v, 2)
            elif isinstance(v, (np.int64, np.int32)):
                c_data[k] = int(v)

        c_data['waterfall'] = waterfall
        c_data['subramos'] = subramos
        c_data['investments'] = investments

        companies_dict[c_code] = c_data

    # Segments list
    segments = sorted(df_summary['tipo_entidad'].unique().tolist())

    payload = {
        "periodo": str(df_raw['periodo'].iloc[0]),
        "total_entidades": len(df_summary),
        "segmentos": segments,
        "macro_ramos": macro_ramos,
        "market_subramos": market_subramos_list,
        "companies": list(companies_dict.values()),
        "companies_by_code": companies_dict
    }

    out_json = r"g:\Mi unidad\IA\Sinensup\data_sinensup.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"data_sinensup.json generated successfully: {len(payload['companies'])} companies ({os.path.getsize(out_json):,} bytes)")
    return out_json

if __name__ == '__main__':
    build_complete_dataset()
