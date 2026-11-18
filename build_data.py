import json
import os
import pandas as pd
import numpy as np
from db_engine import BASE_DIR, get_balance_data, load_data_from_mdb
from insurance_kpis import (
    _extract_ssn_technical_components,
    get_period_months,
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
    current_period_early = str(df_raw['periodo'].iloc[0]).strip() if not df_raw.empty else ''
    period_months = get_period_months(current_period_early)
    annual_factor = 12.0 / float(period_months) if period_months > 0 else 1.0

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

    sub_clean = df_raw[
        (df_raw['desc_subramo'] != '') & (df_raw['desc_subramo'].notna()) & (df_raw['cod_subramo'] != '3.000.99')
    ].copy()
    sub_clean['macro_prod'] = sub_clean['cod_subramo'].apply(get_macro_product)

    macro_productos = {}
    tot_prod_p = 0.0
    tot_prod_d = 0.0
    for k in ['patrimoniales', 'art', 'personas', 'retiro']:
        k_df = sub_clean[sub_clean['macro_prod'] == k]
        comp_k = _extract_ssn_technical_components(k_df, use_exact=False)
        p_val = comp_k['primas_emit']
        d_val = comp_k['primas_dev']
        s_val = comp_k['siniestros_dev'] + comp_k['rescates']
        base_p = d_val if d_val > 0 else p_val
        tot_prod_p += p_val
        tot_prod_d += d_val
        sin_pct = (s_val / base_p * 100.0) if base_p > 0 else 0.0

        macro_productos[k] = {
            "primas": round(p_val, 2),
            "devengadas": round(d_val, 2),
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
    tot_base_p = tot_prod_d if tot_prod_d > 0 else tot_prod_p

    macro_productos['total'] = {
        "primas": round(tot_prod_p, 2),
        "devengadas": round(tot_prod_d, 2),
        "siniestros": round(tot_prod_s, 2),
        "siniestralidad": round((tot_prod_s / tot_base_p * 100), 1) if tot_base_p > 0 else 0.0
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
        base_primas = tot_dev if tot_dev > 0 else (tot_emit if tot_emit > 0 else 0.0)
        has_primas = base_primas > 0
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
        tot_pasivo = float(df_sub['pasivo'].sum())
        tot_deudas = float(df_sub['deudas'].sum())
        tot_prev = float(df_sub['previsiones'].sum())
        tot_pn = float(df_sub['patrimonio_neto'].sum())
        tot_activo = float(df_sub['activo'].sum())
        tot_premios = float(df_sub['premios_a_cobrar'].sum())
        res_fin_sobre_pn = (tot_res_fin / tot_pn * 100.0) if tot_pn > 0 else ((tot_res_fin / abs(tot_pn) * 100.0) if tot_pn < 0 else 0.0)

        return {
            'entidades': int(len(df_sub)),
            'primas_emitidas': tot_emit,
            'primas_devengadas': tot_dev,
            'loss_ratio': round((tot_sin / base_primas * 100.0) if has_primas else 0.0, 2),
            'comm_ratio': round((tot_prod / base_primas * 100.0) if has_primas else 0.0, 2),
            'exp_ratio': round((tot_expl / base_primas * 100.0) if has_primas else 0.0, 2),
            'combined_ratio': round(((tot_sin + tot_gtos_op) / base_primas * 100.0) if has_primas else 0.0, 2),
            'retencion_ratio': round(max(0.0, min(100.0, ((tot_emit - float(df_sub['primas_cedidas'].sum())) / tot_emit * 100.0))) if tot_emit > 0 else 100.0, 2),
            'cesion_ratio': round((float(df_sub['primas_cedidas'].sum()) / tot_emit * 100.0) if tot_emit > 0 else 0.0, 2),
            'roi_inversiones': round((tot_res_fin / tot_inv * 100.0) if tot_inv > 0 else 0.0, 2),
            'densidad_inversiones': round((tot_inv / tot_activo * 100.0) if tot_activo > 0 else 0.0, 2),
            'cobertura_reservas': round(((tot_inv + tot_inm + tot_disp) / tot_ct) if tot_ct > 0 else 0.0, 2),
            'apalancamiento': round(((base_primas * annual_factor) / tot_pn) if tot_pn > 0 else (-1.0 if tot_pn < 0 else 0.0), 2),
            'calidad_cartera': round((tot_premios / (tot_emit * annual_factor) * 100.0) if tot_emit > 0 else 0.0, 2),
            'roe': round((tot_res_neto / tot_pn * 100.0) if tot_pn > 0 else ((tot_res_neto / abs(tot_pn) * 100.0) if tot_pn < 0 else 0.0), 2),
            'res_fin_sobre_pn': round(res_fin_sobre_pn, 2),
            'roa': round((tot_res_neto / tot_activo * 100.0) if tot_activo > 0 else 0.0, 2),
            'margen_neto': round((tot_res_neto / base_primas * 100.0) if has_primas else 0.0, 2),
            'pasivo': tot_pasivo,
            'deudas': tot_deudas,
            'previsiones': tot_prev,
            'patrimonio_neto': tot_pn,
            'activo': tot_activo,
            'inversiones': tot_inv,
            'disponibilidades': tot_disp,
            'inmuebles': tot_inm,
            'compromisos_tecnicos': tot_ct,
            'premios_a_cobrar': tot_premios,
            'siniestros': float(df_sub['siniestros'].sum()),
            'rescates': float(df_sub['rescates'].sum()),
            'gtos_produccion': tot_prod,
            'gtos_explotacion': tot_expl,
            'gtos_operativos': tot_gtos_op,
            'reaseguro_activo_neto': float(df_sub['reaseguro_activo_neto'].sum()),
            'primas_cedidas': float(df_sub['primas_cedidas'].sum()),
            'var_reservas': float(df_sub['var_reservas'].sum()),
            'otros_tec_neto': float(df_sub['otros_tec_neto'].sum()),
            'op_extraordinarias': float(df_sub['op_extraordinarias'].sum()),
            'impuesto_ganancias': float(df_sub['impuesto_ganancias'].sum()),
            'rescates_ratio': round((float(df_sub['rescates'].sum()) / base_primas * 100.0) if has_primas else 0.0, 2),
            'margen_tecnico': round((tot_res_tec / base_primas * 100.0) if has_primas else 0.0, 2),
            'resultado_tecnico': tot_res_tec,
            'resultado_financiero': tot_res_fin,
            'resultado_neto': tot_res_neto,
            'sin_base_primas': bool(not has_primas),
            'patrimonio_negativo': bool(tot_pn <= 0),
            'sin_compromisos_tecnicos': bool(tot_ct <= 0)
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
            comp_sub = _extract_ssn_technical_components(raw_dict, use_exact=False)
            rolled['_net_emit'] = round(comp_sub['primas_emit'], 2)
            rolled['_net_ced'] = round(comp_sub['cesion_neta'], 2)
            rolled['_net_anul'] = round(comp_sub['anulaciones'], 2)
            rolled['_net_dev'] = round(comp_sub['primas_dev'], 2)
            rolled['_net_sin'] = round(comp_sub['siniestros_dev'] + comp_sub['rescates'], 2)
            rolled['_net_gp'] = round(comp_sub['gtos_prod'], 2)
            rolled['_net_ge'] = round(comp_sub['gtos_expl'], 2)
            rolled['_res_tec'] = round(
                float(rolled.get('5.01.00.00.00.00.00.00', 0.0)) - float(rolled.get('4.01.00.00.00.00.00.00', 0.0)),
                2
            )

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
            "consolidation_mode": "vpp_parent",
            "parent_code": "0224",
            "description": "Sancor Seguros, Prevención ART, Prevención Retiro"
        },
        {
            "id": "federacion_patronal",
            "name": "Grupo Federación Patronal",
            "short_name": "Federación Patronal",
            "codes": ["0726", "0425"],
            "consolidation_mode": "additive",
            "description": "Federación Patronal Seguros (PM+ART), Federación Patronal Retiro"
        },
        {
            "id": "provincia",
            "name": "Grupo Provincia",
            "short_name": "Provincia",
            "codes": ["0499", "0621", "0532"],
            "consolidation_mode": "sister_cross_vpp",
            "cross_vpp_holders": ["0499"],
            "description": "Provincia Seguros, Provincia ART, Provincia Vida"
        },
        {
            "id": "san_cristobal",
            "name": "Grupo San Cristóbal",
            "short_name": "San Cristóbal",
            "codes": ["0192", "0620", "0442"],
            "consolidation_mode": "vpp_parent",
            "parent_code": "0192",
            "description": "San Cristóbal Seguros, Asociart ART, San Cristóbal Retiro",
            "member_labels": {
                "0192": "San Cristóbal Seguros",
                "0620": "Asociart ART",
                "0442": "San Cristóbal Retiro"
            }
        },
        {
            "id": "la_segunda",
            "name": "Grupo Asegurador La Segunda",
            "short_name": "La Segunda",
            "codes": ["0317", "0618", "0117", "0436"],
            "consolidation_mode": "vpp_parent",
            "parent_code": "0317",
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
            "codes": ["0228", "0039", "0692", "0541"],
            "merged_codes": ["0039"],
            "description": "Zurich Argentina, Zurich Santander, Zurich International Life",
            "member_labels": {
                "0228": "Zurich Argentina",
                "0039": "Zurich Aseguradora (fusionada)",
                "0692": "Zurich Santander",
                "0541": "Zurich International Life"
            }
        },
        {
            "id": "experta_werthein",
            "name": "Grupo Experta / Werthein",
            "short_name": "Experta / Werthein",
            "codes": ["0880", "0616", "0419"],
            "description": "Experta Seguros, Experta ART, La Estrella Retiro",
            "member_labels": {
                "0880": "Experta Seguros",
                "0616": "Experta ART",
                "0419": "La Estrella Retiro"
            }
        },
        {
            "id": "mercantil_andina",
            "name": "Grupo Mercantil Andina",
            "short_name": "Mercantil Andina",
            "codes": ["0116", "0959"],
            "consolidation_mode": "vpp_parent",
            "parent_code": "0116",
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
            "merged_codes": ["0443"],
            "description": "Seguros Galicia, Galicia Seguros, Galicia Retiro",
            "member_labels": {
                "0025": "Seguros Galicia",
                "0589": "Galicia Seguros",
                "0443": "Galicia Seguros de Retiro (fusionada)",
                "0426": "Galicia Retiro"
            }
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
            "codes": ["0515", "0534"],
            "description": "Nación Seguros, Nación Retiro",
            "member_labels": {
                "0515": "Nación Seguros",
                "0534": "Nación Retiro"
            }
        },
        {
            "id": "mapfre",
            "name": "Grupo Mapfre",
            "short_name": "Mapfre",
            "codes": ["0213", "0699"],
            "description": "Mapfre Seguros, Mapfre Vida",
            "member_labels": {
                "0213": "Mapfre Seguros",
                "0699": "Mapfre Vida"
            }
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
            "codes": ["0878", "0619"],
            "description": "Galeno Seguros, Galeno ART",
            "member_labels": {
                "0878": "Galeno Seguros",
                "0619": "Galeno ART"
            }
        }
    ]

    total_mkt_emit = float(macro_entidades['total_mercado_emitidas'])
    total_mkt_dev = float(macro_entidades['total_mercado_devengadas'])

    groups_ranking = []
    groups_by_id = {}
    groups_balances_general = {}
    groups_balances_subramos = {}
    active_codes_by_gid = {}

    def apply_account_delta(acc_dict, delta_tracker, leaf_code, delta):
        delta = round(float(delta), 2)
        if delta == 0.0:
            return
        curr = leaf_code
        visited = set()
        while curr and curr in plan_de_cuentas and curr not in visited:
            visited.add(curr)
            acc_dict[curr] = round(float(acc_dict.get(curr, 0.0)) + delta, 2)
            delta_tracker[curr] = round(float(delta_tracker.get(curr, 0.0)) + delta, 2)
            curr = plan_de_cuentas[curr].get('padre_codigo', '')

    for gdef in GROUPS_DEFINITIONS:
        gid = gdef['id']
        gname = gdef['name']
        codes = gdef['codes']

        # Collect member companies that exist in dataset
        members = []
        tot_emit = 0.0
        tot_reaseg = 0.0
        tot_cedidas = 0.0
        tot_dev = 0.0
        tot_var = 0.0
        tot_sin = 0.0
        tot_rescates = 0.0
        tot_gtos_prod = 0.0
        tot_gtos_exp = 0.0
        tot_otros_tec = 0.0
        tot_op_ext = 0.0
        tot_imp_gan = 0.0
        tot_res_tec = 0.0
        tot_res_fin = 0.0
        tot_res_neto = 0.0
        tot_activo = 0.0
        tot_inv = 0.0
        tot_disp = 0.0
        tot_cred = 0.0
        tot_premios = 0.0
        tot_inm = 0.0
        tot_bu = 0.0
        tot_otros_act = 0.0
        tot_pasivo = 0.0
        tot_deudas = 0.0
        tot_comp_tec = 0.0
        tot_prev = 0.0
        tot_pn = 0.0
        tot_vpp_res = 0.0
        tot_vpp_act = 0.0

        active_codes = []
        for cd in codes:
            if cd in companies_dict:
                active_codes.append(cd)
                c = companies_dict[cd]
                members.append(c)
                tot_emit += float(c.get('primas_emitidas', 0.0))
                tot_reaseg += float(c.get('reaseguro_activo_neto', 0.0))
                tot_cedidas += float(c.get('primas_cedidas', 0.0))
                tot_dev += float(c.get('primas_devengadas', 0.0))
                tot_var += float(c.get('var_reservas', 0.0))
                tot_sin += float(c.get('siniestros', 0.0))
                tot_rescates += float(c.get('rescates', 0.0))
                tot_gtos_prod += float(c.get('gtos_produccion', 0.0))
                tot_gtos_exp += float(c.get('gtos_explotacion', 0.0))
                tot_otros_tec += float(c.get('otros_tec_neto', 0.0))
                tot_op_ext += float(c.get('op_extraordinarias', 0.0))
                tot_imp_gan += float(c.get('impuesto_ganancias', 0.0))
                tot_res_tec += float(c.get('resultado_tecnico', 0.0))
                tot_res_fin += float(c.get('resultado_financiero', 0.0))
                tot_res_neto += float(c.get('resultado_neto', 0.0))
                tot_activo += float(c.get('activo', 0.0))
                tot_inv += float(c.get('inversiones', 0.0))
                tot_disp += float(c.get('disponibilidades', 0.0))
                tot_cred += float(c.get('creditos', 0.0))
                tot_premios += float(c.get('premios_a_cobrar', 0.0))
                tot_inm += float(c.get('inmuebles', 0.0))
                tot_bu += float(c.get('bienes_uso', 0.0))
                tot_otros_act += float(c.get('otros_activos', 0.0))
                tot_pasivo += float(c.get('pasivo', 0.0))
                tot_deudas += float(c.get('deudas', 0.0))
                tot_comp_tec += float(c.get('compromisos_tecnicos', 0.0))
                tot_prev += float(c.get('previsiones', 0.0))
                tot_pn += float(c.get('patrimonio_neto', 0.0))
                tot_vpp_res += float(c.get('vpp_resultado', 0.0))
                tot_vpp_act += float(c.get('vpp_activo', 0.0))

        if len(members) == 0:
            continue

        active_codes_by_gid[gid] = active_codes

        # Raw aggregated general balance across active group members
        group_gen_raw = {}
        for cd in active_codes:
            if cd in cias_balances_general:
                for acc_code, acc_val in cias_balances_general[cd].items():
                    if not str(acc_code).startswith('_'):
                        group_gen_raw[acc_code] = round(group_gen_raw.get(acc_code, 0.0) + float(acc_val), 2)

        # RT 21 FACPCE / SSN Intra-group VPP consolidation adjustments
        elim_deltas = {}
        vpp_elim_by_member = {cd: 0.0 for cd in active_codes}
        elim_act = 0.0
        elim_res = 0.0
        part_terc_pas = 0.0
        part_terc_res = 0.0
        effective_mode = "additive"
        cons_mode_cfg = gdef.get("consolidation_mode", "additive")
        parent_code = gdef.get("parent_code")

        if cons_mode_cfg == "vpp_parent" and parent_code in active_codes and len(active_codes) > 1:
            effective_mode = "vpp_parent"
            subs_codes = [cd for cd in active_codes if cd != parent_code]

            # 1. Eliminate subsidiaries' Patrimonio Neto (3.*) so chapter 3 equals parent's PN
            for cd in subs_codes:
                for acc_code, acc_val in cias_balances_general.get(cd, {}).items():
                    if str(acc_code).startswith('3.') and not str(acc_code).startswith('_'):
                        val = round(float(acc_val), 2)
                        group_gen_raw[acc_code] = round(group_gen_raw.get(acc_code, 0.0) - val, 2)
                        elim_deltas[acc_code] = round(elim_deltas.get(acc_code, 0.0) - val, 2)

            # 2. Eliminate intra-group VPP equity holdings (1.02.01.02.02.02 & 1.02.01.02.01.02)
            ge_sin = sum(float(cias_balances_general.get(cd, {}).get('1.02.01.02.02.02.00.00', 0.0)) for cd in active_codes)
            ge_con = sum(float(cias_balances_general.get(cd, {}).get('1.02.01.02.01.02.00.00', 0.0)) for cd in active_codes)
            pn_subs = sum(float(companies_dict[cd]['patrimonio_neto']) for cd in subs_codes)
            elim_act = round(min(ge_sin + ge_con, max(0.0, pn_subs)), 2)
            elim_sin = round(min(ge_sin, elim_act), 2)
            elim_con = round(elim_act - elim_sin, 2)
            if elim_sin != 0.0:
                apply_account_delta(group_gen_raw, elim_deltas, '1.02.01.02.02.02.00.00', -elim_sin)
            if elim_con != 0.0:
                apply_account_delta(group_gen_raw, elim_deltas, '1.02.01.02.01.02.00.00', -elim_con)

            # 3. Minority interest in subsidiaries' equity -> 2.04 Participación de Terceros en Soc. Controladas
            part_terc_pas = round(pn_subs - elim_act, 2)
            if abs(part_terc_pas) >= 0.01:
                apply_account_delta(group_gen_raw, elim_deltas, '2.04.04.04.04.01.00.00', part_terc_pas)

            # 4. Eliminate intra-group VPP result (5.02) & recognize minority interest in P&L (4.03)
            rn_subs = sum(float(companies_dict[cd]['resultado_neto']) for cd in subs_codes)
            alpha = (elim_act / pn_subs) if pn_subs > 0 else 1.0
            ten_acc_grp = sum(float(cias_balances_general.get(cd, {}).get('5.02.03.03.01.02.00.00', 0.0)) for cd in active_codes)
            ten_otr_grp = sum(float(cias_balances_general.get(cd, {}).get('5.02.03.03.02.01.00.00', 0.0)) for cd in active_codes)

            if abs(ten_acc_grp) < 1000.0 and abs(ten_otr_grp) > 0 and (
                rn_subs == 0 or (ten_otr_grp * rn_subs > 0 and abs(ten_otr_grp) <= abs(rn_subs) * 1.05)
            ):
                elim_res = round(ten_otr_grp, 2)
                apply_account_delta(group_gen_raw, elim_deltas, '5.02.03.03.02.01.00.00', -elim_res)
                for cd in active_codes:
                    vpp_elim_by_member[cd] = float(cias_balances_general.get(cd, {}).get('5.02.03.03.02.01.00.00', 0.0))
            else:
                elim_res = round(alpha * rn_subs, 2)
                res_leaf = '5.02.03.03.01.02.00.00' if abs(ten_acc_grp) >= abs(ten_otr_grp) else '5.02.03.03.02.01.00.00'
                apply_account_delta(group_gen_raw, elim_deltas, res_leaf, -elim_res)
                vpp_elim_by_member[parent_code] = elim_res

            part_terc_res = round(rn_subs - elim_res, 2)
            if abs(part_terc_res) >= 0.01:
                apply_account_delta(group_gen_raw, elim_deltas, '4.03.03.03.03.01.00.00', part_terc_res)

            # Update group-level totals so Activo == Pasivo + PN and RN == RN_parent
            tot_activo = round(tot_activo - elim_act, 2)
            tot_inv = round(tot_inv - elim_act, 2)
            tot_pasivo = round(tot_pasivo + part_terc_pas, 2)
            tot_pn = float(companies_dict[parent_code]['patrimonio_neto'])
            tot_res_fin = round(tot_res_fin - elim_res, 2)
            tot_op_ext = round(tot_op_ext - part_terc_res, 2)
            tot_res_neto = float(companies_dict[parent_code]['resultado_neto'])

        elif cons_mode_cfg == "sister_cross_vpp" and len(active_codes) > 1:
            holders = [h for h in gdef.get("cross_vpp_holders", []) if h in active_codes]
            non_holders = [cd for cd in active_codes if cd not in holders]
            if holders and non_holders:
                effective_mode = "sister_cross_vpp"
                for h in holders:
                    h_bg = cias_balances_general.get(h, {})
                    h_sin = float(h_bg.get('1.02.01.02.02.02.00.00', 0.0))
                    h_con = float(h_bg.get('1.02.01.02.01.02.00.00', 0.0))
                    h_act = round(h_sin + h_con, 2)
                    h_tacc = float(h_bg.get('5.02.03.03.01.02.00.00', 0.0))
                    h_totr = float(h_bg.get('5.02.03.03.02.01.00.00', 0.0))
                    h_res = round(h_tacc + h_totr, 2) if h_act > 0 else 0.0

                    if h_sin != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '1.02.01.02.02.02.00.00', -h_sin)
                    if h_con != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '1.02.01.02.01.02.00.00', -h_con)
                    if h_act > 0 and h_tacc != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '5.02.03.03.01.02.00.00', -h_tacc)
                    if h_act > 0 and h_totr != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '5.02.03.03.02.01.00.00', -h_totr)
                    if h_res != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '3.05.05.05.05.02.00.00', -h_res)
                    adj_res_cap = round(h_act - h_res, 2)
                    if adj_res_cap != 0.0:
                        apply_account_delta(group_gen_raw, elim_deltas, '3.03.03.03.03.04.00.00', -adj_res_cap)

                    elim_act = round(elim_act + h_act, 2)
                    elim_res = round(elim_res + h_res, 2)
                    vpp_elim_by_member[h] = h_res

                tot_activo = round(tot_activo - elim_act, 2)
                tot_inv = round(tot_inv - elim_act, 2)
                tot_pn = round(tot_pn - elim_act, 2)
                tot_res_fin = round(tot_res_fin - elim_res, 2)
                tot_res_neto = round(tot_res_neto - elim_res, 2)

        # Residual VPP held outside the group perimeter (e.g., health/banks/foreign)
        tot_vpp_act = round(max(0.0, tot_vpp_act - elim_act), 2)
        tot_vpp_res = round(tot_vpp_res - elim_res, 2)
        if tot_vpp_act <= 0 or abs(tot_vpp_res) < 1000.0:
            tot_vpp_res = 0.0

        groups_balances_general[gid] = compute_hierarchical_rollup(group_gen_raw, is_subramo=False)

        if 'member_labels' in gdef:
            active_desc = ", ".join(gdef['member_labels'][cd] for cd in active_codes if cd in gdef['member_labels'])
            if not active_desc:
                active_desc = gdef['description']
        else:
            active_desc = gdef['description']

        base_primas = tot_dev if tot_dev > 0 else (tot_emit if tot_emit > 0 else 0.0)
        has_primas = base_primas > 0
        costo_prestacional = tot_sin + tot_rescates
        tot_gtos_op = tot_gtos_prod + tot_gtos_exp

        # Weighted consolidated ratios (identical definitions to insurance_kpis.py & compute_benchmarks)
        loss_ratio = (costo_prestacional / base_primas * 100.0) if has_primas else 0.0
        rescates_ratio = (tot_rescates / base_primas * 100.0) if has_primas else 0.0
        comm_ratio = (tot_gtos_prod / base_primas * 100.0) if has_primas else 0.0
        exp_ratio = (tot_gtos_exp / base_primas * 100.0) if has_primas else 0.0
        combined_ratio = loss_ratio + comm_ratio + exp_ratio

        roi_inv = (tot_res_fin / tot_inv * 100.0) if tot_inv > 0 else 0.0
        cobertura_reservas = (tot_inv + tot_inm + tot_disp) / tot_comp_tec if tot_comp_tec > 0 else 0.0
        apalancamiento = ((base_primas * annual_factor) / tot_pn) if tot_pn > 0 else (-1.0 if tot_pn < 0 else 0.0)
        calidad_cartera = (tot_premios / (tot_emit * annual_factor) * 100.0) if tot_emit > 0 else 0.0
        retencion_ratio = max(0.0, min(100.0, ((tot_emit - tot_cedidas) / tot_emit * 100.0))) if tot_emit > 0 else 100.0
        cesion_ratio = (tot_cedidas / tot_emit * 100.0) if tot_emit > 0 else 0.0
        densidad_inversiones = (tot_inv / tot_activo * 100.0) if tot_activo > 0 else 0.0
        roe = (tot_res_neto / tot_pn * 100.0) if tot_pn > 0 else ((tot_res_neto / abs(tot_pn) * 100.0) if tot_pn < 0 else 0.0)
        res_fin_sobre_pn = (tot_res_fin / tot_pn * 100.0) if tot_pn > 0 else ((tot_res_fin / abs(tot_pn) * 100.0) if tot_pn < 0 else 0.0)
        roa = (tot_res_neto / tot_activo * 100.0) if tot_activo > 0 else 0.0
        margen_neto = (tot_res_neto / base_primas * 100.0) if has_primas else 0.0
        margen_tecnico = (tot_res_tec / base_primas * 100.0) if has_primas else 0.0
        mkt_share = (tot_emit / total_mkt_emit * 100.0) if total_mkt_emit > 0 else 0.0
        vpp_pct_neto = round((tot_vpp_res / tot_res_neto * 100.0), 1) if (tot_vpp_res != 0 and tot_res_neto != 0) else 0.0
        vpp_pct_fin = round((tot_vpp_res / tot_res_fin * 100.0), 1) if (tot_vpp_res != 0 and tot_res_fin != 0) else 0.0

        # Members breakdown with individual share of group and consolidation metadata
        members_summary = []
        for m in members:
            m_emit = float(m.get('primas_emitidas', 0.0))
            m_cod = m['cod_cia']
            members_summary.append({
                "cod_cia": m_cod,
                "razon_social": m['razon_social'],
                "tipo_entidad": m['tipo_entidad'],
                "is_parent": bool(effective_mode == "vpp_parent" and m_cod == parent_code),
                "excluded_from_rn_pn_sum": bool(effective_mode == "vpp_parent" and m_cod != parent_code),
                "primas_emitidas": m_emit,
                "primas_devengadas": float(m.get('primas_devengadas', 0.0)),
                "siniestros": float(m.get('siniestros', 0.0)),
                "rescates": float(m.get('rescates', 0.0)),
                "resultado_tecnico": float(m.get('resultado_tecnico', 0.0)),
                "resultado_financiero": float(m.get('resultado_financiero', 0.0)),
                "resultado_financiero_consolidado": round(float(m.get('resultado_financiero', 0.0)) - float(vpp_elim_by_member.get(m_cod, 0.0)), 2),
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

        df_group_raw = df_raw[df_raw['cod_cia'].isin(active_codes)]
        elim_rows = [
            {
                'cod_cia': parent_code if effective_mode == 'vpp_parent' else active_codes[0],
                'tipo_entidad': members[0]['tipo_entidad'],
                'cod_subramo': '',
                'cod_cuenta': k,
                'desc_cuenta': plan_de_cuentas.get(k, {}).get('desc', k),
                'importe': float(v),
            }
            for k, v in elim_deltas.items() if abs(v) > 0
        ]
        df_group_cons = pd.concat([df_group_raw, pd.DataFrame(elim_rows)], ignore_index=True) if elim_rows else df_group_raw
        group_waterfall = get_company_waterfall_data(df_group_cons)
        group_investments = get_company_investments_breakdown(df_group_cons)

        g_obj = {
            "id": gid,
            "name": gname,
            "short_name": gdef['short_name'],
            "description": active_desc,
            "entities_count": len(members),
            "consolidation_mode": effective_mode,
            "parent_code": parent_code if effective_mode == "vpp_parent" else None,
            "parent_name": companies_dict[parent_code]['razon_social'] if (effective_mode == "vpp_parent" and parent_code in companies_dict) else None,
            "vpp_eliminado_resultado": round(elim_res, 2),
            "vpp_eliminado_activo": round(elim_act, 2),
            "part_terceros_pasivo": round(part_terc_pas, 2),
            "part_terceros_resultado": round(part_terc_res, 2),
            "members": members_summary,
            "primas_emitidas": round(tot_emit, 2),
            "reaseguro_activo_neto": round(tot_reaseg, 2),
            "primas_cedidas": round(tot_cedidas, 2),
            "primas_devengadas": round(tot_dev, 2),
            "var_reservas": round(tot_var, 2),
            "siniestros": round(tot_sin, 2),
            "rescates": round(tot_rescates, 2),
            "gtos_produccion": round(tot_gtos_prod, 2),
            "gtos_explotacion": round(tot_gtos_exp, 2),
            "gtos_operativos": round(tot_gtos_op, 2),
            "gastos_produccion": round(tot_gtos_prod, 2),
            "gastos_explotacion": round(tot_gtos_exp, 2),
            "otros_tec_neto": round(tot_otros_tec, 2),
            "op_extraordinarias": round(tot_op_ext, 2),
            "impuesto_ganancias": round(tot_imp_gan, 2),
            "resultado_tecnico": round(tot_res_tec, 2),
            "resultado_financiero": round(tot_res_fin, 2),
            "resultado_neto": round(tot_res_neto, 2),
            "activo": round(tot_activo, 2),
            "inversiones": round(tot_inv, 2),
            "disponibilidades": round(tot_disp, 2),
            "creditos": round(tot_cred, 2),
            "premios_a_cobrar": round(tot_premios, 2),
            "inmuebles": round(tot_inm, 2),
            "bienes_uso": round(tot_bu, 2),
            "otros_activos": round(tot_otros_act, 2),
            "pasivo": round(tot_pasivo, 2),
            "deudas": round(tot_deudas, 2),
            "compromisos_tecnicos": round(tot_comp_tec, 2),
            "previsiones": round(tot_prev, 2),
            "patrimonio_neto": round(tot_pn, 2),
            "loss_ratio": round(loss_ratio, 2),
            "rescates_ratio": round(rescates_ratio, 2),
            "comm_ratio": round(comm_ratio, 2),
            "exp_ratio": round(exp_ratio, 2),
            "combined_ratio": round(combined_ratio, 2),
            "roi_inversiones": round(roi_inv, 2),
            "cobertura_reservas": round(cobertura_reservas, 2),
            "apalancamiento": round(apalancamiento, 2),
            "calidad_cartera": round(calidad_cartera, 2),
            "retencion_ratio": round(retencion_ratio, 2),
            "cesion_ratio": round(cesion_ratio, 2),
            "densidad_inversiones": round(densidad_inversiones, 2),
            "roe": round(roe, 2),
            "res_fin_sobre_pn": round(res_fin_sobre_pn, 2),
            "roa": round(roa, 2),
            "margen_neto": round(margen_neto, 2),
            "margen_tecnico": round(margen_tecnico, 2),
            "market_share": round(mkt_share, 2),
            "vpp_resultado": round(tot_vpp_res, 2),
            "vpp_activo": round(tot_vpp_act, 2),
            "vpp_pct_neto": vpp_pct_neto,
            "vpp_pct_fin": vpp_pct_fin,
            "sin_base_primas": bool(not has_primas),
            "patrimonio_negativo": bool(tot_pn <= 0),
            "sin_compromisos_tecnicos": bool(tot_comp_tec <= 0),
            "investments": group_investments,
            "waterfall": group_waterfall
        }

        groups_ranking.append(g_obj)
        groups_by_id[gid] = g_obj

        # Consolidate Subramo Balances directly from raw subramo leaf rows (avoids double rollups)
        groups_balances_subramos[gid] = {}
        df_group_sub = sub_df[sub_df['cod_cia'].isin(active_codes)]
        for scod, grp in df_group_sub.groupby('cod_subramo'):
            raw_map = {str(k): round(float(v), 2) for k, v in grp.groupby('cod_cuenta')['importe'].sum().items()}
            groups_balances_subramos[gid][str(scod)] = compute_hierarchical_rollup(raw_map, is_subramo=True)

        g_subramos_raw = get_company_subramos(df_group_sub)
        g_obj["subramos"] = [
            {
                "cod_subramo": r['cod_subramo'],
                "desc_subramo": r['desc_subramo'],
                "primas_emitidas": r['primas'],
                "primas_devengadas": r['primas_devengadas'],
                "siniestros": r['siniestros'],
                "loss_ratio": r['siniestralidad_%']
            }
            for r in g_subramos_raw
        ]

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
    # COMPARATIVE MARKET DATASET (Current Period vs YoY Comparative)
    # ----------------------------------------------------
    current_period = str(df_raw['periodo'].iloc[0]).strip()
    if '-' in current_period:
        p_year, p_qtr = current_period.split('-', 1)
        try:
            comp_period = f"{int(p_year) - 1}-{p_qtr}"
        except ValueError:
            comp_period = "2025-2"
    else:
        comp_period = "2025-2"

    print(f"Building comparative subramos dataset ({current_period} vs {comp_period})...")
    cias_comparative_subramos = {}
    groups_comparative_subramos = {}
    market_comparative_subramos = {}
    historical_companies = {}

    mdb_prev = os.path.join(BASE_DIR, f"{comp_period}.mdb")

    if not df_raw.empty and os.path.exists(mdb_prev):
        try:
            df_c26 = df_raw[df_raw['cod_subramo'].notna() & (df_raw['cod_subramo'] != '')][
                ['cod_cia', 'cod_subramo', 'cod_cuenta', 'importe']
            ].copy()

            df_prev_raw = load_data_from_mdb(
                mdb_prev,
                columns=['cod_cia', 'razon_social', 'cod_subramo', 'cod_cuenta', 'importe']
            )
            df_prev_names = df_prev_raw[['cod_cia', 'razon_social']].copy()
            df_prev_names['cod_cia'] = df_prev_names['cod_cia'].fillna('').astype(str).str.strip().str.zfill(4)
            df_prev_names['razon_social'] = df_prev_names['razon_social'].fillna('').astype(str).str.strip()
            for _, nr in df_prev_names.drop_duplicates('cod_cia').iterrows():
                cc = nr['cod_cia']
                if cc and cc not in companies_dict and nr['razon_social']:
                    historical_companies[cc] = {"razon_social": nr['razon_social']}

            df_c25 = df_prev_raw[df_prev_raw['cod_subramo'].notna() & (df_prev_raw['cod_subramo'] != '')].copy()

            def process_comp_df(df_in):
                df_c = df_in.copy()
                df_c['cod_cia'] = df_c['cod_cia'].fillna('').astype(str).str.strip().str.zfill(4)
                df_c['cod_subramo'] = df_c['cod_subramo'].fillna('').astype(str).str.strip()
                df_c['cod_cuenta'] = df_c['cod_cuenta'].fillna('').astype(str).str.strip()
                df_c['importe'] = pd.to_numeric(df_c['importe'], errors='coerce').fillna(0.0)

                grp = df_c.groupby(['cod_cia', 'cod_subramo', 'cod_cuenta'], as_index=False)['importe'].sum()
                idx_pairs = grp[['cod_cia', 'cod_subramo']].drop_duplicates()
                res_df = pd.DataFrame(index=pd.MultiIndex.from_frame(idx_pairs))

                prefix_specs = {
                    'emit_pos': ('5.01.01.01.01.01.', '5.01.01.01.01.02.', '5.01.01.01.01.03.'),
                    'emit_neg': ('4.01.04.04.04.01.', '4.01.04.04.04.02.'),
                    'ing_primas': '5.01.01.',
                    'anul_primas': '4.01.04.',
                    'cesion_bruta': '4.01.03.',
                    'recup_cesion': '5.01.02.',
                    'var_cargo': '4.01.05.',
                    'var_lib': ('5.01.04.04.04.11.', '5.01.04.04.04.12.', '5.01.04.04.04.13.'),
                    'tot_recup': '5.01.04.',
                    'part_util': '5.01.04.04.04.08.',
                    'sin_cargo': '4.01.01.',
                    'rescates': '4.01.02.',
                    'gtos_prod_cargo': '4.01.06.',
                    'recup_gtos_prod': '5.01.03.',
                    'gtos_expl': ('4.01.07.', '4.01.60.'),
                    'ing_tec': '5.01.',
                    'egr_tec': '4.01.',
                }
                for col_name, pfx in prefix_specs.items():
                    s = grp[grp['cod_cuenta'].str.startswith(pfx)].groupby(['cod_cia', 'cod_subramo'])['importe'].sum()
                    res_df[col_name] = s
                res_df = res_df.fillna(0.0)

                res_df['emit'] = res_df['emit_pos'] - res_df['emit_neg']
                reaseg_neto = (res_df['ing_primas'] - res_df['anul_primas']) - res_df['emit']
                cesion_neta = res_df['cesion_bruta'] - res_df['recup_cesion']
                var_comp_tec = res_df['var_cargo'] - res_df['var_lib']
                res_df['dev'] = res_df['emit'] + reaseg_neto - cesion_neta - var_comp_tec

                recup_sin = res_df['tot_recup'] - res_df['var_lib'] - res_df['part_util']
                siniestros_dev = res_df['sin_cargo'] - recup_sin
                res_df['sin'] = siniestros_dev + res_df['rescates']

                gtos_prod = res_df['gtos_prod_cargo'] - res_df['recup_gtos_prod'] - res_df['part_util']
                res_df['gtos'] = gtos_prod + res_df['gtos_expl']
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

            # Group rollup (homogeneous perimeter: active 2026-3 codes + explicitly merged predecessors)
            for gdef in GROUPS_DEFINITIONS:
                gid = gdef['id']
                g_subs = {}
                comp_codes = list(dict.fromkeys(active_codes_by_gid.get(gid, []) + gdef.get('merged_codes', [])))
                for m_cod in comp_codes:
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
        "periodo": current_period,
        "periodo_comparativo": comp_period,
        "period_months": period_months,
        "annual_factor": annual_factor,
        "default_inflation_rate": 33.4,
        "total_entidades": len(df_summary),
        "historical_companies": historical_companies,
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

    out_json = os.path.join(BASE_DIR, "data_sinensup.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"data_sinensup.json generated successfully: {len(payload['companies'])} companies, {len(groups_ranking)} groups ({os.path.getsize(out_json):,} bytes)")
    return out_json

if __name__ == '__main__':
    build_complete_dataset()

