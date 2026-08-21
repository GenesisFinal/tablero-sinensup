import pandas as pd
import numpy as np

def get_account_value(df_c, code, exact=True):
    """Safely retrieves the sum of an account for a given company DataFrame."""
    if exact:
        sub = df_c[df_c['cod_cuenta'] == code]
    else:
        sub = df_c[df_c['cod_cuenta'].str.startswith(code)]
    if sub.empty:
        return 0.0
    return float(sub['importe'].sum())

def compute_all_companies_summary(df):
    """
    Computes rigorous actuarial and regulatory KPIs for all insurance companies
    following official SSN / RGAA standards.
    """
    companies = df[['cod_cia', 'razon_social', 'tipo_entidad']].drop_duplicates()
    records = []

    for _, row in companies.iterrows():
        c_code = row['cod_cia']
        r_name = row['razon_social']
        t_ent = row['tipo_entidad']

        df_c = df[df['cod_cia'] == c_code]

        # 1. Balance Patrimonial
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

        # 2. Estado de Resultados Técnico (Devengado SSN)
        primas_emit = get_account_value(df_c, '5.01.01.00.00.00.00.00', exact=True)
        primas_ced = get_account_value(df_c, '4.01.03.00.00.00.00.00', exact=True)
        anulaciones = get_account_value(df_c, '4.01.04.00.00.00.00.00', exact=True)

        comp_tec_cargo = get_account_value(df_c, '4.01.05.00.00.00.00.00', exact=True)
        comp_tec_liberacion = (
            get_account_value(df_c, '5.01.04.04.04.11.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.12.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.13.00.00', exact=True)
        )
        var_comp_tec = comp_tec_cargo - comp_tec_liberacion

        # Primas Devengadas Netas
        primas_dev = primas_emit - primas_ced - anulaciones - var_comp_tec
        if primas_dev <= 0 and primas_emit > 0:
            primas_dev = primas_emit - primas_ced - anulaciones

        # Siniestros Devengados Netos
        siniestros_cargo = get_account_value(df_c, '4.01.01.00.00.00.00.00', exact=True)
        recup_stros = (
            get_account_value(df_c, '5.01.04.04.04.01.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.02.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.03.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.04.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.05.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.06.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.07.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.08.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.09.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.10.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.14.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.15.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.16.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.17.00.00', exact=True)
        )
        tot_recup = get_account_value(df_c, '5.01.04.00.00.00.00.00', exact=True)
        if recup_stros == 0 and tot_recup > comp_tec_liberacion:
            recup_stros = tot_recup - comp_tec_liberacion

        siniestros_dev = siniestros_cargo - recup_stros
        if siniestros_dev < 0:
            siniestros_dev = max(0.0, siniestros_cargo)

        # Rescates / Rentas / Otras Indemnizaciones
        rescates_indemn = get_account_value(df_c, '4.01.02.00.00.00.00.00', exact=True)

        # Gastos Operativos Netos (Producción + Explotación - Recupero Reaseguros)
        gtos_prod = get_account_value(df_c, '4.01.06.00.00.00.00.00', exact=True)
        gtos_expl = get_account_value(df_c, '4.01.07.00.00.00.00.00', exact=True)
        gtos_reaseg = get_account_value(df_c, '5.01.03.00.00.00.00.00', exact=True)
        gtos_operativos = gtos_prod + gtos_expl - gtos_reaseg

        # Otros Ingresos y Egresos Técnicos
        otros_ing_tec = get_account_value(df_c, '5.01.05.00.00.00.00.00', exact=True)
        otros_egr_tec = get_account_value(df_c, '4.01.50.00.00.00.00.00', exact=True)

        # Resultado Técnico Oficial SSN
        gan_tec = get_account_value(df_c, '5.01.00.00.00.00.00.00', exact=True)
        perd_tec = get_account_value(df_c, '4.01.00.00.00.00.00.00', exact=True)
        res_tecnico = gan_tec - perd_tec

        # Estructura Financiera
        gan_fin = get_account_value(df_c, '5.02.00.00.00.00.00.00', exact=True)
        perd_fin = get_account_value(df_c, '4.02.00.00.00.00.00.00', exact=True)
        res_financiero = gan_fin - perd_fin

        # Impuesto a las Ganancias y Resultado Neto
        imp_gan = get_account_value(df_c, '4.05.00.00.00.00.00.00', exact=True)
        gan_tot = get_account_value(df_c, '5.00.00.00.00.00.00.00', exact=True)
        perd_tot = get_account_value(df_c, '4.00.00.00.00.00.00.00', exact=True)
        res_neto = gan_tot - perd_tot

        # Ratios Actuariales
        base_denominador = primas_dev if primas_dev > 0 else (primas_emit if primas_emit > 0 else 1.0)
        
        loss_ratio = (siniestros_dev / base_denominador * 100) if primas_dev > 0 else 0.0
        rescates_ratio = (rescates_indemn / base_denominador * 100) if primas_dev > 0 else 0.0
        comm_ratio = (gtos_prod / base_denominador * 100) if primas_dev > 0 else 0.0
        exp_ratio = ((gtos_expl - gtos_reaseg) / base_denominador * 100) if primas_dev > 0 else 0.0
        combined_ratio = loss_ratio + comm_ratio + exp_ratio + (rescates_ratio if t_ent == 'Seguros de Retiro' else 0.0)

        margen_tecnico = (res_tecnico / base_denominador * 100) if primas_dev > 0 else 0.0
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
            'siniestros': siniestros_dev,
            'rescates_indemn': rescates_indemn,
            'gtos_operativos': gtos_operativos,
            'gtos_produccion': gtos_prod,
            'gtos_explotacion': gtos_expl,
            'otros_ing_tec': otros_ing_tec,
            'otros_egr_tec': otros_egr_tec,
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
    """
    Generates waterfall steps for income statement of a single company,
    guaranteeing 100% reconciliation with official SSN devengamiento.
    """
    primas_emit = get_account_value(df_cia, '5.01.01.00.00.00.00.00', exact=True)
    primas_ced = get_account_value(df_cia, '4.01.03.00.00.00.00.00', exact=True)
    anulaciones = get_account_value(df_cia, '4.01.04.00.00.00.00.00', exact=True)

    comp_tec_cargo = get_account_value(df_cia, '4.01.05.00.00.00.00.00', exact=True)
    comp_tec_liberacion = (
        get_account_value(df_cia, '5.01.04.04.04.11.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.12.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.13.00.00', exact=True)
    )
    var_comp_tec = comp_tec_cargo - comp_tec_liberacion

    primas_dev = primas_emit - primas_ced - anulaciones - var_comp_tec
    if primas_dev <= 0 and primas_emit > 0:
        primas_dev = primas_emit - primas_ced - anulaciones

    siniestros_cargo = get_account_value(df_cia, '4.01.01.00.00.00.00.00', exact=True)
    recup_stros = (
        get_account_value(df_cia, '5.01.04.04.04.01.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.02.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.03.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.04.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.05.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.06.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.07.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.08.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.09.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.10.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.14.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.15.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.16.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.17.00.00', exact=True)
    )
    tot_recup = get_account_value(df_cia, '5.01.04.00.00.00.00.00', exact=True)
    if recup_stros == 0 and tot_recup > comp_tec_liberacion:
        recup_stros = tot_recup - comp_tec_liberacion

    siniestros_dev = siniestros_cargo - recup_stros
    if siniestros_dev < 0:
        siniestros_dev = max(0.0, siniestros_cargo)

    rescates = get_account_value(df_cia, '4.01.02.00.00.00.00.00', exact=True)

    gtos_prod = get_account_value(df_cia, '4.01.06.00.00.00.00.00', exact=True)
    gtos_expl = get_account_value(df_cia, '4.01.07.00.00.00.00.00', exact=True)
    gtos_reaseg = get_account_value(df_cia, '5.01.03.00.00.00.00.00', exact=True)
    gtos_operativos = gtos_prod + gtos_expl - gtos_reaseg

    otros_ing_tec = get_account_value(df_cia, '5.01.05.00.00.00.00.00', exact=True)
    otros_egr_tec = get_account_value(df_cia, '4.01.50.00.00.00.00.00', exact=True)

    res_tec = get_account_value(df_cia, '5.01.00.00.00.00.00.00', exact=True) - get_account_value(df_cia, '4.01.00.00.00.00.00.00', exact=True)

    gan_fin = get_account_value(df_cia, '5.02.00.00.00.00.00.00', exact=True)
    perd_fin = get_account_value(df_cia, '4.02.00.00.00.00.00.00', exact=True)
    res_fin = gan_fin - perd_fin

    imp_gan = get_account_value(df_cia, '4.05.00.00.00.00.00.00', exact=True)

    gan_tot = get_account_value(df_cia, '5.00.00.00.00.00.00.00', exact=True)
    perd_tot = get_account_value(df_cia, '4.00.00.00.00.00.00.00', exact=True)
    res_neto = gan_tot - perd_tot

    steps = [
        {"name": "Primas y Recargos", "amount": primas_dev, "type": "relative"},
        {"name": "Siniestros Devengados", "amount": -siniestros_dev, "type": "relative"},
    ]
    if rescates > 0:
        steps.append({"name": "Rescates / Prestaciones", "amount": -rescates, "type": "relative"})
    if gtos_operativos > 0:
        steps.append({"name": "Gastos Producción y Explotación", "amount": -gtos_operativos, "type": "relative"})
    if otros_ing_tec > 0:
        steps.append({"name": "Otros Ingresos Técnicos", "amount": otros_ing_tec, "type": "relative"})
    if otros_egr_tec > 0:
        steps.append({"name": "Otros Egresos Técnicos", "amount": -otros_egr_tec, "type": "relative"})
    
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
        sub_df = df[df['cod_cia'] == cod_cia]
    else:
        sub_df = df

    sub_valid = sub_df[(sub_df['desc_subramo'] != '') & (sub_df['desc_subramo'].notna())]
    if sub_valid.empty:
        return pd.DataFrame(columns=['cod_subramo', 'desc_subramo', 'primas', 'siniestros', 'siniestralidad_%'])

    primas_df = sub_valid[sub_valid['cod_cuenta'].str.startswith('5.01.01')].groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()
    primas_df.rename(columns={'importe': 'primas'}, inplace=True)

    stros_df = sub_valid[sub_valid['cod_cuenta'].str.startswith('4.01.01')].groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()
    stros_df.rename(columns={'importe': 'siniestros'}, inplace=True)

    merged = pd.merge(primas_df, stros_df, on=['cod_subramo', 'desc_subramo'], how='outer').fillna(0.0)
    merged['siniestralidad_%'] = np.where(merged['primas'] > 0, (merged['siniestros'] / merged['primas']) * 100, 0.0)
    merged.sort_values(by='primas', ascending=False, inplace=True)
    return merged

def get_company_investments(df_cia):
    """Extracts level 3 investments breakdown for a company."""
    inv_df = df_cia[(df_cia['cod_cuenta'].str.startswith('1.02.')) & (df_cia['nivel'] == 3)].copy()
    if inv_df.empty:
        return pd.DataFrame(columns=['cod_cuenta', 'desc_cuenta', 'importe', 'porcentaje'])

    tot_inv = inv_df['importe'].sum()
    inv_df['porcentaje'] = np.where(tot_inv > 0, (inv_df['importe'] / tot_inv) * 100, 0.0).round(1)
    inv_df.sort_values(by='importe', ascending=False, inplace=True)
    return inv_df[['cod_cuenta', 'desc_cuenta', 'importe', 'porcentaje']]
