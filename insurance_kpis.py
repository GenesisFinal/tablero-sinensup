import pandas as pd
import numpy as np

def get_account_value(df_cia, account_code_prefix, exact=False):
    """Safely retrieves the sum of imports for a given account code pattern."""
    if df_cia.empty:
        return 0.0
    if exact:
        sub = df_cia[df_cia['cod_cuenta'] == account_code_prefix]
    else:
        sub = df_cia[df_cia['cod_cuenta'].str.startswith(account_code_prefix)]
    if sub.empty:
        return 0.0
    return float(sub['importe'].sum())


def _extract_ssn_technical_components(df_slice, use_exact=True):
    """
    Extracts exact SSN RGAA technical P&L components for a slice of accounting rows
    or a pre-aggregated `{cod_cuenta: importe}` dict.
    - When `use_exact=True`, rows MUST be balance-level (`cod_subramo == ''`)
      where hierarchical `.00` summary accounts exist without double counting.
    - When `use_exact=False`, rows MUST be subramo leaf-only (`cod_subramo != ''`)
      where `.00` summary rollups do not exist.
    Guarantees 0-peso reconciliation:
      primas_dev - (siniestros_dev + rescates) - gtos_prod - gtos_expl + otros_tec_neto == 5.01 - 4.01
    """
    if isinstance(df_slice, dict):
        acc_sums = df_slice
        is_empty = (len(acc_sums) == 0)
    else:
        is_empty = df_slice.empty
        acc_sums = {} if is_empty else df_slice.groupby('cod_cuenta')['importe'].sum().to_dict()

    if is_empty:
        return {k: 0.0 for k in (
            'primas_emit', 'anulaciones', 'reaseg_neto', 'primas_cedidas', 'recup_cesion',
            'cesion_neta', 'cesiones_anul', 'var_comp_tec', 'primas_dev',
            'part_util_reaseg', 'recup_sin', 'siniestros_dev', 'rescates',
            'gtos_prod', 'gtos_expl', 'gtos_operativos', 'otros_ing_tec',
            'otros_egr_tec', 'otros_tec_neto', 'res_tec_calc'
        )}

    def g_prefix(prefix):
        return float(sum(v for k, v in acc_sums.items() if k.startswith(prefix)))

    def g_lvl(exact_code, prefix_with_dot):
        if use_exact and exact_code in acc_sums:
            return float(acc_sums[exact_code])
        return g_prefix(prefix_with_dot)

    # Paso 1: Emisión Directa Neta Total (Directas + Derechos + Recargos - Anulaciones)
    p_dir = g_lvl('5.01.01.01.01.01.00.00', '5.01.01.01.01.01.')
    derechos = g_lvl('5.01.01.01.01.02.00.00', '5.01.01.01.01.02.')
    recargos = g_lvl('5.01.01.01.01.03.00.00', '5.01.01.01.01.03.')
    a_dir = g_lvl('4.01.04.04.04.01.00.00', '4.01.04.04.04.01.')
    a_rec = g_lvl('4.01.04.04.04.02.00.00', '4.01.04.04.04.02.')
    anulaciones = a_dir + a_rec
    primas_emit = (p_dir + derechos + recargos) - anulaciones

    # Reaseguro activo neto = total primas netas de anulaciones (5.01.01 - 4.01.04) - emisión directa neta
    tot_ing_primas = g_lvl('5.01.01.00.00.00.00.00', '5.01.01.')
    tot_anul_primas = g_lvl('4.01.04.00.00.00.00.00', '4.01.04.')
    reaseg_neto = (tot_ing_primas - tot_anul_primas) - primas_emit

    # Paso 2: Cesiones netas a Reaseguro (4.01.03 - 5.01.02 Recupero/Anul. Primas Cedidas)
    cesion_bruta = g_lvl('4.01.03.00.00.00.00.00', '4.01.03.')
    recup_cesion = g_lvl('5.01.02.00.00.00.00.00', '5.01.02.')
    cesion_neta = cesion_bruta - recup_cesion
    cesiones_anul = cesion_neta + anulaciones

    # Paso 3: Variación Neta de Compromisos Técnicos / Riesgos en Curso (.11/.12/.13)
    var_comp_cargo = g_lvl('4.01.05.00.00.00.00.00', '4.01.05.')
    var_comp_lib = (
        g_lvl('5.01.04.04.04.11.00.00', '5.01.04.04.04.11.') +
        g_lvl('5.01.04.04.04.12.00.00', '5.01.04.04.04.12.') +
        g_lvl('5.01.04.04.04.13.00.00', '5.01.04.04.04.13.')
    )
    var_comp_tec = var_comp_cargo - var_comp_lib

    # Primas Devengadas Técnicas Oficiales
    primas_dev = primas_emit + reaseg_neto - cesion_neta - var_comp_tec

    # Paso 4: Siniestros Devengados Netos (incluye .03/.04/.05/.19/.22 etc.; excluye .08 Part. Utilidades)
    tot_recup = g_lvl('5.01.04.00.00.00.00.00', '5.01.04.')
    part_util_reaseg = g_lvl('5.01.04.04.04.08.00.00', '5.01.04.04.04.08.')
    recup_sin = tot_recup - var_comp_lib - part_util_reaseg
    siniestros_cargo = g_lvl('4.01.01.00.00.00.00.00', '4.01.01.')
    siniestros_dev = siniestros_cargo - recup_sin

    # Paso 5: Rescates, Rentas y Beneficios (4.01.02)
    rescates = g_lvl('4.01.02.00.00.00.00.00', '4.01.02.')

    # Paso 6: Gastos de Producción y Explotación (incluye 4.01.60 Prevención ART y .08 Part. Utilidades)
    gtos_prod_cargo = g_lvl('4.01.06.00.00.00.00.00', '4.01.06.')
    recup_gtos_prod = g_lvl('5.01.03.00.00.00.00.00', '5.01.03.')
    gtos_prod = gtos_prod_cargo - recup_gtos_prod - part_util_reaseg

    gtos_expl = g_lvl('4.01.07.00.00.00.00.00', '4.01.07.') + g_lvl('4.01.60.00.00.00.00.00', '4.01.60.')
    gtos_operativos = gtos_prod + gtos_expl

    # Paso 7: Otros Ingresos y Egresos Técnicos
    otros_ing_tec = g_lvl('5.01.05.00.00.00.00.00', '5.01.05.')
    otros_egr_tec = g_lvl('4.01.50.00.00.00.00.00', '4.01.50.')
    otros_tec_neto = otros_ing_tec - otros_egr_tec

    res_tec_calc = primas_dev - (siniestros_dev + rescates) - gtos_operativos + otros_tec_neto

    return {
        'primas_emit': primas_emit,
        'anulaciones': anulaciones,
        'reaseg_neto': reaseg_neto,
        'primas_cedidas': cesion_neta,
        'recup_cesion': recup_cesion,
        'cesion_neta': cesion_neta,
        'cesiones_anul': cesiones_anul,
        'var_comp_tec': var_comp_tec,
        'primas_dev': primas_dev,
        'part_util_reaseg': part_util_reaseg,
        'recup_sin': recup_sin,
        'siniestros_dev': siniestros_dev,
        'rescates': rescates,
        'gtos_prod': gtos_prod,
        'gtos_expl': gtos_expl,
        'gtos_operativos': gtos_operativos,
        'otros_ing_tec': otros_ing_tec,
        'otros_egr_tec': otros_egr_tec,
        'otros_tec_neto': otros_tec_neto,
        'res_tec_calc': res_tec_calc,
    }


def get_period_months(periodo_str):
    """
    Returns elapsed fiscal months in the SSN July–June exercise:
    -3 (Sep, Q1) -> 3 months; -4 (Dec, Q2) -> 6; -1 (Mar, Q3) -> 9; -2 (Jun, Q4) -> 12.
    """
    s = str(periodo_str or '').strip()
    if '-' in s:
        q = s.split('-', 1)[1].strip()
        return {'3': 3, '4': 6, '1': 9, '2': 12}.get(q, 12)
    return 12


def compute_all_companies_summary(df):
    """
    Computes standard SSN financial and technical KPIs for all companies.
    Values are in ARS (Pesos Homogéneos).
    """
    df_bal = df[df['cod_subramo'] == ''] if 'cod_subramo' in df.columns else df
    df_sub = df[df['cod_subramo'] != ''] if 'cod_subramo' in df.columns else df.iloc[0:0]
    df_20101 = df_sub[df_sub['cod_cuenta'].str.startswith('2.01.01.')] if not df_sub.empty else df_sub

    RSP_PREFIXES = (
        '2.01.01.01.01.01.',  # Stros. Pendientes - Seguros Directos Administrativos
        '2.01.01.01.01.02.',  # Stros. Pendientes - Seguros Directos En juicios
        '2.01.01.01.01.03.',  # Stros. Pendientes - Seguros Directos En Mediación
        '2.01.01.01.01.04.',  # Stros. Pendientes a/c Reaseguradores (-)
        '2.01.01.01.01.05.',  # Stros. Liquidados a Pagar
        '2.01.01.01.01.06.',  # Stros. en Proceso de Liquidación
        '2.01.01.01.01.07.',  # Stros. Pendientes Reaseguros Activos y Retrocesiones
        '2.01.01.01.01.16.',  # Stros. Esperados (Vida - Ley 24.241)
        '2.01.01.01.01.17.',  # Reserva Especial - Transporte Público de Pasajeros
        '2.01.01.01.01.18.',  # Stros. por Reclamaciones Judiciales ART (.01 Med, .02 Juicio, .03 Ley 27348)
        '2.01.01.01.01.19.',  # Diferimiento Stros. Pendientes (-)
        '2.01.01.01.01.21.',  # Incapacidades Laborales Temporarias a Pagar
        '2.01.01.01.01.22.',  # Prestaciones en Especies a Pagar
        '2.01.01.01.01.24.',  # Saldo a amortizar dif. reserva pto. 33.4.1.6 (-)
        '2.01.01.01.01.26.',  # Amort. dif. cálc. Rva.-val. juicios s/sentencia (-)
        '2.01.01.01.01.27.',  # Ajuste por Diferencia a amortizar en 8 trimestres (-)
        '2.01.01.01.01.28.01.', '2.01.01.01.01.28.02.', '2.01.01.01.01.28.03.', '2.01.01.01.01.28.04.',
        '2.01.01.01.01.28.05.', '2.01.01.01.01.28.06.', '2.01.01.01.01.28.07.', '2.01.01.01.01.28.08.',
        '2.01.01.01.01.28.09.', '2.01.01.01.01.28.10.', '2.01.01.01.01.28.11.', '2.01.01.01.01.28.12.',
        '2.01.01.01.01.28.15.', '2.01.01.01.01.28.16.',  # Stros. Pendientes a/c FFEP (-)
        '2.01.01.01.01.29.',  # Reserva por Juicios Futuros
    )
    IBNR_PREFIXES = (
        '2.01.01.01.01.08.',     # Stros. Ocurridos y no Reportados - IBNR
        '2.01.01.01.01.09.',     # Stros. Ocurridos y no Suficientemente Reportados - IBNER
        '2.01.01.01.01.10.',     # Stros. Ocurridos y no Reportados - IBNR a/c Reaseg. (-)
        '2.01.01.01.01.20.',     # Diferimiento IBNR (-)
        '2.01.01.01.01.25.',     # Stros. Ocurr. y no Reportados - IBNR por Reas. Act.
        '2.01.01.01.01.28.13.',  # IBNR a/c FFEP (-)
    )
    JUICIOS_PREFIXES = (
        '2.01.01.01.01.02.',     # Stros. Pendientes - Seguros Directos En juicios
        '2.01.01.01.01.18.02.',  # Siniestros ART - En juicio
        '2.01.01.01.01.18.03.',  # Proc jud. de revisión inst adm Art 2° Ley 27348
        '2.01.01.01.01.26.',     # Amort. dif. cálc. Rva.-val. juicios s/sentencia (-)
        '2.01.01.01.01.28.07.',  # Stros. en Juicio a/c FFEP (-)
        '2.01.01.01.01.28.08.',  # Stros. COVID en Juicio a/c FFEP (-)
        '2.01.01.01.01.28.15.',  # Rev Inst Adm Art 2° Ley 27348 a/c FFEP (-)
        '2.01.01.01.01.28.16.',  # Rev Inst Adm Art 2° Ley 27348 COVID a/c FFEP (-)
        '2.01.01.01.01.29.',     # Reserva por Juicios Futuros
    )
    MEDIACIONES_PREFIXES = (
        '2.01.01.01.01.03.',     # Stros. Pendientes - Seguros Directos En Mediación
        '2.01.01.01.01.18.01.',  # Siniestros ART - En mediación
        '2.01.01.01.01.28.05.',  # Stros. en Mediación a/c FFEP (-)
        '2.01.01.01.01.28.06.',  # Stros. COVID en Mediación a/c FFEP (-)
    )

    if not df_20101.empty:
        rsp_by_cia = df_20101[df_20101['cod_cuenta'].str.startswith(RSP_PREFIXES)].groupby('cod_cia')['importe'].sum().to_dict()
        ibnr_by_cia = df_20101[df_20101['cod_cuenta'].str.startswith(IBNR_PREFIXES)].groupby('cod_cia')['importe'].sum().to_dict()
        juicios_by_cia = df_20101[df_20101['cod_cuenta'].str.startswith(JUICIOS_PREFIXES)].groupby('cod_cia')['importe'].sum().to_dict()
        med_by_cia = df_20101[df_20101['cod_cuenta'].str.startswith(MEDIACIONES_PREFIXES)].groupby('cod_cia')['importe'].sum().to_dict()
    else:
        rsp_by_cia, ibnr_by_cia, juicios_by_cia, med_by_cia = {}, {}, {}, {}

    companies = df_bal[['cod_cia', 'razon_social', 'tipo_entidad']].drop_duplicates()
    periodo_str = str(df_bal['periodo'].iloc[0]).strip() if ('periodo' in df_bal.columns and not df_bal.empty) else ''
    period_months = get_period_months(periodo_str)
    annual_factor = 12.0 / float(period_months) if period_months > 0 else 1.0
    records = []

    for _, cia in companies.iterrows():
        cod = cia['cod_cia']
        df_c = df_bal[df_bal['cod_cia'] == cod]

        # ----------------------------------------------------
        # 1. BALANCE PATRIMONIAL
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
        deudas_aseg = get_account_value(df_c, '2.01.01.00.00.00.00.00', exact=True)
        comp_tec_pasivo = get_account_value(df_c, '2.02.00.00.00.00.00.00', exact=True)
        riesgos_curso = get_account_value(df_c, '2.02.02.02.02.00.00.00', exact=True)
        res_matematicas = get_account_value(df_c, '2.02.02.02.03.00.00.00', exact=True)
        prev = get_account_value(df_c, '2.03.00.00.00.00.00.00', exact=True)
        pn = get_account_value(df_c, '3.00.00.00.00.00.00.00', exact=True)

        # ----------------------------------------------------
        # 2. ESTADO DE RESULTADOS OFICIAL (SSN MONEDA HOMOGÉNEA)
        # ----------------------------------------------------
        tipo_entidad = cia['tipo_entidad']
        comp = _extract_ssn_technical_components(df_c, use_exact=True)
        primas_emit = comp['primas_emit']
        reaseg_neto = comp['reaseg_neto']
        primas_cedidas = comp['primas_cedidas']
        cesiones_anul = comp['cesiones_anul']
        var_comp_tec = comp['var_comp_tec']
        primas_dev = comp['primas_dev']
        siniestros_dev = comp['siniestros_dev']
        rescates = comp['rescates']
        gtos_prod = comp['gtos_prod']
        gtos_expl = comp['gtos_expl']
        gtos_operativos = comp['gtos_operativos']
        otros_tec_neto = comp['otros_tec_neto']

        # Resultados Oficiales
        res_tec = get_account_value(df_c, '5.01.00.00.00.00.00.00', exact=True) - get_account_value(df_c, '4.01.00.00.00.00.00.00', exact=True)
        gan_fin = get_account_value(df_c, '5.02.00.00.00.00.00.00', exact=True)
        perd_fin = get_account_value(df_c, '4.02.00.00.00.00.00.00', exact=True)
        res_fin = gan_fin - perd_fin
        op_extraord = (
            (get_account_value(df_c, '5.03.00.00.00.00.00.00', exact=True) - get_account_value(df_c, '4.04.00.00.00.00.00.00', exact=True))
            - get_account_value(df_c, '4.03.00.00.00.00.00.00', exact=True)
        )
        imp_gan = get_account_value(df_c, '4.05.00.00.00.00.00.00', exact=True)

        gan_tot = get_account_value(df_c, '5.00.00.00.00.00.00.00', exact=True)
        perd_tot = get_account_value(df_c, '4.00.00.00.00.00.00.00', exact=True)
        res_neto = gan_tot - perd_tot

        # ----------------------------------------------------
        # 3. RATIOS TÉCNICOS & FINANCIEROS (BASE DEVENGADA)
        # ----------------------------------------------------
        base_primas = primas_dev if primas_dev > 0 else (primas_emit if primas_emit > 0 else 0.0)
        sin_base_primas = (base_primas <= 0)
        has_primas = not sin_base_primas

        costo_prestacional = siniestros_dev + rescates
        loss_ratio = (costo_prestacional / base_primas) * 100.0 if has_primas else 0.0
        rescates_ratio = (rescates / base_primas) * 100.0 if has_primas else 0.0
        comm_ratio = (gtos_prod / base_primas) * 100.0 if has_primas else 0.0
        exp_ratio = (gtos_expl / base_primas) * 100.0 if has_primas else 0.0
        combined_ratio = loss_ratio + ((gtos_operativos) / base_primas * 100.0) if has_primas else 0.0

        margen_tecnico = (res_tec / base_primas) * 100.0 if has_primas else 0.0
        roi_inversiones = (res_fin / inv) * 100.0 if inv > 0 else 0.0

        # Solvencia SSN (Stock / Flujo anualizado según trimestre fiscal)
        sin_compromisos_tecnicos = (comp_tec_pasivo <= 0)
        patrimonio_negativo = (pn <= 0)
        cobertura_res = (inv + inm + disp) / comp_tec_pasivo if comp_tec_pasivo > 0 else 0.0
        apalancamiento = ((base_primas * annual_factor) / pn) if pn > 0 else (-1.0 if pn < 0 else 0.0)
        premios_a_cobrar = get_account_value(df_c, '1.03.01.00.00.00.00.00', exact=True)
        calidad_cartera = (premios_a_cobrar / (primas_emit * annual_factor)) * 100.0 if primas_emit > 0 else 0.0

        # Ratios de Gestión adicionales (Retención pura de Reaseguro: Primas Emitidas - Cedidas / Primas Emitidas)
        retencion_ratio = max(0.0, min(100.0, ((primas_emit - primas_cedidas) / primas_emit * 100.0))) if primas_emit > 0 else 100.0
        cesion_ratio = (primas_cedidas / primas_emit * 100.0) if primas_emit > 0 else 0.0
        roe = (res_neto / pn * 100.0) if pn > 0 else ((res_neto / abs(pn) * 100.0) if pn < 0 else 0.0)
        res_fin_sobre_pn = (res_fin / pn * 100.0) if pn > 0 else ((res_fin / abs(pn) * 100.0) if pn < 0 else 0.0)
        roa = (res_neto / activo_tot * 100.0) if activo_tot > 0 else 0.0
        margen_neto = (res_neto / base_primas * 100.0) if has_primas else 0.0
        densidad_inversiones = (inv / activo_tot * 100.0) if activo_tot > 0 else 0.0

        # VPP (Valor Patrimonial Proporcional / Acciones Grupo Económico y Otras Participaciones)
        vpp_activo_sin = get_account_value(df_c, '1.02.01.02.02.02.00.00', exact=True)
        vpp_activo_con = get_account_value(df_c, '1.02.01.02.01.02.00.00', exact=True)
        vpp_activo_ext = get_account_value(df_c, '1.02.02.01.02.02.00.00', exact=True)
        vpp_activo = vpp_activo_sin + vpp_activo_con + vpp_activo_ext

        mkt_acciones = (
            get_account_value(df_c, '1.02.01.02.01.01.00.00', exact=True) +
            get_account_value(df_c, '1.02.01.02.02.01.00.00', exact=True) +
            get_account_value(df_c, '1.02.02.01.02.01.00.00', exact=True)
        )

        vpp_tenencia_acc = get_account_value(df_c, '5.02.03.03.01.02.00.00', exact=True)
        vpp_tenencia_otr = get_account_value(df_c, '5.02.03.03.02.01.00.00', exact=True)
        vpp_realizacion_acc = get_account_value(df_c, '5.02.02.02.01.02.00.00', exact=True)

        if vpp_activo <= 0 or (vpp_activo < 100_000_000.0 and vpp_activo < 0.05 * mkt_acciones):
            vpp_resultado = 0.0
        else:
            equity_share_ge = (vpp_activo / (vpp_activo + mkt_acciones)) if (vpp_activo + mkt_acciones) > 0 else 1.0
            vpp_resultado = (vpp_tenencia_acc + vpp_realizacion_acc) * equity_share_ge + vpp_tenencia_otr
            if abs(vpp_resultado) < 1000.0:
                vpp_resultado = 0.0

        vpp_pct_neto = round((vpp_resultado / res_neto * 100.0), 1) if (vpp_resultado != 0 and res_neto != 0) else 0.0
        vpp_pct_fin = round((vpp_resultado / res_fin * 100.0), 1) if (vpp_resultado != 0 and res_fin != 0) else 0.0

        records.append({
            'cod_cia': cod,
            'razon_social': cia['razon_social'],
            'tipo_entidad': tipo_entidad,
            'activo': activo_tot,
            'disponibilidades': disp,
            'inversiones': inv,
            'creditos': cred,
            'premios_a_cobrar': premios_a_cobrar,
            'inmuebles': inm,
            'bienes_uso': bienes_uso,
            'otros_activos': otros_act,
            'pasivo': pasivo_tot,
            'deudas': deudas,
            'deudas_asegurados': deudas_aseg,
            'reserva_siniestros_pendientes': float(rsp_by_cia.get(cod, 0.0)),
            'ibnr': float(ibnr_by_cia.get(cod, 0.0)),
            'reserva_juicios': float(juicios_by_cia.get(cod, 0.0)),
            'reserva_mediaciones': float(med_by_cia.get(cod, 0.0)),
            'compromisos_tecnicos': comp_tec_pasivo,
            'riesgos_en_curso': riesgos_curso,
            'reservas_matematicas': res_matematicas,
            'previsiones': prev,
            'patrimonio_neto': pn,
            'primas_emitidas': primas_emit,
            'reaseguro_activo_neto': reaseg_neto,
            'primas_cedidas': primas_cedidas,
            'cesiones_anulaciones': cesiones_anul,
            'var_reservas': var_comp_tec,
            'primas_devengadas': primas_dev,
            'siniestros': siniestros_dev,
            'rescates': rescates,
            'gtos_produccion': gtos_prod,
            'gtos_explotacion': gtos_expl,
            'gtos_operativos': gtos_operativos,
            'otros_tec_neto': otros_tec_neto,
            'op_extraordinarias': op_extraord,
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
            'calidad_cartera': calidad_cartera,
            'retencion_ratio': retencion_ratio,
            'cesion_ratio': cesion_ratio,
            'roe': roe,
            'res_fin_sobre_pn': res_fin_sobre_pn,
            'roa': roa,
            'margen_neto': margen_neto,
            'densidad_inversiones': densidad_inversiones,
            'vpp_resultado': vpp_resultado,
            'vpp_activo': vpp_activo,
            'vpp_pct_neto': vpp_pct_neto,
            'vpp_pct_fin': vpp_pct_fin,
            'sin_base_primas': bool(sin_base_primas),
            'patrimonio_negativo': bool(patrimonio_negativo),
            'sin_compromisos_tecnicos': bool(sin_compromisos_tecnicos)
        })

    return pd.DataFrame(records)

