import json
import os
import pyodbc
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

    # 2. Macro Branch Totals BY REAL PRODUCT LINE (Emisión Directa Neta Total: Directas + Derechos + Recargos - Anulaciones)
    pos_accounts = (
        '5.01.01.01.01.01.01', '5.01.01.01.01.01.99',
        '5.01.01.01.01.02.01', '5.01.01.01.01.02.99',
        '5.01.01.01.01.03.02', '5.01.01.01.01.03.99'
    )
    neg_accounts = (
        '4.01.04.04.04.01.01', '4.01.04.04.04.01.99',
        '4.01.04.04.04.02.01', '4.01.04.04.04.02.99'
    )
    sin_accounts = (
        '4.01.01.01.01.01', '4.01.01.01.01.99', '4.01.01.01.02.01', '4.01.01.01.02.99',
        '4.01.01.01.03.01', '4.01.01.01.03.99', '4.01.01.01.04.01', '4.01.01.01.04.99',
        '4.01.02.01', '4.01.02.02', '4.01.02.03'
    )

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

    sub_clean = df_raw[(df_raw['desc_subramo'] != '') & (df_raw['desc_subramo'].notna())].copy()
    sub_clean['macro_prod'] = sub_clean['cod_subramo'].apply(get_macro_product)

    macro_productos = {}
    tot_prod_p = 0.0
    for k in ['patrimoniales', 'art', 'personas', 'retiro']:
        k_df = sub_clean[sub_clean['macro_prod'] == k]
        p_pos = float(k_df[k_df['cod_cuenta'].str.startswith(pos_accounts)]['importe'].sum())
        p_neg = float(k_df[k_df['cod_cuenta'].str.startswith(neg_accounts)]['importe'].sum())
        p_val = p_pos - p_neg
        s_val = float(k_df[k_df['cod_cuenta'].str.startswith(sin_accounts)]['importe'].sum())
        tot_prod_p += p_val
        sin_pct = (s_val / p_val * 100) if p_val > 0 else 0.0

        macro_productos[k] = {
            "primas": round(p_val, 2),
            "siniestros": round(s_val, 2),
            "siniestralidad": round(sin_pct, 1),
            "participacion": 0.0
        }

    for k in ['patrimoniales', 'art', 'personas', 'retiro']:
        macro_productos[k]["participacion"] = round((macro_productos[k]['primas'] / tot_prod_p * 100) if tot_prod_p > 0 else 0.0, 1)

    # Cross-selling breakdown for personas
    pers_k_df = sub_clean[sub_clean['macro_prod'] == 'personas']
    def get_pers_net_by_tipo(t_name):
        t_df = pers_k_df[pers_k_df['tipo_entidad'] == t_name]
        pos = float(t_df[t_df['cod_cuenta'].str.startswith(pos_accounts)]['importe'].sum())
        neg = float(t_df[t_df['cod_cuenta'].str.startswith(neg_accounts)]['importe'].sum())
        return pos - neg

    pers_in_mixtas = get_pers_net_by_tipo('Patrimoniales y Mixtas')
    pers_in_personas = get_pers_net_by_tipo('Seguros de Personas')
    pers_in_art = get_pers_net_by_tipo('Riesgos del Trabajo (ART)')

    macro_productos['personas_cross_selling'] = {
        "en_mixtas": round(pers_in_mixtas, 2),
        "en_personas": round(pers_in_personas, 2),
        "en_art": round(pers_in_art, 2),
        "pct_en_mixtas": round((pers_in_mixtas / macro_productos['personas']['primas'] * 100), 1) if macro_productos['personas']['primas'] > 0 else 0.0,
        "pct_en_personas": round((pers_in_personas / macro_productos['personas']['primas'] * 100), 1) if macro_productos['personas']['primas'] > 0 else 0.0
    }

    tot_prod_s = sum(macro_productos[k]['siniestros'] for k in ['patrimoniales', 'art', 'personas', 'retiro'])

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
            'retencion_ratio': round(((tot_emit - float(df_sub['primas_cedidas'].sum())) / tot_emit * 100.0) if tot_emit > 0 else 100.0, 2),
            'cesion_ratio': round((float(df_sub['primas_cedidas'].sum()) / tot_emit * 100.0) if tot_emit > 0 else 0.0, 2),
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

    # ========================================================
    # COMPLETE BALANCE PLAN DE CUENTAS & HIERARCHICAL TREES
    # ========================================================
    print("Building complete Plan de Cuentas and balance trees...")
    cat_df = df_raw[['cod_cuenta', 'desc_cuenta', 'nivel', 'id_padre']].drop_duplicates().sort_values('cod_cuenta')
    all_codes_set = set(cat_df['cod_cuenta'].astype(str))

    def get_parent_account_code(code, nivel):
        if nivel <= 1:
            return ''
        parts = code.split('.')
        for try_level in range(nivel - 1, 0, -1):
            parent_parts = parts[:]
            for i in range(try_level, len(parts)):
                parent_parts[i] = '00'
            candidate = '.'.join(parent_parts)
            if candidate in all_codes_set and candidate != code:
                return candidate
        return ''

    plan_de_cuentas = {}
    for _, r in cat_df.iterrows():
        code_str = str(r['cod_cuenta'])
        niv = int(r['nivel'])
        padre_code = get_parent_account_code(code_str, niv)
        plan_de_cuentas[code_str] = {
            'desc': str(r['desc_cuenta']),
            'nivel': niv,
            'padre_codigo': padre_code,
            'id_padre': str(r['id_padre']) if pd.notna(r['id_padre']) else ''
        }

    # Build children mapping for recursive hierarchical rollups
    children_map = {}
    for code, info in plan_de_cuentas.items():
        padre = info.get('padre_codigo')
        if padre and padre in plan_de_cuentas:
            if padre not in children_map:
                children_map[padre] = []
            children_map[padre].append(code)

    def compute_hierarchical_rollup(raw_dict, is_subramo=False):
        memo = {}
        def get_total(code):
            if code in memo:
                return memo[code]
            children = children_map.get(code, [])
            if not children:
                val = float(raw_dict.get(code, 0.0))
            else:
                child_sums = sum(get_total(child) for child in children)
                raw_val = float(raw_dict.get(code, 0.0))
                if is_subramo:
                    val = child_sums if child_sums != 0 else raw_val
                else:
                    # In general balance, preserve explicit reported figures if present, otherwise roll up
                    val = raw_val if raw_val != 0 else child_sums
            memo[code] = val
            return val

        rolled = {}
        for code in plan_de_cuentas.keys():
            tot = get_total(code)
            if tot != 0:
                rolled[code] = round(tot, 2)

        if is_subramo:
            # Emisión Directa Neta Total: (Directas + Derechos + Recargos) - (Anulaciones Directas + Anulaciones Recargos)
            p_dir = float(raw_dict.get('5.01.01.01.01.01.01.00', 0.0)) + float(raw_dict.get('5.01.01.01.01.01.99.00', 0.0))
            der = float(raw_dict.get('5.01.01.01.01.02.01.00', 0.0)) + float(raw_dict.get('5.01.01.01.01.02.99.00', 0.0))
            rec = float(raw_dict.get('5.01.01.01.01.03.02.00', 0.0)) + float(raw_dict.get('5.01.01.01.01.03.99.00', 0.0))
            a_dir = float(raw_dict.get('4.01.04.04.04.01.01.00', 0.0)) + float(raw_dict.get('4.01.04.04.04.01.99.00', 0.0))
            a_rec = float(raw_dict.get('4.01.04.04.04.02.01.00', 0.0)) + float(raw_dict.get('4.01.04.04.04.02.99.00', 0.0))
            rolled['_net_emit'] = round((p_dir + der + rec) - (a_dir + a_rec), 2)

        return rolled

    # General Balance (where cod_subramo is empty)
    gen_df = df_raw[df_raw['cod_subramo'].fillna('') == '']
    gen_agg = gen_df.groupby(['cod_cia', 'cod_cuenta'])['importe'].sum().reset_index()

    cias_balances_general = {}
    for cod_cia, grp in gen_agg.groupby('cod_cia'):
        raw_map = {str(r['cod_cuenta']): round(float(r['importe']), 2) for _, r in grp.iterrows()}
        cias_balances_general[str(cod_cia)] = compute_hierarchical_rollup(raw_map, is_subramo=False)

    market_raw = {str(k): round(float(v), 2) for k, v in gen_df.groupby('cod_cuenta')['importe'].sum().items()}
    market_balances_general = compute_hierarchical_rollup(market_raw, is_subramo=False)

    segment_balances_general = {}
    for seg, grp in gen_df.groupby('tipo_entidad'):
        seg_raw = {str(k): round(float(v), 2) for k, v in grp.groupby('cod_cuenta')['importe'].sum().items()}
        segment_balances_general[str(seg)] = compute_hierarchical_rollup(seg_raw, is_subramo=False)

    # Subramo technical balances
    sub_df = df_raw[df_raw['cod_subramo'].fillna('') != '']
    sub_cat = sub_df[['cod_subramo', 'desc_subramo']].drop_duplicates().sort_values('cod_subramo')
    subramos_catalog = [{'cod': str(r['cod_subramo']), 'desc': str(r['desc_subramo'])} for _, r in sub_cat.iterrows()]

    sub_agg = sub_df.groupby(['cod_cia', 'cod_subramo', 'cod_cuenta'])['importe'].sum().reset_index()
    cias_balances_subramos = {}
    for (cod_cia, cod_sub), grp in sub_agg.groupby(['cod_cia', 'cod_subramo']):
        cod_cia_str = str(cod_cia)
        cod_sub_str = str(cod_sub)
        if cod_cia_str not in cias_balances_subramos:
            cias_balances_subramos[cod_cia_str] = {}
        raw_map = {str(r['cod_cuenta']): round(float(r['importe']), 2) for _, r in grp.iterrows()}
        cias_balances_subramos[cod_cia_str][cod_sub_str] = compute_hierarchical_rollup(raw_map, is_subramo=True)

    market_balances_subramos = {}
    for cod_sub, grp in sub_df.groupby('cod_subramo'):
        raw_map = {str(k): round(float(v), 2) for k, v in grp.groupby('cod_cuenta')['importe'].sum().items()}
        market_balances_subramos[str(cod_sub)] = compute_hierarchical_rollup(raw_map, is_subramo=True)

    segment_balances_subramos = {}
    for (seg, cod_sub), grp in sub_df.groupby(['tipo_entidad', 'cod_subramo']):
        seg_str = str(seg)
        cod_sub_str = str(cod_sub)
        if seg_str not in segment_balances_subramos:
            segment_balances_subramos[seg_str] = {}
        raw_map = {str(k): round(float(v), 2) for k, v in grp.groupby('cod_cuenta')['importe'].sum().items()}
        segment_balances_subramos[seg_str][cod_sub_str] = compute_hierarchical_rollup(raw_map, is_subramo=True)

    # ========================================================
    # INSURANCE GROUPS (GRUPOS ASEGURADORES) CONSOLIDATION
    # ========================================================
    print("Consolidating Insurance Groups...")
    GROUPS_DEFINITIONS = [
        {
            "id": "sancor",
            "name": "Grupo Sancor Seguros",
            "short_name": "Sancor Seguros",
            "codes": ["0224", "0626", "0930"],
            "description": "Sancor Seguros, Prevención ART, Prevención Retiro"
        },
        {
            "id": "federacion_patronal",
            "name": "Grupo Federación Patronal",
            "short_name": "Federación Patronal",
            "codes": ["0726", "0425"],
            "description": "Federación Patronal Seguros (PM+ART), Federación Patronal Retiro"
        },
        {
            "id": "provincia",
            "name": "Grupo Provincia",
            "short_name": "Provincia",
            "codes": ["0499", "0621", "0532"],
            "description": "Provincia Seguros, Provincia ART, Provincia Vida"
        },
        {
            "id": "san_cristobal",
            "name": "Grupo San Cristóbal",
            "short_name": "San Cristóbal",
            "codes": ["0192", "0620", "0434"],
            "description": "San Cristóbal Seguros, Asociart ART, San Cristóbal Retiro"
        },
        {
            "id": "la_segunda",
            "name": "Grupo Asegurador La Segunda",
            "short_name": "La Segunda",
            "codes": ["0317", "0618", "0117", "0436"],
            "description": "La Segunda Generales, La Segunda ART, La Segunda Personas, La Segunda Retiro"
        },
        {
            "id": "la_caja_generali",
            "name": "Grupo La Caja / Generali",
            "short_name": "La Caja / Generali",
            "codes": ["0501"],
            "description": "Caja de Seguros S.A. (Patrimoniales y Vida)"
        },
        {
            "id": "zurich",
            "name": "Grupo Zurich",
            "short_name": "Zurich",
            "codes": ["0228", "0692", "0541"],
            "description": "Zurich Argentina, Zurich Santander, Zurich International Life"
        },
        {
            "id": "experta_werthein",
            "name": "Grupo Experta / Werthein",
            "short_name": "Experta / Werthein",
            "codes": ["0880", "0616", "0419"],
            "description": "Experta Seguros, Experta ART, La Estrella Retiro"
        },
        {
            "id": "mercantil_andina",
            "name": "Grupo Mercantil Andina",
            "short_name": "Mercantil Andina",
            "codes": ["0116", "0959"],
            "description": "Mercantil Andina, Andina ART"
        },
        {
            "id": "rivadavia",
            "name": "Grupo Asegurador Rivadavia",
            "short_name": "Rivadavia",
            "codes": ["0222", "0678"],
            "description": "Seguros Bernardino Rivadavia, Mutual Rivadavia TP"
        },
        {
            "id": "galicia",
            "name": "Grupo Galicia Seguros",
            "short_name": "Galicia Seguros",
            "codes": ["0025", "0589", "0443", "0426"],
            "description": "Galicia Seguros, Sudamericana Seguros Galicia, Galicia Retiro"
        },
        {
            "id": "swiss_medical",
            "name": "Grupo Swiss Medical (SMG)",
            "short_name": "Swiss Medical (SMG)",
            "codes": ["0002", "0605", "0580", "0710", "0661"],
            "description": "SMG Seguros, Swiss Medical ART, SMG Life, SMG Retiro, Instituto de Salta"
        },
        {
            "id": "st",
            "name": "Grupo ST",
            "short_name": "Grupo ST",
            "codes": ["0251", "0423"],
            "description": "Life Seguros, Orígenes Retiro"
        },
        {
            "id": "nacion",
            "name": "Grupo Nación",
            "short_name": "Nación",
            "codes": ["0244", "0424"],
            "description": "Nación Seguros, Nación Retiro"
        },
        {
            "id": "mapfre",
            "name": "Grupo Mapfre",
            "short_name": "Mapfre",
            "codes": ["0213", "0699"],
            "description": "Mapfre Seguros, Mapfre Vida"
        },
        {
            "id": "barbuss_hdi",
            "name": "Grupo Barbuss / HDI",
            "short_name": "Barbuss / HDI",
            "codes": ["0335"],
            "description": "Barbuss Risk Seguros (ex HDI Seguros)"
        },
        {
            "id": "galeno",
            "name": "Grupo Galeno",
            "short_name": "Galeno",
            "codes": ["0878", "0606"],
            "description": "Galeno Seguros, Galeno ART"
        }
    ]

    total_mkt_emit = float(macro_entidades['total_mercado_emitidas'])
    total_mkt_dev = float(macro_entidades['total_mercado_devengadas'])

    groups_ranking = []
    groups_by_id = {}
    groups_balances_general = {}
    groups_balances_subramos = {}

    for gdef in GROUPS_DEFINITIONS:
        gid = gdef['id']
        gname = gdef['name']
        codes = gdef['codes']
        
        # Collect member companies that exist in dataset
        members = []
        tot_emit = 0.0
        tot_dev = 0.0
        tot_var = 0.0
        tot_sin = 0.0
        tot_gtos_prod = 0.0
        tot_gtos_exp = 0.0
        tot_res_tec = 0.0
        tot_res_fin = 0.0
        tot_res_neto = 0.0
        tot_activo = 0.0
        tot_inv = 0.0
        tot_disp = 0.0
        tot_cred = 0.0
        tot_inm = 0.0
        tot_deudas = 0.0
        tot_comp_tec = 0.0
        tot_pn = 0.0

        for cd in codes:
            if cd in companies_dict:
                c = companies_dict[cd]
                members.append(c)
                tot_emit += float(c.get('primas_emitidas', 0.0))
                tot_dev += float(c.get('primas_devengadas', 0.0))
                tot_var += float(c.get('var_reservas', 0.0))
                tot_sin += float(c.get('siniestros', 0.0))
                tot_gtos_prod += float(c.get('gastos_produccion', 0.0))
                tot_gtos_exp += float(c.get('gastos_explotacion', 0.0))
                tot_res_tec += float(c.get('resultado_tecnico', 0.0))
                tot_res_fin += float(c.get('resultado_financiero', 0.0))
                tot_res_neto += float(c.get('resultado_neto', 0.0))
                tot_activo += float(c.get('activo', 0.0))
                tot_inv += float(c.get('inversiones', 0.0))
                tot_disp += float(c.get('disponibilidades', 0.0))
                tot_cred += float(c.get('creditos', 0.0))
                tot_inm += float(c.get('inmuebles', 0.0))
                tot_deudas += float(c.get('deudas', 0.0))
                tot_comp_tec += float(c.get('compromisos_tecnicos', 0.0))
                tot_pn += float(c.get('patrimonio_neto', 0.0))

        if len(members) == 0:
            continue

        # Weighted consolidated ratios
        loss_ratio = (tot_sin / tot_dev * 100.0) if tot_dev > 0 else 0.0
        comm_ratio = (tot_gtos_prod / tot_dev * 100.0) if tot_dev > 0 else 0.0
        exp_ratio = (tot_gtos_exp / tot_dev * 100.0) if tot_dev > 0 else 0.0
        combined_ratio = loss_ratio + comm_ratio + exp_ratio
        
        roi_inv = (tot_res_fin / tot_inv * 100.0) if tot_inv > 0 else 0.0
        total_reservas = tot_comp_tec + tot_deudas
        cobertura_reservas = (tot_inv + tot_inm) / total_reservas if total_reservas > 0 else 0.0
        apalancamiento = total_reservas / tot_pn if tot_pn > 0 else 0.0
        calidad_cartera = (tot_cred / tot_activo * 100.0) if tot_activo > 0 else 0.0
        roe = (tot_res_neto / tot_pn * 100.0) if tot_pn > 0 else 0.0
        roa = (tot_res_neto / tot_activo * 100.0) if tot_activo > 0 else 0.0
        margen_neto = (tot_res_neto / tot_dev * 100.0) if tot_dev > 0 else 0.0
        mkt_share = (tot_emit / total_mkt_emit * 100.0) if total_mkt_emit > 0 else 0.0

        # Members breakdown with individual share of group
        members_summary = []
        for m in members:
            m_emit = float(m.get('primas_emitidas', 0.0))
            members_summary.append({
                "cod_cia": m['cod_cia'],
                "razon_social": m['razon_social'],
                "tipo_entidad": m['tipo_entidad'],
                "primas_emitidas": m_emit,
                "primas_devengadas": float(m.get('primas_devengadas', 0.0)),
                "siniestros": float(m.get('siniestros', 0.0)),
                "resultado_tecnico": float(m.get('resultado_tecnico', 0.0)),
                "resultado_financiero": float(m.get('resultado_financiero', 0.0)),
                "resultado_neto": float(m.get('resultado_neto', 0.0)),
                "vpp_resultado": float(m.get('vpp_resultado', 0.0)),
                "vpp_activo": float(m.get('vpp_activo', 0.0)),
                "vpp_pct_neto": float(m.get('vpp_pct_neto', 0.0)),
                "activo": float(m.get('activo', 0.0)),
                "patrimonio_neto": float(m.get('patrimonio_neto', 0.0)),
                "combined_ratio": float(m.get('combined_ratio', 0.0)),
                "share_of_group": round((m_emit / tot_emit * 100.0) if tot_emit > 0 else 0.0, 1)
            })
        members_summary.sort(key=lambda x: x['primas_emitidas'], reverse=True)

        g_obj = {
            "id": gid,
            "name": gname,
            "short_name": gdef['short_name'],
            "description": gdef['description'],
            "entities_count": len(members),
            "members": members_summary,
            "primas_emitidas": tot_emit,
            "primas_devengadas": tot_dev,
            "var_reservas": tot_var,
            "siniestros": tot_sin,
            "gastos_produccion": tot_gtos_prod,
            "gastos_explotacion": tot_gtos_exp,
            "resultado_tecnico": tot_res_tec,
            "resultado_financiero": tot_res_fin,
            "resultado_neto": tot_res_neto,
            "activo": tot_activo,
            "inversiones": tot_inv,
            "disponibilidades": tot_disp,
            "creditos": tot_cred,
            "inmuebles": tot_inm,
            "deudas": tot_deudas,
            "compromisos_tecnicos": tot_comp_tec,
            "patrimonio_neto": tot_pn,
            "loss_ratio": round(loss_ratio, 2),
            "comm_ratio": round(comm_ratio, 2),
            "exp_ratio": round(exp_ratio, 2),
            "combined_ratio": round(combined_ratio, 2),
            "roi_inversiones": round(roi_inv, 2),
            "cobertura_reservas": round(cobertura_reservas, 2),
            "apalancamiento": round(apalancamiento, 2),
            "calidad_cartera": round(calidad_cartera, 2),
            "roe": round(roe, 2),
            "roa": round(roa, 2),
            "margen_neto": round(margen_neto, 2),
            "margen_tecnico": round((tot_res_tec / tot_dev * 100.0) if tot_dev > 0 else 0.0, 2),
            "market_share": round(mkt_share, 2),
            "waterfall": [
                {"name": "Primas Emitidas", "amount": tot_emit, "type": "relative"},
                {"name": "Variación Reservas", "amount": tot_var, "type": "relative"},
                {"name": "Primas Devengadas", "amount": tot_dev, "type": "total"},
                {"name": "Siniestros Netos", "amount": -tot_sin, "type": "relative"},
                {"name": "Gastos Producción", "amount": -tot_gtos_prod, "type": "relative"},
                {"name": "Gastos Explotación", "amount": -tot_gtos_exp, "type": "relative"},
                {"name": "Resultado Técnico", "amount": tot_res_tec, "type": "total"},
                {"name": "Resultado Financiero", "amount": tot_res_fin, "type": "relative"},
                {"name": "Otros Ing/Egr e Imp.", "amount": tot_res_neto - tot_res_tec - tot_res_fin, "type": "relative"},
                {"name": "Resultado Neto", "amount": tot_res_neto, "type": "total"}
            ]
        }

        groups_ranking.append(g_obj)
        groups_by_id[gid] = g_obj

        # Consolidate General Balances for this group
        group_gen_raw = {}
        for cd in codes:
            if cd in cias_balances_general:
                for acc_code, acc_val in cias_balances_general[cd].items():
                    group_gen_raw[acc_code] = group_gen_raw.get(acc_code, 0.0) + acc_val
        groups_balances_general[gid] = compute_hierarchical_rollup(group_gen_raw, is_subramo=False)

        # Consolidate Subramo Balances for this group
        groups_balances_subramos[gid] = {}
        g_subramos_list = []
        for scat in subramos_catalog:
            scod = scat['cod']
            group_sub_raw = {}
            for cd in codes:
                if cd in cias_balances_subramos and scod in cias_balances_subramos[cd]:
                    for acc_code, acc_val in cias_balances_subramos[cd][scod].items():
                        group_sub_raw[acc_code] = group_sub_raw.get(acc_code, 0.0) + acc_val
            if group_sub_raw:
                sub_rollup = compute_hierarchical_rollup(group_sub_raw, is_subramo=True)
                groups_balances_subramos[gid][scod] = sub_rollup
                sub_emit = sub_rollup.get('_net_emit', sub_rollup.get('5.01.01.00.00.00.00.00', 0.0))
                sub_sin = sub_rollup.get('4.01.01.00.00.00.00.00', 0.0) + sub_rollup.get('4.01.02.00.00.00.00.00', 0.0)
                if sub_emit > 0:
                    g_subramos_list.append({
                        "cod_subramo": scod,
                        "desc_subramo": scat['desc'],
                        "primas_emitidas": sub_emit,
                        "siniestros": sub_sin,
                        "loss_ratio": round((sub_sin / sub_emit * 100.0), 2) if sub_emit > 0 else 0.0
                    })
        g_subramos_list.sort(key=lambda x: x['primas_emitidas'], reverse=True)
        g_obj["subramos"] = g_subramos_list

    groups_ranking.sort(key=lambda x: x['primas_emitidas'], reverse=True)
    for i, g in enumerate(groups_ranking, 1):
        g['rank'] = i

    RAMOS_TAXONOMY = {
        "patrimoniales": {
            "id": "patrimoniales",
            "name": "Daños Patrimoniales",
            "icon": "fa-car",
            "ramos": {
                "auto": {
                    "id": "auto",
                    "name": "Automotores y Motos",
                    "subramos": ["1.030.01", "1.030.02", "1.030.03", "1.180.01", "1.180.02", "1.180.03"]
                },
                "incendio_comb": {
                    "id": "incendio_comb",
                    "name": "Incendio y Combinados",
                    "subramos": ["1.010.99", "1.020.01", "1.020.02", "1.020.99"]
                },
                "rc": {
                    "id": "rc",
                    "name": "Responsabilidad Civil",
                    "subramos": ["1.080.01", "1.080.02", "1.080.03", "1.080.99"]
                },
                "caucion_credito": {
                    "id": "caucion_credito",
                    "name": "Caución y Créditos",
                    "subramos": ["1.100.01", "1.100.99", "1.110.01", "1.110.02", "1.110.99"]
                },
                "agro": {
                    "id": "agro",
                    "name": "Agropecuario y Forestal",
                    "subramos": ["1.070.01", "1.070.02", "1.070.99"]
                },
                "transporte": {
                    "id": "transporte",
                    "name": "Transporte y Vías",
                    "subramos": ["1.040.99", "1.120.99", "1.130.01", "1.130.99", "1.140.99", "1.150.99"]
                },
                "tecnico_otros": {
                    "id": "tecnico_otros",
                    "name": "Seguro Técnico, Robo y Varios",
                    "subramos": ["1.090.99", "1.160.99", "1.170.01", "1.170.02", "1.170.03", "1.170.99"]
                }
            }
        },
        "art": {
            "id": "art",
            "name": "Riesgos del Trabajo (ART)",
            "icon": "fa-helmet-safety",
            "ramos": {
                "art_total": {
                    "id": "art_total",
                    "name": "Riesgos del Trabajo (ART)",
                    "subramos": ["1.050.01", "1.050.99"]
                }
            }
        },
        "personas": {
            "id": "personas",
            "name": "Seguros de Personas",
            "icon": "fa-heart-pulse",
            "ramos": {
                "vida": {
                    "id": "vida",
                    "name": "Seguros de Vida",
                    "subramos": ["2.030.01", "2.030.02", "2.030.03", "2.030.04", "2.030.05"]
                },
                "ap": {
                    "id": "ap",
                    "name": "Accidentes Personales",
                    "subramos": ["2.010.01", "2.010.02"]
                },
                "salud": {
                    "id": "salud",
                    "name": "Salud",
                    "subramos": ["2.020.01", "2.020.02"]
                },
                "sepelio": {
                    "id": "sepelio",
                    "name": "Sepelio",
                    "subramos": ["2.050.01", "2.050.02"]
                }
            }
        },
        "retiro": {
            "id": "retiro",
            "name": "Retiro y Rentas",
            "icon": "fa-piggy-bank",
            "ramos": {
                "retiro_puro": {
                    "id": "retiro_puro",
                    "name": "Seguros de Retiro",
                    "subramos": ["2.060.01", "2.060.02"]
                },
                "rentas": {
                    "id": "rentas",
                    "name": "Rentas Previsionales y ART",
                    "subramos": ["2.070.01", "2.070.02"]
                }
            }
        }
    }

    # ----------------------------------------------------
    # COMPARATIVE MARKET DATASET (2026-2 vs 2025-2)
    # ----------------------------------------------------
    print("Building comparative subramos dataset (2026 vs 2025)...")
    cias_comparative_subramos = {}
    groups_comparative_subramos = {}
    market_comparative_subramos = {}

    mdb_2026 = r"g:\Mi unidad\IA\Sinensup\2026-2.mdb"
    mdb_2025 = r"g:\Mi unidad\IA\Sinensup\2025-2.mdb"

    if os.path.exists(mdb_2026) and os.path.exists(mdb_2025):
        try:
            conn26 = pyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_2026};")
            df_c26 = pd.read_sql("SELECT cod_cia, cod_subramo, cod_cuenta, importe FROM Balance WHERE cod_subramo IS NOT NULL AND cod_subramo <> ''", conn26)
            conn26.close()

            conn25 = pyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_2025};")
            df_c25 = pd.read_sql("SELECT cod_cia, cod_subramo, cod_cuenta, importe FROM Balance WHERE cod_subramo IS NOT NULL AND cod_subramo <> ''", conn25)
            conn25.close()

            def process_comp_df(df_in):
                df_c = df_in.copy()
                df_c['cod_cia'] = df_c['cod_cia'].astype(str).str.strip().str.zfill(4)
                df_c['cod_subramo'] = df_c['cod_subramo'].astype(str).str.strip()
                df_c['cod_cuenta'] = df_c['cod_cuenta'].astype(str).str.strip()
                df_c['importe'] = df_c['importe'].fillna(0.0)

                # Primas Directas Netas y Adicionales (Emisión Directa Neta Total)
                p_dir_01 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.01.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                p_dir_99 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.01.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                der_01 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.02.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                der_99 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.02.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                rec_02 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.03.02.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                rec_99 = df_c[df_c['cod_cuenta'] == '5.01.01.01.01.03.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                a_dir_01 = df_c[df_c['cod_cuenta'] == '4.01.04.04.04.01.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                a_dir_99 = df_c[df_c['cod_cuenta'] == '4.01.04.04.04.01.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                a_rec_01 = df_c[df_c['cod_cuenta'] == '4.01.04.04.04.02.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                a_rec_99 = df_c[df_c['cod_cuenta'] == '4.01.04.04.04.02.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                # Siniestros Netos
                s_pag_01 = df_c[df_c['cod_cuenta'] == '4.01.01.01.01.01.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_pag_99 = df_c[df_c['cod_cuenta'] == '4.01.01.01.01.99.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_pend_01 = df_c[df_c['cod_cuenta'] == '4.01.01.01.06.01.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_liq_01 = df_c[df_c['cod_cuenta'] == '4.01.01.01.04.01.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_liq_99 = df_c[df_c['cod_cuenta'] == '4.01.01.01.04.99.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_resc = df_c[df_c['cod_cuenta'] == '4.01.02.00.00.00.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                
                s_pend_ant_01 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.06.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_pend_ant_99 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.06.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_recup_reag_01 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.01.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_recup_reag_99 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.01.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_recup_terc_01 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.03.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                s_recup_terc_99 = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.03.99.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                # Gastos
                g_prod = df_c[df_c['cod_cuenta'].str.startswith('4.01.06')].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                g_expl = df_c[df_c['cod_cuenta'].str.startswith('4.01.07')].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                # Devengadas
                rva_ej = df_c[df_c['cod_cuenta'] == '4.01.05.05.01.01.01.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                rva_ant = df_c[df_c['cod_cuenta'] == '5.01.04.04.04.12.01.01'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                p_ced = df_c[df_c['cod_cuenta'] == '4.01.03.03.03.01.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                # Res Tecnico
                ing_tec = df_c[df_c['cod_cuenta'] == '5.01.00.00.00.00.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                egr_tec = df_c[df_c['cod_cuenta'] == '4.01.00.00.00.00.00.00'].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()

                res_df = pd.DataFrame({
                    'p_dir_01': p_dir_01, 'p_dir_99': p_dir_99,
                    'der_01': der_01, 'der_99': der_99,
                    'rec_02': rec_02, 'rec_99': rec_99,
                    'a_dir_01': a_dir_01, 'a_dir_99': a_dir_99,
                    'a_rec_01': a_rec_01, 'a_rec_99': a_rec_99,
                    's_pag_01': s_pag_01, 's_pag_99': s_pag_99, 's_pend_01': s_pend_01, 's_liq_01': s_liq_01, 's_liq_99': s_liq_99, 's_resc': s_resc,
                    's_pend_ant_01': s_pend_ant_01, 's_pend_ant_99': s_pend_ant_99, 's_recup_reag_01': s_recup_reag_01, 's_recup_reag_99': s_recup_reag_99,
                    's_recup_terc_01': s_recup_terc_01, 's_recup_terc_99': s_recup_terc_99,
                    'g_prod': g_prod, 'g_expl': g_expl, 'rva_ej': rva_ej, 'rva_ant': rva_ant, 'p_ced': p_ced,
                    'ing_tec': ing_tec, 'egr_tec': egr_tec
                }).fillna(0.0)

                res_df['emit'] = (res_df['p_dir_01'] + res_df['p_dir_99'] + res_df['der_01'] + res_df['der_99'] + res_df['rec_02'] + res_df['rec_99']) - (res_df['a_dir_01'] + res_df['a_dir_99'] + res_df['a_rec_01'] + res_df['a_rec_99'])
                res_df['sin'] = (res_df['s_pag_01'] + res_df['s_pag_99'] + res_df['s_pend_01'] + res_df['s_liq_01'] + res_df['s_liq_99'] + res_df['s_resc']) - (res_df['s_pend_ant_01'] + res_df['s_pend_ant_99'] + res_df['s_recup_reag_01'] + res_df['s_recup_reag_99'] + res_df['s_recup_terc_01'] + res_df['s_recup_terc_99'])
                res_df['gtos'] = res_df['g_prod'] + res_df['g_expl']
                res_df['dev'] = res_df['emit'] - res_df['p_ced'] - (res_df['rva_ej'] - res_df['rva_ant'])
                res_df['res_tec'] = res_df['ing_tec'] - res_df['egr_tec']
                return res_df[['emit', 'sin', 'gtos', 'dev', 'res_tec']]

            p26 = process_comp_df(df_c26)
            p25 = process_comp_df(df_c25)

            merged_comp = p26.merge(p25, on=['cod_cia', 'cod_subramo'], how='outer', suffixes=('_26', '_25')).fillna(0.0)

            for (cod_cia, cod_sub), r in merged_comp.iterrows():
                if cod_cia not in cias_comparative_subramos:
                    cias_comparative_subramos[cod_cia] = {}
                cias_comparative_subramos[cod_cia][cod_sub] = {
                    'e26': round(float(r['emit_26']), 2),
                    'e25': round(float(r['emit_25']), 2),
                    's26': round(float(r['sin_26']), 2),
                    's25': round(float(r['sin_25']), 2),
                    'g26': round(float(r['gtos_26']), 2),
                    'g25': round(float(r['gtos_25']), 2),
                    'd26': round(float(r['dev_26']), 2),
                    'd25': round(float(r['dev_25']), 2),
                    't26': round(float(r['res_tec_26']), 2),
                    't25': round(float(r['res_tec_25']), 2)
                }

            # Group rollup
            for gdef in GROUPS_DEFINITIONS:
                gid = gdef['id']
                g_subs = {}
                for m_cod in gdef['codes']:
                    m_data = cias_comparative_subramos.get(m_cod, {})
                    for scod, sval in m_data.items():
                        if scod not in g_subs:
                            g_subs[scod] = {'e26': 0.0, 'e25': 0.0, 's26': 0.0, 's25': 0.0, 'g26': 0.0, 'g25': 0.0, 'd26': 0.0, 'd25': 0.0, 't26': 0.0, 't25': 0.0}
                        for k in g_subs[scod]:
                            g_subs[scod][k] = round(g_subs[scod][k] + sval[k], 2)
                groups_comparative_subramos[gid] = g_subs

            # Market rollup
            for cod_cia, c_subs in cias_comparative_subramos.items():
                for scod, sval in c_subs.items():
                    if scod not in market_comparative_subramos:
                        market_comparative_subramos[scod] = {'e26': 0.0, 'e25': 0.0, 's26': 0.0, 's25': 0.0, 'g26': 0.0, 'g25': 0.0, 'd26': 0.0, 'd25': 0.0, 't26': 0.0, 't25': 0.0}
                    for k in market_comparative_subramos[scod]:
                        market_comparative_subramos[scod][k] = round(market_comparative_subramos[scod][k] + sval[k], 2)

            print(f"Comparative subramos ready: {len(cias_comparative_subramos)} cias, {len(groups_comparative_subramos)} groups, {len(market_comparative_subramos)} subramos.")
        except Exception as e:
            print(f"Error building comparative subramos dataset: {e}")

    payload = {
        "periodo": str(df_raw['periodo'].iloc[0]),
        "periodo_comparativo": "2025-2",
        "default_inflation_rate": 45.0,
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
        "companies_by_code": companies_dict,
        "groups": groups_ranking,
        "groups_by_id": groups_by_id,
        "groups_balances_general": groups_balances_general,
        "groups_balances_subramos": groups_balances_subramos,
        "ramos_taxonomy": RAMOS_TAXONOMY,
        "plan_de_cuentas": plan_de_cuentas,
        "subramos_catalog": subramos_catalog,
        "market_balances_general": market_balances_general,
        "market_balances_subramos": market_balances_subramos,
        "segment_balances_general": segment_balances_general,
        "segment_balances_subramos": segment_balances_subramos,
        "cias_balances_general": cias_balances_general,
        "cias_balances_subramos": cias_balances_subramos,
        "cias_comparative_subramos": cias_comparative_subramos,
        "groups_comparative_subramos": groups_comparative_subramos,
        "market_comparative_subramos": market_comparative_subramos
    }

    out_json = r"g:\Mi unidad\IA\Sinensup\data_sinensup.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"data_sinensup.json generated successfully: {len(payload['companies'])} companies, {len(groups_ranking)} groups ({os.path.getsize(out_json):,} bytes)")
    return out_json

if __name__ == '__main__':
    build_complete_dataset()

