# 📊 Dashboard Analítico del Mercado Asegurador Argentino (SSN - SINENSUP)

Este proyecto proporciona un **Dashboard Analítico e Interactivo de 11 pestañas** (y su versión Streamlit complementaria) para el análisis integral de los estados contables de las compañías del mercado asegurador argentino bajo el régimen **SINENSUP** de la **Superintendencia de Seguros de la Nación (SSN)**.

- **Tablero Web Estático (GitHub Pages):** https://GenesisFinal.github.io/tablero-sinensup/
- **Último período procesado:** `2026-3` (cierre 30/09/2026 — **178 entidades** y **17 grupos aseguradores**, comparativo interanual vs. `2025-3` con **192 entidades** históricas/activas y **52 subramos**).

---

## 🚀 Cómo Iniciar o Actualizar el Dashboard

### Opción 1: Tablero HTML Interactivo (`index.html`, 11 Pestañas)
Abrí directamente [index.html](index.html) en cualquier navegador o publicá la última compilación en GitHub Pages:
```bash
python3 build_data.py
python3 generate_html.py
python3 deploy_to_github.py
```

### Opción 2: Actualización Automática desde SSN SINENSUP
* **macOS:** doble clic en `actualizar.command` (o `python3 ssn_updater.py`)
* **Windows:** doble clic en `actualizar.bat`

### Opción 3: Aplicación Streamlit (`app.py`, 5 Módulos)
* **macOS:** doble clic en `run_dashboard.command`
* **Windows:** doble clic en `run_dashboard.bat`
* **Terminal:**
```bash
python3 -m streamlit run app.py
```

---

## 🏛️ Estructura del Proyecto

* **`db_engine.py`**: Motor multiplataforma (`macOS` con `access_parser` parcheado / `Windows` con `pyodbc` + PowerShell) para extraer tablas Access `.mdb` de SSN con caché Parquet (`balance_cache.parquet`) validado por período y fecha de modificación.
* **`insurance_kpis.py`**: Motor contable bajo normas RGAA de la SSN con cuadre exacto (`0.00` pesos) de Primas Devengadas, Siniestros Devengados, Rescates/Rentas, Gastos, Resultado Técnico y Resultado Neto, anualización de ratios stock/flujo según trimestre fiscal, desglose de Inversiones (`1.02`) y subramos.
* **`build_data.py`**: Genera `data_sinensup.json` consolidando las compañías individuales, 17 grupos aseguradores con consolidación RT 21 y eliminación de VPP intra-grupo (sin doble cómputo de resultados ni patrimonio), benchmarks de mercado y segmentos, árbol completo del Plan de Cuentas SSN y comparativo interanual (`2026-3` vs `2025-3`) con IPC INDEC de referencia.
* **`generate_html.py`**: Compila `index.html` autocontenido con las 11 pestañas interactivas, Modo Claro / Modo Oscuro y exportaciones CSV/PNG.
* **`ssn_updater.py` / `deploy_to_github.py`**: Descarga nuevos períodos trimestrales `.mdb` desde SSN SINENSUP y publica el tablero actualizado en GitHub Pages.
* **`app.py` / `charts.py`**: Versión interactiva en Streamlit y sus gráficos Plotly.

---

## 📑 Pestañas del Tablero (`index.html`)

1. **🌐 Visión Mercado:** Distribución institucional y por línea real de productos, matriz estratégica de 4 cuadrantes (Grupos y Compañías), Top 15, ranking consolidado de grupos con modales de detalle y base completa de entidades.
2. **🏢 Ficha de Aseguradora / Grupo:** Scorecard individual o de grupo, gráfico en cascada (*Waterfall*) del Estado de Resultados hasta Resultado Neto, composición de Activo y Pasivo/PN e impacto VPP.
3. **🛡️ Ramos y Suscripción:** Emisión directa neta, primas devengadas y siniestralidad devengada por subramo.
4. **🏆 Rankings por Rama:** Participación de mercado, peso por subramo y ranking por macro-sección/ramo/subramo para grupos o aseguradoras.
5. **🔬 Análisis por Ramo:** Ratio combinado apilado Top 15, radar de 6 ejes vs. mercado y tabla técnica completa por ramo.
6. **⚖️ Comparativo de Mercado:** Evolución interanual (`Sep-26 vs Sep-25`) en cifras nominales o ajustadas por inflación (AXI), variación de share y ratios técnicos.
7. **📈 Inversiones y Finanzas:** Desglose multinivel de la cartera de inversiones (`1.02`), ROI, VPP y rankings de activos e inversiones.
8. **⚖️ Solvencia y Ratios SSN:** Cobertura de compromisos técnicos, apalancamiento anualizado, cobranza de premios y ranking de solvencia.
9. **🎯 Ratios de Gestión:** Scorecard de 14 KPIs con semáforos, gráfico radar, diagnóstico ejecutivo y filtros de alerta temprana.
10. **📒 Balances Contables:** Árbol jerárquico navegable del Plan de Cuentas oficial SSN (Patrimonial, EDR, Técnico, Financiero y por Subramo) para mercado, segmento, grupo o entidad.
11. **🔀 Flujo de Resultados (Sankey):** Trazabilidad completa con conservación exacta de flujo desde Emisión hasta Resultado Neto.