def get_company_waterfall_data(df_cia):
    """
    Builds the Waterfall steps starting with Primas Emitidas and reconciling
    to official SSN Resultado Técnico and Resultado Neto (0-peso discrepancy).
    """
    if df_cia.empty:
        return []

    df_bal = df_cia[df_cia['cod_subramo'] == ''] if 'cod_subramo' in df_cia.columns else df_cia
    if df_bal.empty:
        return []

    unique_tipos = df_bal['tipo_entidad'].dropna().unique() if 'tipo_entidad' in df_bal.columns else []
    is_retiro = (len(unique_tipos) == 1 and unique_tipos[0] == 'Seguros de Retiro')
    reserva_label = "Var. Reservas Matemáticas" if is_retiro else "Var. Riesgos en Curso / Reservas"

    comp = _extract_ssn_technical_components(df_bal, use_exact=True)
    primas_emit = comp['primas_emit']
    reaseg_neto = comp['reaseg_neto']
    primas_cedidas = comp['primas_cedidas']
    var_comp_tec = comp['var_comp_tec']
    siniestros_dev = comp['siniestros_dev']
    rescates = comp['rescates']
    gtos_operativos = comp['gtos_operativos']
    otros_ing_tec = comp['otros_ing_tec']
    otros_egr_tec = comp['otros_egr_tec']

    # Totales Oficiales
    res_tec = get_account_value(df_bal, '5.01.00.00.00.00.00.00', exact=True) - get_account_value(df_bal, '4.01.00.00.00.00.00.00', exact=True)
    gan_fin = get_account_value(df_bal, '5.02.00.00.00.00.00.00', exact=True)
    perd_fin = get_account_value(df_bal, '4.02.00.00.00.00.00.00', exact=True)
    res_fin = gan_fin - perd_fin
    op_extraord = (
        (get_account_value(df_bal, '5.03.00.00.00.00.00.00', exact=True) - get_account_value(df_bal, '4.04.00.00.00.00.00.00', exact=True))
        - get_account_value(df_bal, '4.03.00.00.00.00.00.00', exact=True)
    )
    imp_gan = get_account_value(df_bal, '4.05.00.00.00.00.00.00', exact=True)
    res_neto = get_account_value(df_bal, '5.00.00.00.00.00.00.00', exact=True) - get_account_value(df_bal, '4.00.00.00.00.00.00.00', exact=True)

    steps = [
        {"name": "Emisión Directa Neta Total", "amount": round(primas_emit, 2), "type": "relative"}
    ]

    if reaseg_neto != 0:
        steps.append({"name": "Reaseguros Activos Netos", "amount": round(reaseg_neto, 2), "type": "relative"})

    if primas_cedidas != 0:
        steps.append({"name": "Cesión a Reaseguradores", "amount": round(-primas_cedidas, 2), "type": "relative"})

    if var_comp_tec != 0:
        steps.append({"name": reserva_label, "amount": round(-var_comp_tec, 2), "type": "relative"})

    if siniestros_dev != 0:
        steps.append({"name": "Siniestros Devengados", "amount": round(-siniestros_dev, 2), "type": "relative"})

    if rescates != 0:
        label_rescates = "Rescates y Rentas" if is_retiro else "Rescates / Prestaciones"
        steps.append({"name": label_rescates, "amount": round(-rescates, 2), "type": "relative"})

    if gtos_operativos != 0:
        steps.append({"name": "Gastos Producción y Explotación", "amount": round(-gtos_operativos, 2), "type": "relative"})

    if otros_ing_tec != 0:
        label_ing = "Transf. Financiera a Técnica" if (is_retiro and otros_ing_tec < 0) else "Otros Ingresos Técnicos"
        steps.append({"name": label_ing, "amount": round(otros_ing_tec, 2), "type": "relative"})

    if otros_egr_tec != 0:
        steps.append({"name": "Otros Egresos Técnicos", "amount": round(-otros_egr_tec, 2), "type": "relative"})

    steps.append({"name": "Resultado Técnico", "amount": round(res_tec, 2), "type": "total"})
    steps.append({"name": "Resultado Financiero", "amount": round(res_fin, 2), "type": "relative"})

    if op_extraord != 0:
        steps.append({"name": "Op. Extraordinarias / Part. Terceros", "amount": round(op_extraord, 2), "type": "relative"})

    if imp_gan != 0:
        steps.append({"name": "Impuesto Ganancias", "amount": round(-imp_gan, 2), "type": "relative"})

    steps.append({"name": "Resultado Neto", "amount": round(res_neto, 2), "type": "total"})
    return steps

