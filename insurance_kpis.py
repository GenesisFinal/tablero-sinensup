import pandas as pd
import numpy as np

def get_account_value(df_cia, cod_prefix, exact=False):
    """Safely extracts value from account prefix or exact code."""
    if exact:
        sub = df_cia[df_cia['cod_cuenta'] == cod_prefix]
    else:
        sub = df_cia[df_cia['cod_cuenta'].str.startswith(cod_prefix)]
    if sub.empty:
        return 0.0
    return float(sub['importe'].sum())

def compute_all_companies_summary(df):
    """Computes high-level KPI and balance sheet for all 185 companies."""
    cias = df[['cod_cia', 'razon_social', 'tipo_entidad']].drop_duplicates()
    records = []

    for _, row in cias.iterrows():
        c_code = row['cod_cia']
        r_name = row['razon_social']
        t_ent = row['tipo_entidad']
        df_c = df[df['cod_cia'] == c_code]

        # 1. Patrimoniales
        activo = get_account_value(df_c, '1.00.00.00.00.00.00.00', exact=True)
        disp = get_account_value(df_c, '1.01.00.00.00.00.00.00', exact=True)
        inv = get_account_value(df_c, '1.02.00.00.00.00.00.00', exact=True)
        cred = get_account_value(df_c, '1.03.00.00.00.00.00.00', exact=True)
        inm = get_account_value(df_c, '1.04.00.00.00.00.00.00', exact=True)
        b_uso = get_account_value(df_c, '1.05.00.00.00.00.00.00', exact=True)
        otros_act = get_account_value(df_c, '1.06.00.00.00.00.00.00', exact=True)

        pasivo = get_account_value(df_c, '2.00.00.00.00.00.00.00', exact=True)
        deudas = get_account_value(df_c, '2.01.00.00.00.00.00.00', exact=True)
        comp_tec = get_account_value(df_c, '2.02.00.00.00.00.00.00', exact=True)
        prev = get_account_value(df_c, '2.03.00.00.00.00.00.00', exact=True)

        pn = get_account_value(df_c, '3.00.00.00.00.00.00.00', exact=True)
        capital = get_account_value(df_c, '3.01.00.00.00.00.00.00', exact=True)
        ajuste_pn = get_account_value(df_c, '3.03.00.00.00.00.00.00', exact=True)
        reservas = get_account_value(df_c, '3.04.00.00.00.00.00.00', exact=True)
        res_acum = get_account_value(df_c, '3.05.00.00.00.00.00.00', exact=True)

        # 2. Resultados
        # Ganancias
        gan_tec = get_account_value(df_c, '5.01.00.00.00.00.00.00', exact=True)
        primas_emit = get_account_value(df_c, '5.01.01.00.00.00.00.00', exact=True)
        gan_fin = get_account_value(df_c, '5.02.00.00.00.00.00.00', exact=True)
        gan_tot = get_account_value(df_c, '5.00.00.00.00.00.00.00', exact=True)

        # Pérdidas
        perd_tec = get_account_value(df_c, '4.01.00.00.00.00.00.00', exact=True)
        siniestros = get_account_value(df_c, '4.01.01.00.00.00.00.00', exact=True)
        rescates_indemn = get_account_value(df_c, '4.01.02.00.00.00.00.00', exact=True)
        gtos_prod = get_account_value(df_c, '4.01.06.00.00.00.00.00', exact=True)
        gtos_expl = get_account_value(df_c, '4.01.07.00.00.00.00.00', exact=True)
        perd_fin = get_account_value(df_c, '4.02.00.00.00.00.00.00', exact=True)
        imp_gan = get_account_value(df_c, '4.05.00.00.00.00.00.00', exact=True)
        perd_tot = get_account_value(df_c, '4.00.00.00.00.00.00.00', exact=True)

        # Resultados netos
        res_tecnico = gan_tec - perd_tec
        res_financiero = gan_fin - perd_fin
        res_neto = gan_tot - perd_tot

        # Base devengada estimada de primas:
        # En la estructura contable SSN, Ganancias Técnicas menos cesiones y compromisos técnicos.
        # Primas Devengadas = gan_tec (si no hay desglose negativo) o primas_emitidas ajustadas
        primas_dev = gan_tec if gan_tec > 0 else primas_emit

        # Ratios
        loss_ratio = (siniestros / primas_dev * 100) if primas_dev > 0 else 0.0
        rescates_ratio = (rescates_indemn / primas_dev * 100) if primas_dev > 0 else 0.0
        comm_ratio = (gtos_prod / primas_dev * 100) if primas_dev > 0 else 0.0
        exp_ratio = (gtos_expl / primas_dev * 100) if primas_dev > 0 else 0.0
        combined_ratio = loss_ratio + comm_ratio + exp_ratio + (rescates_ratio if t_ent == 'Seguros de Retiro' else 0.0)

        margen_tecnico = (res_tecnico / primas_dev * 100) if primas_dev > 0 else 0.0
        roi_inversiones = (res_financiero / inv * 100) if inv > 0 else 0.0
        cobertura_res = ((disp + inv + inm) / comp_tec) if comp_tec > 0 else 1.5
        apalancamiento = (primas_dev / pn) if pn > 0 else 0.0
        calidad_cartera = (cred / primas_emit * 100) if primas_emit > 0 else 0.0

        records.append({
            'cod_cia': c_code,
            'razon_social': r_name,
            'tipo_entidad': t_ent,
            'activo': activo,
            'disponibilidades': disp,
            'inversiones': inv,
            'creditos': cred,
            'inmuebles': inm,
            'bienes_uso': b_uso,
            'otros_activos': otros_act,
            'pasivo': pasivo,
            'deudas': deudas,
            'compromisos_tecnicos': comp_tec,
            'previsiones': prev,
            'patrimonio_neto': pn,
            'capital': capital,
            'ajuste_pn': ajuste_pn,
            'reservas': reservas,
            'primas_emitidas': primas_emit,
            'primas_devengadas': primas_dev,
            'ganancias_tecnicas': gan_tec,
            'perdidas_tecnicas': perd_tec,
            'siniestros': siniestros,
            'rescates_indemn': rescates_indemn,
            'gtos_produccion': gtos_prod,
            'gtos_explotacion': gtos_expl,
            'resultado_tecnico': res_tecnico,
            'ganancias_financieras': gan_fin,
            'perdidas_financieras': perd_fin,
            'resultado_financiero': res_financiero,
            'impuesto_ganancias': imp_gan,
            'resultado_neto': res_neto,
            'loss_ratio': loss_ratio,
            'rescates_ratio': rescates_ratio,
            'comm_ratio': comm_ratio,
            'exp_ratio': exp_ratio,
            'combined_ratio': combined_ratio,
            'margen_tecnico': margen_tecnico,
            'roi_inversiones': roi_inversiones,
            'cobertura_reservas': cobertura_res,
            'apalancamiento': apalancamiento,
            'calidad_cartera': calidad_cartera
        })

    return pd.DataFrame(records)

