import streamlit as st
import pandas as pd
import numpy as np
from db_engine import get_balance_data
from insurance_kpis import (
    compute_all_companies_summary,
    get_company_waterfall_data,
    get_company_subramos,
    get_company_investments
)
from charts import (
    format_ars,
    plot_waterfall_results,
    plot_market_matrix,
    plot_asset_liability_donuts,
    plot_subramos_bar,
    plot_investments_pie
)

# Page configuration
st.set_page_config(
    page_title="Dashboard Mercado Asegurador | SSN SINENSUP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive look & feel
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 5px solid #3182CE;
    }
    .metric-title { font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.4rem; color: #1E293B; font-weight: 700; margin-top: 4px; }
    .metric-sub { font-size: 0.8rem; color: #10B981; margin-top: 2px; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: #FFFFFF;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3182CE !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_all():
    df = get_balance_data()
    summary = compute_all_companies_summary(df)
    return df, summary

with st.spinner("Cargando y procesando base de balances de la SSN..."):
    df_raw, df_summary = load_all()

# Header
st.title("📊 Dashboard Ejecutivo del Mercado Asegurador Argentino")
st.caption(f"Fuente: Balances SSN - Régimen SINENSUP (Período: {df_raw['periodo'].iloc[0]}) | Total Entidades: {len(df_summary)}")

# Sidebar Filters
st.sidebar.header("🔍 Filtros y Segmentación")
tipo_entidad_list = ["Todos"] + sorted(df_summary['tipo_entidad'].unique().tolist())
selected_tipo = st.sidebar.selectbox("Tipo de Entidad / Segmento:", tipo_entidad_list)

if selected_tipo != "Todos":
    df_filtered_summary = df_summary[df_summary['tipo_entidad'] == selected_tipo].copy()
    df_filtered_raw = df_raw[df_raw['tipo_entidad'] == selected_tipo].copy()
else:
    df_filtered_summary = df_summary.copy()
    df_filtered_raw = df_raw.copy()

# Company search & selector
st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Selección de Aseguradora")
company_options = sorted(df_filtered_summary['razon_social'].tolist())
selected_company_name = st.sidebar.selectbox("Aseguradora para Análisis Detallado:", company_options)
selected_cia_row = df_filtered_summary[df_filtered_summary['razon_social'] == selected_company_name].iloc[0]
selected_cia_code = selected_cia_row['cod_cia']
df_cia_raw = df_raw[df_raw['cod_cia'] == selected_cia_code]

# Tabs definition
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 1. Visión Mercado",
    "🏢 2. Ficha de la Aseguradora",
    "🛡️ 3. Ramos y Suscripción",
    "📈 4. Inversiones y Finanzas",
    "⚖️ 5. Solvencia y Ratios SSN"
])