def get_company_subramos(df, cod_cia=None):
    """
    Extracts subramos breakdown for a company or the entire market using exact SSN
    net emission, earned premiums, and net incurred claims + rescates (Devengado Neto).
    """
    if cod_cia:
        sub_df = df[df['cod_cia'] == cod_cia]
    else:
        sub_df = df

    sub_df = sub_df[(sub_df['desc_subramo'].notna()) & (sub_df['desc_subramo'] != '')]
    if 'cod_subramo' in sub_df.columns:
        sub_df = sub_df[sub_df['cod_subramo'] != '']
    if sub_df.empty:
        return []

    grouped = sub_df.groupby(['cod_subramo', 'desc_subramo', 'cod_cuenta'], as_index=False)['importe'].sum()
    acc_by_sub = {}
    for row in grouped.itertuples(index=False):
        key = (str(row.cod_subramo), str(row.desc_subramo))
        if key not in acc_by_sub:
            acc_by_sub[key] = {}
        acc_by_sub[key][str(row.cod_cuenta)] = float(row.importe)

    records = []
    for (scod, sdesc), acc_map in acc_by_sub.items():
        comp = _extract_ssn_technical_components(acc_map, use_exact=False)
        primas_emit = comp['primas_emit']
        primas_dev = comp['primas_dev']
        siniestros = comp['siniestros_dev'] + comp['rescates']
        if primas_emit == 0.0 and primas_dev == 0.0 and siniestros == 0.0:
            continue
        base_primas = primas_dev if primas_dev > 0 else primas_emit
        siniestralidad = (siniestros / base_primas) * 100.0 if base_primas > 0 else 0.0
        records.append({
            'cod_subramo': scod,
            'desc_subramo': sdesc,
            'primas': round(primas_emit, 2),
            'primas_devengadas': round(primas_dev, 2),
            'siniestros': round(siniestros, 2),
            'siniestralidad_%': round(siniestralidad, 2),
        })

    records.sort(key=lambda r: r['primas'], reverse=True)
    return records

