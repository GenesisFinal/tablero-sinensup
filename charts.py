import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def format_ars(val):
    """Format large numbers into human-readable millions/billions."""
    if abs(val) >= 1e12:
        return f"${val/1e12:,.2f} B"
    elif abs(val) >= 1e9:
        return f"${val/1e9:,.2f} MM"
    elif abs(val) >= 1e6:
        return f"${val/1e6:,.2f} M"
    else:
        return f"${val:,.0f}"

def plot_waterfall_results(steps, company_name=""):
    """Plot Plotly waterfall for income statement."""
    x = [s["name"] for s in steps]
    y = [s["amount"] for s in steps]
    measure = ["relative" if s["type"] == "relative" else "total" for s in steps]
    text = [format_ars(v) for v in y]

    fig = go.Figure(go.Waterfall(
        name="Resultados",
        orientation="v",
        measure=measure,
        x=x,
        textposition="outside",
        text=text,
        y=y,
        connector={"line": {"color": "#4A5568"}},
        decreasing={"marker": {"color": "#E53E3E"}},
        increasing={"marker": {"color": "#38A169"}},
        totals={"marker": {"color": "#3182CE"}}
    ))

    fig.update_layout(
        title=f"Estado de Resultados: Cascada de Rentabilidad - {company_name}",
        waterfallgap=0.3,
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        yaxis=dict(title="Importe (ARS)", showgrid=True, gridcolor="#EDF2F7")
    )
    return fig

def plot_market_matrix(df_summary):
    """Scatter plot: Technical margin vs. Financial margin."""
    df_plot = df_summary[df_summary['primas_devengadas'] > 0].copy()
    # Clip extreme outliers for visual clarity
    df_plot['margen_tecnico_plot'] = df_plot['margen_tecnico'].clip(-150, 150)
    df_plot['roi_inversiones_plot'] = df_plot['roi_inversiones'].clip(-50, 100)

    fig = px.scatter(
        df_plot,
        x="margen_tecnico_plot",
        y="roi_inversiones_plot",
        size="primas_devengadas",
        color="tipo_entidad",
        hover_name="razon_social",
        hover_data={
            "primas_devengadas": ":,.0f",
            "resultado_tecnico": ":,.0f",
            "resultado_financiero": ":,.0f",
            "combined_ratio": ":.2f",
            "margen_tecnico_plot": False,
            "roi_inversiones_plot": False
        },
        labels={
            "margen_tecnico_plot": "Margen Técnico (%)",
            "roi_inversiones_plot": "Rendimiento Financiero s/ Inversiones (%)",
            "tipo_entidad": "Tipo de Entidad"
        },
        title="Matriz Estratégica: Margen Técnico vs. Rendimiento Financiero",
        template="plotly_white"
    )

    fig.add_hline(y=0, line_dash="dash", line_color="#718096")
    fig.add_vline(x=0, line_dash="dash", line_color="#718096")

    # Annotate quadrants
    fig.add_annotation(x=60, y=50, text="<b>Cuadrante 1: Ganadoras Integrales</b><br>(Técnico + / Financiero +)", showarrow=False, font=dict(color="#276749", size=10))
    fig.add_annotation(x=-70, y=50, text="<b>Cuadrante 2: Dependencia Financiera</b><br>(Técnico - / Financiero +)", showarrow=False, font=dict(color="#D69E2E", size=10))
    fig.add_annotation(x=60, y=-25, text="<b>Cuadrante 3: Técnicas Puras</b><br>(Técnico + / Financiero -)", showarrow=False, font=dict(color="#0369A1", size=10))
    fig.add_annotation(x=-70, y=-25, text="<b>Cuadrante 4: En Riesgo Operativo</b><br>(Técnico - / Financiero -)", showarrow=False, font=dict(color="#C53030", size=10))

    fig.update_layout(height=550, margin=dict(l=40, r=40, t=60, b=40))
    return fig

def plot_asset_liability_donuts(row_cia):
    """Plots side-by-side donut charts for assets and liabilities/equity."""
    # Assets
    asset_labels = ['Disponibilidades', 'Inversiones', 'Créditos', 'Inmuebles', 'Bienes de Uso y Otros']
    asset_vals = [
        max(0, row_cia['disponibilidades']),
        max(0, row_cia['inversiones']),
        max(0, row_cia['creditos']),
        max(0, row_cia['inmuebles']),
        max(0, row_cia['otros_activos'] + row_cia['bienes_uso'])
    ]

    fig_a = go.Figure(data=[go.Pie(
        labels=asset_labels,
        values=asset_vals,
        hole=0.45,
        textinfo="label+percent",
        marker_colors=['#4299E1', '#48BB78', '#ECC94B', '#ED8936', '#A0AEC0']
    )])
    fig_a.update_layout(
        title="Composición del Activo",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white",
        showlegend=False
    )

    # Liabilities & Equity
    liab_labels = ['Deudas', 'Compromisos Técnicos (Reservas)', 'Previsiones', 'Patrimonio Neto']
    liab_vals = [
        max(0, row_cia['deudas']),
        max(0, row_cia['compromisos_tecnicos']),
        max(0, row_cia['previsiones']),
        max(0, row_cia['patrimonio_neto'])
    ]

    fig_l = go.Figure(data=[go.Pie(
        labels=liab_labels,
        values=liab_vals,
        hole=0.45,
        textinfo="label+percent",
        marker_colors=['#F56565', '#9F7AEA', '#ED8936', '#38B2AC']
    )])
    fig_l.update_layout(
        title="Composición de Pasivo y Patrimonio Neto",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly_white",
        showlegend=False
    )
    return fig_a, fig_l

def plot_subramos_bar(df_subramos, title="Producción y Siniestralidad por Ramo"):
    """Bar chart for production and loss ratio per subramo."""
    top_sub = df_subramos.head(15).copy()
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_sub['desc_subramo'],
        y=top_sub['primas'],
        name="Primas Emitidas (ARS)",
        marker_color="#3182CE",
        yaxis="y"
    ))

    fig.add_trace(go.Scatter(
        x=top_sub['desc_subramo'],
        y=top_sub['siniestralidad_%'],
        name="Siniestralidad (%)",
        marker_color="#E53E3E",
        mode="lines+markers",
        yaxis="y2"
    ))

    fig.update_layout(
        title=title,
        height=450,
        margin=dict(l=40, r=40, t=50, b=100),
        template="plotly_white",
        xaxis=dict(tickangle=-45),
        yaxis=dict(title="Primas (ARS)", showgrid=True),
        yaxis2=dict(title="Siniestralidad (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_investments_pie(df_inv, title="Composición de Inversiones"):
    """Pie chart of investment portfolio breakdown."""
    fig = px.pie(
        df_inv,
        names="desc_cuenta",
        values="importe",
        title=title,
        hole=0.4,
        template="plotly_white"
    )
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig
