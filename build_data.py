import json
import os
import pandas as pd
import numpy as np
from db_engine import get_balance_data
from insurance_kpis import (
    compute_all_companies_summary,
    get_company_waterfall_data,
    get_company_subramos,
    get_company_investments
)

def build_complete_dataset():
    print("Loading balance raw data...")
    df_raw = get_balance_data()
    print("Computing company summary...")
    df_summary = compute_all_companies_summary(df_raw)

    # Market-wide subramos
    market_subramos = get_company_subramos(df_raw)
    market_subramos_list = market_subramos.to_dict(orient='records')

    # Convert summary to list of dicts with deep dive details
    companies_dict = {}
    print("Building detailed profiles for each company...")

    for idx, row in df_summary.iterrows():
        c_code = row['cod_cia']
        df_cia_raw = df_raw[df_raw['cod_cia'] == c_code]

        waterfall = get_company_waterfall_data(df_cia_raw)
        subramos = get_company_subramos(df_raw, cod_cia=c_code).to_dict(orient='records')
        investments = get_company_investments(df_cia_raw).to_dict(orient='records')

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