def get_company_investments_breakdown(df_cia):
    """
    Extracts detailed instrument allocation breakdown of account 1.02 (Inversiones)
    at Level 4 (Títulos Públicos, Acciones, FCIs, ONs, Plazos Fijos, etc.).
    """
    df_bal = df_cia[df_cia['cod_subramo'] == ''] if 'cod_subramo' in df_cia.columns else df_cia
    if df_bal.empty:
        return []

    inv4 = df_bal[df_bal['cod_cuenta'].str.startswith('1.02.01.') & df_bal['cod_cuenta'].apply(
        lambda x: len(x.split('.')) >= 4 and x.split('.')[3] != '00' and (len(x.split('.')) == 4 or x.split('.')[4] == '00')
    )]
    inv_ext = df_bal[df_bal['cod_cuenta'] == '1.02.02.00.00.00.00.00']
    combined = pd.concat([inv4, inv_ext]) if not inv_ext.empty else inv4

    if combined.empty:
        # Fallback to level 3 if level 4 is not populated
        combined = df_bal[df_bal['cod_cuenta'].str.startswith('1.02.') & df_bal['cod_cuenta'].apply(
            lambda x: len(x.split('.')) >= 3 and x.split('.')[2] != '00' and (len(x.split('.')) == 3 or x.split('.')[3] == '00')
        )]

    if combined.empty:
        return []

    grp = combined.groupby('cod_cuenta', as_index=False).agg({'desc_cuenta': 'first', 'importe': 'sum'})
    tot = grp['importe'].sum()
    grp['porcentaje'] = (grp['importe'] / tot * 100.0).round(1) if tot > 0 else 0.0
    grp = grp[grp['importe'] > 0].sort_values(by='importe', ascending=False)

    records = []
    for _, row in grp.iterrows():
        records.append({
            'cod_cuenta': str(row['cod_cuenta']),
            'desc_cuenta': str(row['desc_cuenta']),
            'importe': float(row['importe']),
            'porcentaje': float(row['porcentaje'])
        })
    return records

def get_company_investments(df_cia):
    """Returns investments breakdown as a DataFrame for Streamlit app compatibility."""
    return pd.DataFrame(get_company_investments_breakdown(df_cia))
