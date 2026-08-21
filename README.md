# 📊 Dashboard Analítico del Mercado Asegurador Argentino (SSN - SINENSUP)

Este proyecto proporciona un **Dashboard Analítico e Interactivo** para el análisis integral de balances de las compañías del mercado asegurador argentino, basado en la base de datos oficial de la **Superintendencia de Seguros de la Nación (SSN)** bajo el régimen **SINENSUP**.

---

## 🚀 Cómo Iniciar el Dashboard

### Opción 1: Con el lanzador automático
Doble clic en el archivo:
```text
run_dashboard.bat
```

### Opción 2: Desde la terminal / PowerShell
```bash
python -m streamlit run app.py
```
El dashboard se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 🏛️ Estructura del Proyecto

* **`app.py`**: Aplicación web interactiva en Streamlit estructurada en 5 módulos analíticos.
* **`db_engine.py`**: Motor de extracción y transformación de datos desde `2026-2.mdb` con almacenamiento en caché `Parquet` para respuesta en milisegundos.
* **`insurance_kpis.py`**: Motor de cálculo contable asegurador bajo normas SSN (Primas devengadas, siniestros devengados, rescates, ratios combinados, solvencia).
* **`charts.py`**: Generador de gráficos interactivos Plotly (Gráfico en cascada *Waterfall*, matriz estratégica de 4 cuadrantes, gráficos de dona patrimoniales, barras de subramos).
* **`2026-2.mdb`**: Base de datos de Access con 294.245 registros oficiales del mercado asegurador.

---

## 📑 Módulos del Dashboard

1. **🌐 1. Visión Mercado:**
   * Resumen macro del mercado, primas devengadas, primas emitidas, siniestralidad media y resultado consolidado.
   * Matriz estratégica de 4 cuadrantes: Margen Técnico (%) vs. Rendimiento Financiero (%).
   * Ranking del Top 10 / 20 por primas devengadas y activos.
   * Exportación de la base de mercado en formato CSV.

2. **🏢 2. Ficha de la Aseguradora:**
   * Selector interactivo de cualquiera de las 185 aseguradoras.
   * Gráfico de cascada (*Waterfall Chart*) que detalla el camino desde los ingresos técnicos devengados hasta el resultado neto final.
   * Estructura del activo (disponibilidades, inversiones, créditos, inmuebles) y pasivo (deudas vs. reservas técnicas).

3. **🛡️ 3. Ramos y Suscripción:**
   * Análisis por subramo (Automotores, ART, Vida Colectivo, Vida Individual, Retiro, Incendio, Caución, etc.).
   * Comparativa de volumen de emisión y siniestralidad devengada (%) por ramo para la aseguradora seleccionada o para el mercado consolidado.

4. **📈 4. Inversiones y Finanzas:**
   * Cartera de inversiones detallada a nivel de subcuentas (Títulos Públicos, Obligaciones Negociables, Plazos Fijos, FCI, Fideicomisos).
   * Desglose del resultado financiero neto y cálculo del retorno sobre inversiones (ROI).

5. **⚖️ 5. Solvencia y Ratios SSN:**
   * Cobertura de compromisos técnicos e IBNR.
   * Apalancamiento patrimonial y calidad de cobranza.
   * Ranking de solvencia y ratio combinado de todo el mercado asegurador.
