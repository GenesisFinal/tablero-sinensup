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
    df_raw = get_balance_data(force_reload=False)
    print("Computing company summary...")
    df_summary = compute_all_companies_summary(df_raw)

    # Market-wide subramos
    market_subramos_list = get_company_subramos(df_raw)

    # Macro Branch Totals - Calculated directly from summary to ensure 100% mathematical consistency
    tot_emit = float(df_summary['primas_emitidas'].sum())
    tot_dev = float(df_summary['primas_devengadas'].sum())

    def get_seg_sums(seg_name):
        sub = df_summary[df_summary['tipo_entidad'] == seg_name]
        return {
            'emitidas': float(sub['primas_emitidas'].sum()),
            'devengadas': float(sub['primas_devengadas'].sum()),
            'entidades': int(len(sub))
        }

    patrim = get_seg_sums('Patrimoniales y Mixtas')
    art = get_seg_sums('Riesgos del Trabajo (ART)')
    personas = get_seg_sums('Seguros de Personas')
    retiro = get_seg_sums('Seguros de Retiro')

    macro_ramos = {
        "total_mercado_emitidas": round(tot_emit, 2),
        "total_mercado_devengadas": round(tot_dev, 2),
        "patrimoniales_emitidas": round(patrim['emitidas'], 2),
        "patrimoniales_devengadas": round(patrim['devengadas'], 2),
        "patrimoniales_entidades": patrim['entidades'],
        "art_emitidas": round(art['emitidas'], 2),
        "art_devengadas": round(art['devengadas'], 2),
        "art_entidades": art['entidades'],
        "personas_emitidas": round(personas['emitidas'], 2),
        "personas_devengadas": round(personas['devengadas'], 2),
        "personas_entidades": personas['entidades'],
        "retiro_emitidas": round(retiro['emitidas'], 2),
        "retiro_devengadas": round(retiro['devengadas'], 2),
        "retiro_entidades": retiro['entidades']
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
