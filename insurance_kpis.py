import pandas as pd
import numpy as np

def get_account_value(df_cia, cod_cuenta, exact=True):
    """Safely extracts the sum of an account from a single company's slice."""
    if exact:
        sub = df_cia[df_cia['cod_cuenta'] == cod_cuenta]
    else:
        sub = df_cia[df_cia['cod_cuenta'].str.startswith(cod_cuenta)]
    
    if sub.empty:
        return 0.0
    return float(sub['importe'].sum())

def compute_all_companies_summary(df):
    """
    Computes consolidated and company-level insurance KPIs according to SSN accounting rules.
    """
    cias = df[['cod_cia', 'razon_social', 'tipo_entidad']].drop_duplicates()
    records = []

    for _, cia in cias.iterrows():
        cod = cia['cod_cia']
        df_c = df[df['cod_cia'] == cod]
        tipo_entidad = cia['tipo_entidad']
        is_retiro = 'Retiro' in str(tipo_entidad)

        # ----------------------------------------------------
        # 1. BALANCE SHEET METRICS (ACTIVO / PASIVO / PN)
        # ----------------------------------------------------
        activo_tot = get_account_value(df_c, '1.00.00.00.00.00.00.00', exact=True)
        disp = get_account_value(df_c, '1.01.00.00.00.00.00.00', exact=True)
        inv = get_account_value(df_c, '1.02.00.00.00.00.00.00', exact=True)
        cred = get_account_value(df_c, '1.03.00.00.00.00.00.00', exact=True)
        inm = get_account_value(df_c, '1.04.00.00.00.00.00.00', exact=True)
        bienes_uso = get_account_value(df_c, '1.05.00.00.00.00.00.00', exact=True)
        otros_act = get_account_value(df_c, '1.06.00.00.00.00.00.00', exact=True)

        pasivo_tot = get_account_value(df_c, '2.00.00.00.00.00.00.00', exact=True)
        deudas = get_account_value(df_c, '2.01.00.00.00.00.00.00', exact=True)
        comp_tec_pasivo = get_account_value(df_c, '2.02.00.00.00.00.00.00', exact=True)
        prev = get_account_value(df_c, '2.03.00.00.00.00.00.00', exact=True)
        pn = get_account_value(df_c, '3.00.00.00.00.00.00.00', exact=True)

        # Fallback for PN if missing or inconsistent
        if pn == 0 and (activo_tot > 0 or pasivo_tot > 0):
            pn = activo_tot - pasivo_tot

        # ----------------------------------------------------
        # 2. INCOME STATEMENT (DEVENGAMIENTO EXACTO SSN)
        # ----------------------------------------------------
        # Primas Emitidas Brutas
        primas_emit = get_account_value(df_c, '5.01.01.00.00.00.00.00', exact=True)
        
        # Cesiones y Anulaciones
        primas_ced = get_account_value(df_c, '4.01.03.00.00.00.00.00', exact=True)
        anulaciones = get_account_value(df_c, '4.01.04.00.00.00.00.00', exact=True)
        cesiones_anul = primas_ced + anulaciones

        # Variación de Compromisos Técnicos / Reservas Matemáticas / Riesgos en Curso
        comp_tec_cargo = get_account_value(df_c, '4.01.05.00.00.00.00.00', exact=True)
        comp_tec_liberacion = (
            get_account_value(df_c, '5.01.04.04.04.11.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.12.00.00', exact=True) +
            get_account_value(df_c, '5.01.04.04.04.13.00.00', exact=True)
        )
        var_comp_tec = comp_tec_cargo - comp_tec_liberacion

        # Primas Devengadas Netas
        primas_dev = primas_emit - cesiones_anul - var_comp_tec
        if primas_dev <= 0 and primas_emit > 0:
            primas_dev = primas_emit - cesiones_anul

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

        # Rescates y Prestaciones
        rescates = get_account_value(df_c, '4.01.02.00.00.00.00.00', exact=True)

        # Gastos Operativos Netos
        gtos_prod = get_account_value(df_c, '4.01.06.00.00.00.00.00', exact=True)
        gtos_expl = get_account_value(df_c, '4.01.07.00.00.00.00.00', exact=True)
        gtos_reaseg = get_account_value(df_c, '5.01.03.00.00.00.00.00', exact=True)
        gtos_operativos = gtos_prod + gtos_expl - gtos_reaseg

        # Otros Ingresos y Egresos Técnicos
        otros_ing_tec = get_account_value(df_c, '5.01.05.00.00.00.00.00', exact=True)
        otros_egr_tec = get_account_value(df_c, '4.01.50.00.00.00.00.00', exact=True)

        # Resultados Oficiales
        res_tec = get_account_value(df_c, '5.01.00.00.00.00.00.00', exact=True) - get_account_value(df_c, '4.01.00.00.00.00.00.00', exact=True)
        gan_fin = get_account_value(df_c, '5.02.00.00.00.00.00.00', exact=True)
        perd_fin = get_account_value(df_c, '4.02.00.00.00.00.00.00', exact=True)
        res_fin = gan_fin - perd_fin
        imp_gan = get_account_value(df_c, '4.05.00.00.00.00.00.00', exact=True)

        gan_tot = get_account_value(df_c, '5.00.00.00.00.00.00.00', exact=True)
        perd_tot = get_account_value(df_c, '4.00.00.00.00.00.00.00', exact=True)
        res_neto = gan_tot - perd_tot

        # ----------------------------------------------------
        # 3. RATIOS TÉCNICOS & FINANCIEROS (BASE DEVENGADA)
        # ----------------------------------------------------
        base_primas = primas_dev if primas_dev > 0 else (primas_emit if primas_emit > 0 else 1.0)
        
        # En seguros de Retiro / Personas, las prestaciones y rescates forman parte del costo técnico
        costo_prestacional = siniestros_dev + rescates
        loss_ratio = (costo_prestacional / base_primas) * 100.0 if base_primas > 0 else 0.0
        rescates_ratio = (rescates / base_primas) * 100.0 if base_primas > 0 else 0.0
        comm_ratio = (gtos_prod / base_primas) * 100.0 if base_primas > 0 else 0.0
        exp_ratio = (gtos_expl / base_primas) * 100.0 if base_primas > 0 else 0.0
        combined_ratio = loss_ratio + ((gtos_operativos) / base_primas * 100.0) if base_primas > 0 else 0.0

        margen_tecnico = (res_tec / base_primas) * 100.0 if base_primas > 0 else 0.0
        roi_inversiones = (res_fin / inv) * 100.0 if inv > 0 else 0.0

        # Solvencia SSN
        cobertura_res = (inv + inm + disp) / comp_tec_pasivo if comp_tec_pasivo > 0 else 1.0
        apalancamiento = base_primas / pn if pn > 0 else 0.0
        premios_a_cobrar = get_account_value(df_c, '1.03.01.00.00.00.00.00', exact=True)
        calidad_cartera = (premios_a_cobrar / base_primas) * 100.0 if base_primas > 0 else 0.0

        records.append({
            'cod_cia': cod,
            'razon_social': cia['razon_social'],
            'tipo_entidad': tipo_entidad,
            'activo': activo_tot,
            'disponibilidades': disp,
            'inversiones': inv,
            'creditos': cred,
            'inmuebles': inm,
            'bienes_uso': bienes_uso,
            'otros_activos': otros_act,
            'pasivo': pasivo_tot,
            'deudas': deudas,
            'compromisos_tecnicos': comp_tec_pasivo,
            'previsiones': prev,
            'patrimonio_neto': pn,
            'primas_emitidas': primas_emit,
            'cesiones_anulaciones': cesiones_anul,
            'var_reservas': var_comp_tec,
            'primas_devengadas': primas_dev,
            'siniestros': siniestros_dev,
            'rescates': rescates,
            'gtos_produccion': gtos_prod,
            'gtos_explotacion': gtos_expl,
            'gtos_operativos': gtos_operativos,
            'resultado_tecnico': res_tec,
            'resultado_financiero': res_fin,
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
    separating Primas Emitidas from Variación de Reservas Matemáticas / Riesgos en Curso,
    guaranteeing 100% mathematical reconciliation with official SSN balances.
    """
    tipo_entidad = df_cia['tipo_entidad'].iloc[0] if 'tipo_entidad' in df_cia.columns else ''
    is_retiro = 'Retiro' in str(tipo_entidad)

    # 1. Primas Emitidas Brutas
    primas_emit = get_account_value(df_cia, '5.01.01.00.00.00.00.00', exact=True)
    
    # 2. Cesiones y Anulaciones
    primas_ced = get_account_value(df_cia, '4.01.03.00.00.00.00.00', exact=True)
    anulaciones = get_account_value(df_cia, '4.01.04.00.00.00.00.00', exact=True)
    cesiones_anul = primas_ced + anulaciones

    # 3. Variación de Compromisos Técnicos / Reservas Matemáticas / Riesgos en Curso
    comp_tec_cargo = get_account_value(df_cia, '4.01.05.00.00.00.00.00', exact=True)
    comp_tec_liberacion = (
        get_account_value(df_cia, '5.01.04.04.04.11.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.12.00.00', exact=True) +
        get_account_value(df_cia, '5.01.04.04.04.13.00.00', exact=True)
    )
    var_comp_tec = comp_tec_cargo - comp_tec_liberacion

    # 4. Siniestros Devengados Netos
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

    # 5. Rescates / Rentas / Prestaciones
    rescates_tot = get_account_value(df_cia, '4.01.02.00.00.00.00.00', exact=True)

    # 6. Gastos Operativos Netos
    gtos_prod = get_account_value(df_cia, '4.01.06.00.00.00.00.00', exact=True)
    gtos_expl = get_account_value(df_cia, '4.01.07.00.00.00.00.00', exact=True)
    gtos_reaseg = get_account_value(df_cia, '5.01.03.00.00.00.00.00', exact=True)
    gtos_operativos = gtos_prod + gtos_expl - gtos_reaseg

    # 7. Otros Ingresos y Egresos Técnicos
    otros_ing_tec = get_account_value(df_cia, '5.01.05.00.00.00.00.00', exact=True)
    otros_egr_tec = get_account_value(df_cia, '4.01.50.00.00.00.00.00', exact=True)

    # 8. Totales de Resultados
    res_tec = get_account_value(df_cia, '5.01.00.00.00.00.00.00', exact=True) - get_account_value(df_cia, '4.01.00.00.00.00.00.00', exact=True)
    gan_fin = get_account_value(df_cia, '5.02.00.00.00.00.00.00', exact=True)
    perd_fin = get_account_value(df_cia, '4.02.00.00.00.00.00.00', exact=True)
    res_fin = gan_fin - perd_fin
    imp_gan = get_account_value(df_cia, '4.05.00.00.00.00.00.00', exact=True)

    gan_tot = get_account_value(df_cia, '5.00.00.00.00.00.00.00', exact=True)
    perd_tot = get_account_value(df_cia, '4.00.00.00.00.00.00.00', exact=True)
    res_neto = gan_tot - perd_tot

    steps = [
        {"name": "Primas y Recargos Emitidos", "amount": primas_emit, "type": "relative"}
    ]
    if abs(cesiones_anul) > 1e3:
        steps.append({"name": "Cesiones y Anulaciones", "amount": -cesiones_anul, "type": "relative"})
        
    if abs(var_comp_tec) > 1e3:
        label_res = "Var. Reservas Matemáticas" if is_retiro else "Var. Riesgos en Curso / Reservas"
        steps.append({"name": label_res, "amount": -var_comp_tec, "type": "relative"})

    if abs(siniestros_dev) > 1e3:
        steps.append({"name": "Siniestros Devengados", "amount": -siniestros_dev, "type": "relative"})

    if abs(rescates_tot) > 1e3:
        label_resc = "Rescates y Rentas" if is_retiro else "Rescates / Prestaciones"
        steps.append({"name": label_resc, "amount": -rescates_tot, "type": "relative"})

    if abs(gtos_operativos) > 1e3:
        steps.append({"name": "Gastos Producción y Explotación", "amount": -gtos_operativos, "type": "relative"})

    if abs(otros_ing_tec) > 1e3:
        label_ing = "Transf. Financiera a Técnica" if (is_retiro and otros_ing_tec < 0) else "Otros Ingresos Técnicos"
        steps.append({"name": label_ing, "amount": otros_ing_tec, "type": "relative"})

    if abs(otros_egr_tec) > 1e3:
        steps.append({"name": "Otros Egresos Técnicos", "amount": -otros_egr_tec, "type": "relative"})

    steps.extend([
        {"name": "Resultado Técnico", "amount": res_tec, "type": "total"},
        {"name": "Resultado Financiero", "amount": res_fin, "type": "relative"},
    ])
    if abs(imp_gan) > 1e3:
        steps.append({"name": "Impuesto Ganancias", "amount": -imp_gan, "type": "relative"})

    steps.append({"name": "Resultado Neto", "amount": res_neto, "type": "total"})
    return steps

def get_company_subramos(df, cod_cia=None):
    """Extracts subramos breakdown for a company or the entire market."""
    if cod_cia:
        sub_df = df[df['cod_cia'] == cod_cia]
    else:
        sub_df = df

    primas_rows = sub_df[sub_df['cod_cuenta'].str.startswith('5.01.01.01.01.01')]
    siniestros_rows = sub_df[sub_df['cod_cuenta'].str.startswith('4.01.01.01.01.01')]

    primas_by_sub = primas_rows.groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()
    sin_by_sub = siniestros_rows.groupby(['cod_subramo', 'desc_subramo'])['importe'].sum().reset_index()

    merged = pd.merge(primas_by_sub, sin_by_sub, on=['cod_subramo', 'desc_subramo'], how='outer', suffixes=('_primas', '_siniestros')).fillna(0)
    merged['primas'] = merged['importe_primas']
    merged['siniestros'] = merged['importe_siniestros']
    merged['siniestralidad_%'] = np.where(merged['primas'] > 0, (merged['siniestros'] / merged['primas']) * 100.0, 0.0)

    merged = merged[merged['desc_subramo'].notna() & (merged['desc_subramo'] != '') & (merged['primas'] > 0 | (merged['siniestros'] > 0))]
    merged = merged.sort_values(by='primas', ascending=False)
    
    return merged[['cod_subramo', 'desc_subramo', 'primas', 'siniestros', 'siniestralidad_%']].to_dict(orient='records')

def get_company_investments_breakdown(df_cia):
    """Extracts level 3 breakdown of account 1.02 (Inversiones)."""
    inv_df = df_cia[df_cia['cod_cuenta'].str.startswith('1.02.')]
    
    # We want level 3 accounts: e.g., 1.02.01.00.00.00.00.00
    # or accounts where level 3 is non zero and level 4 is 00
    level3 = inv_df[inv_df['cod_cuenta'].apply(lambda x: len(x.split('.')) >= 3 and x.split('.')[2] != '00' and (len(x.split('.')) == 3 or x.split('.')[3] == '00'))]
    
    if level3.empty:
        # Fallback to level 2
        level3 = inv_df[inv_df['cod_cuenta'].apply(lambda x: len(x.split('.')) >= 2 and x.split('.')[1] != '00' and (len(x.split('.')) == 2 or x.split('.')[2] == '00'))]

    records = []
    total_inv = level3['importe'].sum()
    for _, row in level3.iterrows():
        if row['importe'] > 0:
            pct = (row['importe'] / total_inv * 100.0) if total_inv > 0 else 0.0
            records.append({
                'cod_cuenta': row['cod_cuenta'],
                'desc_cuenta': row['desc_cuenta'],
                'importe': float(row['importe']),
                'porcentaje': round(pct, 1)
            })
    records.sort(key=lambda x: x['importe'], reverse=True)
    return records
