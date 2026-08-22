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

    # Market-wide subramos (unified full emission)
    market_subramos_list = get_company_subramos(df_raw)

    # 1. Macro Branch Totals BY ENTITY TYPE
    tot_emit = float(df_summary['primas_emitidas'].sum())
    tot_dev = float(df_summary['primas_devengadas'].sum())

    def get_seg_sums(seg_name):
        sub = df_summary[df_summary['tipo_entidad'] == seg_name]
        return {
            'emitidas': float(sub['primas_emitidas'].sum()),
            'devengadas': float(sub['primas_devengadas'].sum()),
            'entidades': int(len(sub))
        }

    patrim_ent = get_seg_sums('Patrimoniales y Mixtas')
    art_ent = get_seg_sums('Riesgos del Trabajo (ART)')
    personas_ent = get_seg_sums('Seguros de Personas')
    retiro_ent = get_seg_sums('Seguros de Retiro')

    macro_entidades = {
        "total_mercado_emitidas": round(tot_emit, 2),
        "total_mercado_devengadas": round(tot_dev, 2),
        "patrimoniales_emitidas": round(patrim_ent['emitidas'], 2),
        "patrimoniales_devengadas": round(patrim_ent['devengadas'], 2),
        "patrimoniales_entidades": patrim_ent['entidades'],
        "art_emitidas": round(art_ent['emitidas'], 2),
        "art_devengadas": round(art_ent['devengadas'], 2),
        "art_entidades": art_ent['entidades'],
        "personas_emitidas": round(personas_ent['emitidas'], 2),
        "personas_devengadas": round(personas_ent['devengadas'], 2),
        "personas_entidades": personas_ent['entidades'],
        "retiro_emitidas": round(retiro_ent['emitidas'], 2),
        "retiro_devengadas": round(retiro_ent['devengadas'], 2),
        "retiro_entidades": retiro_ent['entidades']
    }

    # 2. Macro Branch Totals BY REAL PRODUCT LINE (Unified with Directas + Derechos + Recargos + Reaseguros)
    accounts_primas = (
        '5.01.01.01.01.01.01', '5.01.01.01.01.01.99',
        '5.01.01.01.01.02.01', '5.01.01.01.01.02.99',
        '5.01.01.01.01.03.02', '5.01.01.01.01.03.99',
        '5.01.01.01.01.04.01', '5.01.01.01.01.04.99'
    )
    primas_sub = df_raw[df_raw['cod_cuenta'].str.startswith(accounts_primas) & (df_raw['desc_subramo'] != '') & (df_raw['desc_subramo'].notna())]
    sin_sub = df_raw[df_raw['cod_cuenta'].str.startswith(('4.01.01.01.01.01', '4.01.01.01.01.99', '4.01.01.01.02.01', '4.01.01.01.02.99', '4.01.01.01.03.01', '4.01.01.01.03.99', '4.01.01.01.04.01', '4.01.01.01.04.99', '4.01.02.01', '4.01.02.02', '4.01.02.03')) & (df_raw['desc_subramo'] != '') & (df_raw['desc_subramo'].notna())]

    def get_macro_product(cod_sub):
        cod_str = str(cod_sub).strip()
        if cod_str.startswith('1.050') or cod_str.startswith('1.50') or cod_str == '1.05':
            return 'art'
        elif cod_str.startswith('1.'):
            return 'patrimoniales'
        elif cod_str.startswith('2.06') or cod_str.startswith('2.07') or cod_str.startswith('2.08'):
            return 'retiro'
        elif cod_str.startswith('2.'):
            return 'personas'
        return 'otros'

    p_df = primas_sub.copy()
    s_df = sin_sub.copy()
    p_df['macro_prod'] = p_df['cod_subramo'].apply(get_macro_product)
    s_df['macro_prod'] = s_df['cod_subramo'].apply(get_macro_product)

    tot_prod_p = float(p_df['importe'].sum())
    tot_prod_s = float(s_df['importe'].sum())

    macro_productos = {}
    for k in ['patrimoniales', 'art', 'personas', 'retiro']:
        p_val = float(p_df[p_df['macro_prod'] == k]['importe'].sum())
        s_val = float(s_df[s_df['macro_prod'] == k]['importe'].sum())
        sin_pct = (s_val / p_val * 100) if p_val > 0 else 0.0
        part_pct = (p_val / tot_prod_p * 100) if tot_prod_p > 0 else 0.0

        macro_productos[k] = {
            "primas": round(p_val, 2),
            "siniestros": round(s_val, 2),
            "siniestralidad": round(sin_pct, 1),
            "participacion": round(part_pct, 1)
        }

    # Cross-selling breakdown for personas
    pers_p_df = p_df[p_df['macro_prod'] == 'personas']
    pers_in_mixtas = float(pers_p_df[pers_p_df['tipo_entidad'] == 'Patrimoniales y Mixtas']['importe'].sum())
    pers_in_personas = float(pers_p_df[pers_p_df['tipo_entidad'] == 'Seguros de Personas']['importe'].sum())
    pers_in_art = float(pers_p_df[pers_p_df['tipo_entidad'] == 'Riesgos del Trabajo (ART)']['importe'].sum())

    macro_productos['personas_cross_selling'] = {
        "en_mixtas": round(pers_in_mixtas, 2),
        "en_personas": round(pers_in_personas, 2),
        "en_art": round(pers_in_art, 2),
        "pct_en_mixtas": round((pers_in_mixtas / macro_productos['personas']['primas'] * 100), 1) if macro_productos['personas']['primas'] > 0 else 0.0,
        "pct_en_personas": round((pers_in_personas / macro_productos['personas']['primas'] * 100), 1) if macro_productos['personas']['primas'] > 0 else 0.0
    }

    macro_productos['total'] = {
        "primas": round(tot_prod_p, 2),
        "siniestros": round(tot_prod_s, 2),
        "siniestralidad": round((tot_prod_s / tot_prod_p * 100), 1) if tot_prod_p > 0 else 0.0
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

    # Market and Segment Investment Breakdowns
    market_investments = get_company_investments_breakdown(df_raw)
    segment_investments = {}
    for seg in segments:
        segment_investments[seg] = get_company_investments_breakdown(df_raw[df_raw['tipo_entidad'] == seg])

    def compute_benchmarks(df_sub):
        tot_emit = float(df_sub['primas_emitidas'].sum())
        tot_dev = float(df_sub['primas_devengadas'].sum())
        base_primas = tot_dev if tot_dev > 0 else tot_emit
        tot_sin = float(df_sub['siniestros'].sum() + df_sub['rescates'].sum())
        tot_prod = float(df_sub['gtos_produccion'].sum())
        tot_expl = float(df_sub['gtos_explotacion'].sum())
        tot_gtos_op = float(df_sub['gtos_operativos'].sum())
        tot_res_tec = float(df_sub['resultado_tecnico'].sum())
        tot_res_fin = float(df_sub['resultado_financiero'].sum())
        tot_res_neto = float(df_sub['resultado_neto'].sum())
        tot_inv = float(df_sub['inversiones'].sum())
        tot_inm = float(df_sub['inmuebles'].sum())
        tot_disp = float(df_sub['disponibilidades'].sum())
        tot_ct = float(df_sub['compromisos_tecnicos'].sum())
        tot_pn = float(df_sub['patrimonio_neto'].sum())
        tot_activo = float(df_sub['activo'].sum())
        tot_premios = float(df_sub['premios_a_cobrar'].sum())

        return {
            'entidades': int(len(df_sub)),
            'primas_emitidas': tot_emit,
            'primas_devengadas': tot_dev,
            'loss_ratio': round((tot_sin / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'comm_ratio': round((tot_prod / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'exp_ratio': round((tot_expl / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'combined_ratio': round(((tot_sin + tot_gtos_op) / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'retencion_ratio': round((tot_dev / tot_emit * 100.0) if tot_emit > 0 else 100.0, 2),
            'roi_inversiones': round((tot_res_fin / tot_inv * 100.0) if tot_inv > 0 else 0.0, 2),
            'densidad_inversiones': round((tot_inv / tot_activo * 100.0) if tot_activo > 0 else 0.0, 2),
            'cobertura_reservas': round(((tot_inv + tot_inm + tot_disp) / tot_ct) if tot_ct > 0 else 1.0, 2),
            'apalancamiento': round((base_primas / tot_pn) if tot_pn > 0 else 0.0, 2),
            'calidad_cartera': round((tot_premios / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'roe': round((tot_res_neto / tot_pn * 100.0) if tot_pn > 0 else 0.0, 2),
            'roa': round((tot_res_neto / tot_activo * 100.0) if tot_activo > 0 else 0.0, 2),
            'margen_neto': round((tot_res_neto / base_primas * 100.0) if base_primas > 0 else 0.0, 2),
            'patrimonio_neto': tot_pn,
            'activo': tot_activo,
            'inversiones': tot_inv,
            'resultado_tecnico': tot_res_tec,
            'resultado_financiero': tot_res_fin,
            'resultado_neto': tot_res_neto
        }

    market_benchmarks = compute_benchmarks(df_summary)
    segment_benchmarks = {}
    for seg in segments:
        segment_benchmarks[seg] = compute_benchmarks(df_summary[df_summary['tipo_entidad'] == seg])

    payload = {
        "periodo": str(df_raw['periodo'].iloc[0]),
        "total_entidades": len(df_summary),
        "segmentos": segments,
        "macro_ramos": macro_entidades,
        "macro_entidades": macro_entidades,
        "macro_productos": macro_productos,
        "market_subramos": market_subramos_list,
        "market_investments": market_investments,
        "segment_investments": segment_investments,
        "market_benchmarks": market_benchmarks,
        "segment_benchmarks": segment_benchmarks,
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