# ----------------------------------------------------
# TAB 1: VISIÓN GENERAL DEL MERCADO
# ----------------------------------------------------
with tab1:
    st.subheader(f"Resumen Global del Mercado ({selected_tipo})")

    # Global KPI cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    tot_primas_dev = df_filtered_summary['primas_devengadas'].sum()
    tot_primas_emit = df_filtered_summary['primas_emitidas'].sum()
    tot_activos = df_filtered_summary['activo'].sum()
    tot_inversiones = df_filtered_summary['inversiones'].sum()
    tot_res_tecnico = df_filtered_summary['resultado_tecnico'].sum()
    tot_res_neto = df_filtered_summary['resultado_neto'].sum()

    tot_prestaciones = df_filtered_summary['siniestros'].sum() + df_filtered_summary['rescates'].sum()
    m_loss_ratio = (tot_prestaciones / tot_primas_dev * 100) if tot_primas_dev > 0 else 0
    m_combined_ratio = ((tot_prestaciones + df_filtered_summary['gtos_produccion'].sum() + df_filtered_summary['gtos_explotacion'].sum()) / tot_primas_dev * 100) if tot_primas_dev > 0 else 0

    kpi_col1.metric("Primas Devengadas", format_ars(tot_primas_dev))
    kpi_col2.metric("Primas Emitidas", format_ars(tot_primas_emit))
    kpi_col3.metric("Activo Total", format_ars(tot_activos))
    kpi_col4.metric("Siniestralidad Prom.", f"{m_loss_ratio:.1f}%")
    kpi_col5.metric("Ratio Combinado", f"{m_combined_ratio:.1f}%")
    kpi_col6.metric("Resultado Neto", format_ars(tot_res_neto))

    st.markdown("---")

    col_m1, col_m2 = st.columns([3, 2])
    with col_m1:
        st.plotly_chart(plot_market_matrix(df_filtered_summary), use_container_width=True)
    
    with col_m2:
        st.subheader("🏆 Top Aseguradoras por Primas Devengadas")
        top_prod = df_filtered_summary.sort_values(by='primas_devengadas', ascending=False).head(10)[['razon_social', 'primas_devengadas', 'resultado_tecnico', 'resultado_neto', 'combined_ratio']].copy()
        top_prod['Primas Devengadas'] = top_prod['primas_devengadas'].apply(format_ars)
        top_prod['Res. Técnico'] = top_prod['resultado_tecnico'].apply(format_ars)
        top_prod['Res. Neto'] = top_prod['resultado_neto'].apply(format_ars)
        top_prod['Ratio Combinado'] = top_prod['combined_ratio'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(top_prod[['razon_social', 'Primas Devengadas', 'Res. Técnico', 'Res. Neto', 'Ratio Combinado']], hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Tabla General de Entidades del Segmento")
    display_df = df_filtered_summary[['cod_cia', 'razon_social', 'tipo_entidad', 'activo', 'inversiones', 'patrimonio_neto', 'primas_devengadas', 'resultado_tecnico', 'resultado_financiero', 'resultado_neto', 'combined_ratio', 'cobertura_reservas']].copy()
    display_df = display_df.sort_values(by='primas_devengadas', ascending=False)
    st.dataframe(display_df, use_container_width=True, height=350)
    
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Datos del Mercado en CSV", csv_data, "mercado_asegurador_ssn.csv", "text/csv")

# ----------------------------------------------------
# TAB 2: FICHA DETALLADA POR COMPAÑÍA
# ----------------------------------------------------
with tab2:
    st.subheader(f"🏢 Ficha Técnica: {selected_company_name} (Cód. SSN: {selected_cia_code})")
    st.caption(f"Segmento: **{selected_cia_row['tipo_entidad']}** | Período: **{df_raw['periodo'].iloc[0]}**")

    # Company KPI cards
    c_col1, c_col2, c_col3, c_col4, c_col5 = st.columns(5)
    c_col1.metric("Primas Devengadas", format_ars(selected_cia_row['primas_devengadas']))
    c_col2.metric("Siniestralidad Dev.", f"{selected_cia_row['loss_ratio']:.1f}%")
    c_col3.metric("Ratio Combinado", f"{selected_cia_row['combined_ratio']:.1f}%")
    c_col4.metric("Resultado Técnico", format_ars(selected_cia_row['resultado_tecnico']))
    c_col5.metric("Resultado Neto", format_ars(selected_cia_row['resultado_neto']))

    st.markdown("---")
    
    # Waterfall Chart
    waterfall_steps = get_company_waterfall_data(df_cia_raw)
    fig_wf = plot_waterfall_results(waterfall_steps, company_name=selected_company_name)
    st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown("---")
    # Asset and Liability Donut charts
    st.subheader("🏛️ Estructura de Balance Patrimonial")
    fig_a, fig_l = plot_asset_liability_donuts(selected_cia_row)
    c_don1, c_don2 = st.columns(2)
    with c_don1:
        st.plotly_chart(fig_a, use_container_width=True)
    with c_don2:
        st.plotly_chart(fig_l, use_container_width=True)

# ----------------------------------------------------
# TAB 3: RAMOS Y LÍNEAS DE NEGOCIO
# ----------------------------------------------------
with tab3:
    st.subheader("🛡️ Desglose de Producción y Siniestralidad por Ramo")
    
    scope_option = st.radio("Alcance del Análisis:", ["Aseguradora Seleccionada", "Mercado Consolidado"], horizontal=True)
    
    if scope_option == "Aseguradora Seleccionada":
        df_sub = pd.DataFrame(get_company_subramos(df_raw, cod_cia=selected_cia_code))
        st.caption(f"Distribución de Ramos para: **{selected_company_name}**")
    else:
        df_sub = pd.DataFrame(get_company_subramos(df_filtered_raw))
        st.caption(f"Distribución de Ramos para el Mercado ({selected_tipo})")

    if not df_sub.empty:
        fig_sub = plot_subramos_bar(df_sub, title=f"Producción y Siniestralidad por Subramo ({scope_option})")
        st.plotly_chart(fig_sub, use_container_width=True)

        st.subheader("Detalle Numérico por Subramo")
        df_sub_disp = df_sub.copy()
        df_sub_disp['Primas Emitidas (ARS)'] = df_sub_disp['primas'].apply(format_ars)
        df_sub_disp['Siniestros (ARS)'] = df_sub_disp['siniestros'].apply(format_ars)
        df_sub_disp['Siniestralidad (%)'] = df_sub_disp['siniestralidad_%'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_sub_disp[['cod_subramo', 'desc_subramo', 'Primas Emitidas (ARS)', 'Siniestros (ARS)', 'Siniestralidad (%)']], hide_index=True, use_container_width=True)
    else:
        st.info("No se registran subramos clasificados para la selección actual.")

# ----------------------------------------------------
# TAB 4: PORTAFOLIO DE INVERSIONES Y FINANZAS
# ----------------------------------------------------
with tab4:
    st.subheader(f"📈 Portafolio de Inversiones y Rendimiento Financiero: {selected_company_name}")
    
    df_inv = get_company_investments(df_cia_raw)
    
    i_col1, i_col2 = st.columns([1, 1])
    with i_col1:
        st.metric("Total Inversiones (1.02)", format_ars(selected_cia_row['inversiones']))
        st.metric("Resultado Financiero Neto", format_ars(selected_cia_row['resultado_financiero']))
        st.metric("Rendimiento s/ Cartera (ROI)", f"{selected_cia_row['roi_inversiones']:.2f}%")
        
        if not df_inv.empty:
            st.dataframe(df_inv, hide_index=True, use_container_width=True)
    
    with i_col2:
        if not df_inv.empty:
            fig_inv = plot_investments_pie(df_inv, title="Composición del Portafolio de Inversiones")
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.info("No hay desglose de inversiones de nivel 4/3 disponible para esta entidad.")

# ----------------------------------------------------
# TAB 5: SOLVENCIA Y RATIOS REGULATORIOS SSN
# ----------------------------------------------------
with tab5:
    st.subheader("⚖️ Indicadores de Solvencia, Cobertura y Ratios SSN")
    
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    s_col1.metric("Cobertura de Compromisos Técnicos", f"{selected_cia_row['cobertura_reservas']:.2f}x", delta="Superávit" if selected_cia_row['cobertura_reservas'] >= 1.0 else "Déficit")
    s_col2.metric("Apalancamiento de Primas (Primas Anualiz./PN)", f"{selected_cia_row['apalancamiento']:.2f}x")
    s_col3.metric("Premios a Cobrar / Primas Emitidas Anualiz.", f"{selected_cia_row['calidad_cartera']:.1f}%")
    s_col4.metric("Patrimonio Neto", format_ars(selected_cia_row['patrimonio_neto']))

    st.markdown("---")
    st.subheader("📊 Ranking de Solvencia y Ratio Combinado en el Mercado")
    
    solv_df = df_filtered_summary[['razon_social', 'cobertura_reservas', 'combined_ratio', 'apalancamiento', 'patrimonio_neto', 'activo']].sort_values(by='cobertura_reservas', ascending=False).copy()
    solv_df['Cobertura (x)'] = solv_df['cobertura_reservas'].apply(lambda x: f"{x:.2f}x")
    solv_df['Ratio Combinado'] = solv_df['combined_ratio'].apply(lambda x: f"{x:.1f}%")
    solv_df['Apalancamiento'] = solv_df['apalancamiento'].apply(lambda x: f"{x:.2f}x")
    solv_df['Patrimonio Neto'] = solv_df['patrimonio_neto'].apply(format_ars)
    solv_df['Activo Total'] = solv_df['activo'].apply(format_ars)
    
    st.dataframe(solv_df[['razon_social', 'Cobertura (x)', 'Ratio Combinado', 'Apalancamiento', 'Patrimonio Neto', 'Activo Total']], hide_index=True, use_container_width=True)