def get_company_waterfall_data(df_cia):
    """Generates waterfall steps for income statement of a single company."""
    gan_tec = get_account_value(df_cia, '5.01.00.00.00.00.00.00', exact=True)
    siniestros = get_account_value(df_cia, '4.01.01.00.00.00.00.00', exact=True)
    rescates = get_account_value(df_cia, '4.01.02.00.00.00.00.00', exact=True)
    reaseg_ces = get_account_value(df_cia, '4.01.03.00.00.00.00.00', exact=True)
    anulaciones = get_account_value(df_cia, '4.01.04.00.00.00.00.00', exact=True)
    comp_tec_var = get_account_value(df_cia, '4.01.05.00.00.00.00.00', exact=True)
    gtos_prod = get_account_value(df_cia, '4.01.06.00.00.00.00.00', exact=True)
    gtos_expl = get_account_value(df_cia, '4.01.07.00.00.00.00.00', exact=True)
    otros_egr_tec = get_account_value(df_cia, '4.01.50.00.00.00.00.00', exact=True)
    
    perd_tec = get_account_value(df_cia, '4.01.00.00.00.00.00.00', exact=True)
    res_tec = gan_tec - perd_tec

    gan_fin = get_account_value(df_cia, '5.02.00.00.00.00.00.00', exact=True)
    perd_fin = get_account_value(df_cia, '4.02.00.00.00.00.00.00', exact=True)
    res_fin = gan_fin - perd_fin

    imp_gan = get_account_value(df_cia, '4.05.00.00.00.00.00.00', exact=True)
    
    gan_tot = get_account_value(df_cia, '5.00.00.00.00.00.00.00', exact=True)
    perd_tot = get_account_value(df_cia, '4.00.00.00.00.00.00.00', exact=True)
    res_neto = gan_tot - perd_tot

    steps = [
        {"name": "Ingresos Técnicos", "amount": gan_tec, "type": "relative"},
        {"name": "Siniestros", "amount": -siniestros, "type": "relative"},
    ]
    if rescates > 0:
        steps.append({"name": "Rescates / Rentas", "amount": -rescates, "type": "relative"})
    if gtos_prod > 0:
        steps.append({"name": "Gastos Producción", "amount": -gtos_prod, "type": "relative"})
    if gtos_expl > 0:
        steps.append({"name": "Gastos Explotación", "amount": -gtos_expl, "type": "relative"})
    
    steps.extend([
        {"name": "Resultado Técnico", "amount": res_tec, "type": "total"},
        {"name": "Resultado Financiero", "amount": res_fin, "type": "relative"},
    ])
    if imp_gan > 0:
        steps.append({"name": "Impuesto Ganancias", "amount": -imp_gan, "type": "relative"})
    
    steps.append({"name": "Resultado Neto", "amount": res_neto, "type": "total"})
    return steps

def get_company_subramos(df, cod_cia=None):
    """Extracts subramos breakdown for a company or the entire market."""
    if cod_cia:
        sub = df[df['cod_cia'] == cod_cia]
    else:
        sub = df

    sub_valid = sub[(sub['desc_subramo'] != '') & (sub['desc_subramo'].notna())]
    # Primas por subramo (cuentas 5.01)
    primas = sub_valid[sub_valid['cod_cuenta'].str.startswith('5.01')].groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()
    primas.rename(columns={'importe': 'primas'}, inplace=True)
    
    siniestros = sub_valid[sub_valid['cod_cuenta'].str.startswith('4.01.01')].groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()
    siniestros.rename(columns={'importe': 'siniestros'}, inplace=True)

    res = pd.merge(primas, siniestros, on=['cod_subramo', 'desc_subramo'], how='outer').fillna(0.0)
    res['siniestralidad_%'] = np.where(res['primas'] > 0, (res['siniestros'] / res['primas'] * 100).round(2), 0.0)
    res = res.sort_values(by='primas', ascending=False)
    return res

def get_company_investments(df_cia):
    """Extracts level 3 investments breakdown for a company."""
    inv_sub = df_cia[(df_cia['cod_cuenta'].str.startswith('1.02.')) & (df_cia['nivel'] == 3)]
    if inv_sub.empty:
        return pd.DataFrame(columns=['desc_cuenta', 'importe', 'porcentaje'])
    res = inv_sub[['desc_cuenta', 'importe']].copy()
    total_inv = res['importe'].sum()
    res['porcentaje'] = np.where(total_inv > 0, (res['importe'] / total_inv * 100).round(2), 0.0)
    return res.sort_values(by='importe', ascending=False)

if __name__ == '__main__':
    from db_engine import get_balance_data
    df = get_balance_data()
    summary = compute_all_companies_summary(df)
    print(f"Summary computed for {len(summary)} companies.")
    print("Top 5 by Activo:\n", summary[['razon_social', 'activo', 'primas_devengadas', 'resultado_neto', 'combined_ratio']].head())
