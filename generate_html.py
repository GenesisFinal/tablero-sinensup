import json
import os

def generate_html():
    json_path = r"g:\Mi unidad\IA\Sinensup\data_sinensup.json"
    with open(json_path, "r", encoding="utf-8") as f:
        raw_json_str = f.read()

    html_content = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard Mercado Asegurador Argentino • SSN SINENSUP</title>
  
  <!-- Cache Control -->
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <meta name="theme-color" content="#0F172A">

  <!-- Google Fonts: Sora & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Sora:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- Chart.js & Plotly.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Sora"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace']
          }},
          colors: {{
            brand: {{
              red: '#E20039',
              blue: '#38BDF8',
              navy: '#0F172A',
              card: '#1E293B',
              border: '#334155',
              green: '#10B981',
              gold: '#F59E0B'
            }}
          }}
        }}
      }}
    }}
  </script>

  <style>
    body {{
      font-family: 'Sora', sans-serif;
      background-color: #0B1120;
      color: #F1F5F9;
    }}
    .font-mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .glass-card {{
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(51, 65, 85, 0.6);
    }}
    .tab-btn.active {{
      background-color: #E20039;
      color: #FFFFFF;
      box-shadow: 0 4px 14px rgba(226, 0, 57, 0.4);
    }}
    /* Custom Scrollbars */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0F172A;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-brand-red selection:text-white">

  <!-- TOP NAVIGATION HEADER -->
  <header class="sticky top-0 z-50 bg-[#0F172A]/90 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      
      <!-- Brand & Title -->
      <div class="flex items-center space-x-3.5">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-red to-rose-700 flex items-center justify-center shadow-lg shadow-brand-red/30">
          <i class="fa-solid fa-shield-halved text-white text-lg"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-bold tracking-tight text-white">Mercado Asegurador Argentino</h1>
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 bg-brand-red/20 text-brand-red border border-brand-red/30 rounded-full font-bold">SSN SINENSUP</span>
          </div>
          <p class="text-xs text-slate-400">Balances Oficiales • Período <span id="headerPeriodo" class="font-mono text-slate-300 font-semibold">2026-2</span> • <span id="headerTotalCias" class="font-mono text-brand-blue font-semibold">185</span> Compañías</p>
        </div>
      </div>

      <!-- Quick Actions / Company Quick Search -->
      <div class="flex items-center gap-3">
        <div class="relative w-64 md:w-80">
          <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <input type="text" id="globalCompanySearch" placeholder="Buscar aseguradora..." 
                 class="w-full pl-9 pr-3 py-1.5 bg-slate-900/90 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-brand-red transition-all">
          <div id="searchResultsDropdown" class="hidden absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl max-h-60 overflow-y-auto z-50 text-xs"></div>
        </div>
        
        <button onclick="exportToCSV()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors flex items-center gap-2">
          <i class="fa-solid fa-file-csv text-brand-green"></i> Exportar CSV
        </button>
      </div>

    </div>

    <!-- NAVIGATION TABS -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-800/60 flex items-center gap-2 overflow-x-auto py-2">
      <button onclick="switchTab('vision-mercado')" id="tabBtn-vision-mercado" class="tab-btn active px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all">
        <i class="fa-solid fa-chart-pie"></i> 1. Visión Mercado
      </button>
      <button onclick="switchTab('ficha-compania')" id="tabBtn-ficha-compania" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-building"></i> 2. Ficha de Aseguradora
      </button>
      <button onclick="switchTab('ramos-suscripcion')" id="tabBtn-ramos-suscripcion" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-shield-heart"></i> 3. Ramos y Suscripción
      </button>
      <button onclick="switchTab('inversiones-finanzas')" id="tabBtn-inversiones-finanzas" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-chart-line"></i> 4. Inversiones y Finanzas
      </button>
      <button onclick="switchTab('solvencia-ratios')" id="tabBtn-solvencia-ratios" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-scale-balanced"></i> 5. Solvencia y Ratios SSN
      </button>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">

    <!-- ======================================================== -->
    <!-- TAB 1: VISIÓN MERCADO -->
    <!-- ======================================================== -->
    <section id="tab-vision-mercado" class="space-y-6">
      
      <!-- Segment Filter Pills -->
      <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-filter text-brand-red"></i> Segmento:</span>
          <div id="segmentPillsContainer" class="flex flex-wrap gap-1.5"></div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades filtradas: <span id="filteredCiasCount" class="font-mono font-bold text-white">185</span>
        </div>
      </div>

      <!-- Macro KPI Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Primas Devengadas</div>
          <div id="kpiPrimasDev" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Base Técnica 100%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-slate-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Primas Emitidas</div>
          <div id="kpiPrimasEmit" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Emisión Bruta</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Activo Administrado</div>
          <div id="kpiActivos" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Total Activo</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Siniestralidad Dev.</div>
          <div id="kpiLossRatio" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Loss Ratio Medio</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Ratio Combinado</div>
          <div id="kpiCombinedRatio" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Técnico + Gastos</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-indigo-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Resultado Neto</div>
          <div id="kpiResNeto" class="text-lg font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Consolidado Final</div>
        </div>
      </div>

      <!-- Interactive Strategic Matrix & Top Rankings -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Scatter Plot Matrix -->
        <div class="lg:col-span-7 glass-card p-5 rounded-xl">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 class="text-sm font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-crosshairs text-brand-red"></i> Matriz Estratégica: Margen Técnico vs. Rendimiento Financiero
              </h3>
              <p class="text-xs text-slate-400">Burbuja = Volumen de Primas Devengadas | Ejes centrados en 0%</p>
            </div>
          </div>
          <div id="marketScatterPlot" class="w-full h-96"></div>
        </div>

        <!-- Top Ranking Table -->
        <div class="lg:col-span-5 glass-card p-5 rounded-xl flex flex-col">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-trophy text-amber-400"></i> Top Aseguradoras (Primas Devengadas)
            </h3>
            <span class="text-xs text-slate-400">Top 10</span>
          </div>
          <div class="overflow-y-auto flex-1 max-h-96">
            <table class="w-full text-left text-xs">
              <thead class="text-slate-400 border-b border-slate-700 bg-slate-900/50 sticky top-0">
                <tr>
                  <th class="py-2 px-2">Aseguradora</th>
                  <th class="py-2 px-2 text-right">Primas Dev.</th>
                  <th class="py-2 px-2 text-right">Ratio Comb.</th>
                  <th class="py-2 px-2 text-right">Res. Neto</th>
                </tr>
              </thead>
              <tbody id="topRankingTableBody" class="divide-y divide-slate-800"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Comprehensive Market Table -->
      <div class="glass-card p-5 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-table-list text-brand-blue"></i> Tabla Consolidada del Mercado Asegurador
          </h3>
          <input type="text" id="marketTableFilter" oninput="renderMarketTable()" placeholder="Filtrar por nombre o código..." 
                 class="px-3 py-1 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-brand-blue">
        </div>
        <div class="overflow-x-auto max-h-[450px]">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="text-slate-400 bg-slate-900 sticky top-0 z-10 border-b border-slate-700">
              <tr>
                <th class="py-2.5 px-3">Cód</th>
                <th class="py-2.5 px-3">Razón Social</th>
                <th class="py-2.5 px-3">Segmento</th>
                <th class="py-2.5 px-3 text-right">Primas Dev.</th>
                <th class="py-2.5 px-3 text-right">Siniestros</th>
                <th class="py-2.5 px-3 text-right">Loss Ratio</th>
                <th class="py-2.5 px-3 text-right">Comb. Ratio</th>
                <th class="py-2.5 px-3 text-right">Res. Técnico</th>
                <th class="py-2.5 px-3 text-right">Res. Financiero</th>
                <th class="py-2.5 px-3 text-right">Res. Neto</th>
                <th class="py-2.5 px-3 text-right">Activo</th>
                <th class="py-2.5 px-3 text-center">Acción</th>
              </tr>
            </thead>
            <tbody id="marketFullTableBody" class="divide-y divide-slate-800 font-mono"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 2: FICHA DE LA ASEGURADORA -->
    <!-- ======================================================== -->
    <section id="tab-ficha-compania" class="hidden space-y-6">
      
      <!-- Company Selector Header -->
      <div class="glass-card p-5 rounded-xl border-l-4 border-l-brand-red flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="selectedCiaTitle" class="text-lg font-bold text-white">...</h2>
            <span id="selectedCiaBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-brand-red/20 text-brand-red border border-brand-red/30">...</span>
          </div>
          <p class="text-xs text-slate-400 mt-1">Código SSN: <span id="selectedCiaCode" class="font-mono text-white font-bold">...</span> | Período: <span class="font-mono text-slate-300">2026-2</span></p>
        </div>
        
        <div class="flex items-center gap-3">
          <select id="companyDropdownSelect" onchange="onCompanyDropdownChange(this.value)" 
                  class="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-brand-red"></select>
        </div>
      </div>

      <!-- Company Mini KPI Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
        <div class="glass-card p-4 rounded-xl">
          <div class="text-[11px] font-semibold text-slate-400">PRIMAS DEVENGADAS</div>
          <div id="ciaKpiPrimasDev" class="text-base font-bold font-mono text-white mt-1">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl">
          <div class="text-[11px] font-semibold text-slate-400">RATIO COMBINADO</div>
          <div id="ciaKpiCombined" class="text-base font-bold font-mono text-white mt-1">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl">
          <div class="text-[11px] font-semibold text-slate-400">RESULTADO TÉCNICO</div>
          <div id="ciaKpiResTec" class="text-base font-bold font-mono text-white mt-1">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl">
          <div class="text-[11px] font-semibold text-slate-400">RESULTADO FINANCIERO</div>
          <div id="ciaKpiResFin" class="text-base font-bold font-mono text-white mt-1">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl">
          <div class="text-[11px] font-semibold text-slate-400">RESULTADO NETO</div>
          <div id="ciaKpiResNeto" class="text-base font-bold font-mono text-white mt-1">...</div>
        </div>
      </div>

      <!-- Waterfall Chart -->
      <div class="glass-card p-5 rounded-xl">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-waterfall text-brand-blue"></i> Estado de Resultados: Cascada de Rentabilidad
            </h3>
            <p class="text-xs text-slate-400">Evolución contable desde Ingresos Técnicos Devengados hasta Resultado Neto</p>
          </div>
        </div>
        <div id="ciaWaterfallPlot" class="w-full h-96"></div>
      </div>

      <!-- Balance Sheet Breakdown Donuts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="glass-card p-5 rounded-xl">
          <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <i class="fa-solid fa-chart-pie text-emerald-400"></i> Composición del Activo
          </h3>
          <div id="ciaAssetDonut" class="w-full h-72"></div>
        </div>

        <div class="glass-card p-5 rounded-xl">
          <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <i class="fa-solid fa-chart-pie text-purple-400"></i> Composición de Pasivo y Patrimonio Neto
          </h3>
          <div id="ciaLiabDonut" class="w-full h-72"></div>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 3: RAMOS Y SUSCRIPCIÓN -->
    <!-- ======================================================== -->
    <section id="tab-ramos-suscripcion" class="hidden space-y-6">
      <div class="glass-card p-5 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-shield-virus text-brand-red"></i> Distribución de Producción y Siniestralidad por Ramo
            </h3>
            <p class="text-xs text-slate-400">Barras = Primas Emitidas (ARS) | Línea = Siniestralidad Devengada (%)</p>
          </div>
          <div class="flex items-center gap-2 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs">
            <button onclick="setRamosScope('cia')" id="ramosScopeCiaBtn" class="px-3 py-1 rounded bg-brand-red text-white font-semibold">Aseguradora Seleccionada</button>
            <button onclick="setRamosScope('market')" id="ramosScopeMarketBtn" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">Mercado Consolidado</button>
          </div>
        </div>
        
        <div id="subramosBarChart" class="w-full h-96"></div>
      </div>

      <!-- Subramos Numerical Table -->
      <div class="glass-card p-5 rounded-xl">
        <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <i class="fa-solid fa-list-check text-brand-blue"></i> Detalle Numérico por Subramo
        </h3>
        <div class="overflow-x-auto max-h-80">
          <table class="w-full text-left text-xs">
            <thead class="text-slate-400 bg-slate-900 sticky top-0 border-b border-slate-700">
              <tr>
                <th class="py-2.5 px-3">Cód Subramo</th>
                <th class="py-2.5 px-3">Descripción del Subramo</th>
                <th class="py-2.5 px-3 text-right">Primas Emitidas (ARS)</th>
                <th class="py-2.5 px-3 text-right">Siniestros (ARS)</th>
                <th class="py-2.5 px-3 text-right">Siniestralidad (%)</th>
              </tr>
            </thead>
            <tbody id="subramosTableBody" class="divide-y divide-slate-800 font-mono"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 4: INVERSIONES Y FINANZAS -->
    <!-- ======================================================== -->
    <section id="tab-inversiones-finanzas" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-5 glass-card p-5 rounded-xl space-y-4">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-coins text-amber-400"></i> Métricas Financieras: <span id="invCiaName" class="text-brand-blue font-mono">...</span>
          </h3>
          
          <div class="space-y-3 font-mono text-xs">
            <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex justify-between items-center">
              <span class="text-slate-400">Total Inversiones (1.02):</span>
              <span id="invTotalVal" class="text-white font-bold text-sm">...</span>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex justify-between items-center">
              <span class="text-slate-400">Resultado Financiero Neto:</span>
              <span id="invResFinVal" class="text-white font-bold text-sm">...</span>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex justify-between items-center">
              <span class="text-slate-400">Rendimiento s/ Inversiones (ROI):</span>
              <span id="invRoiVal" class="text-emerald-400 font-bold text-sm">...</span>
            </div>
          </div>

          <div class="mt-4">
            <h4 class="text-xs font-semibold text-slate-300 uppercase mb-2">Desglose de Cartera (Nivel 3)</h4>
            <div class="overflow-y-auto max-h-56">
              <table class="w-full text-left text-xs font-mono">
                <tbody id="investmentsListBody" class="divide-y divide-slate-800"></tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="lg:col-span-7 glass-card p-5 rounded-xl">
          <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <i class="fa-solid fa-chart-pie text-emerald-400"></i> Composición del Portafolio de Inversiones
          </h3>
          <div id="investmentsPieChart" class="w-full h-80"></div>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 5: SOLVENCIA Y RATIOS SSN -->
    <!-- ======================================================== -->
    <section id="tab-solvencia-ratios" class="hidden space-y-6">
      
      <!-- Solvency Cards for selected company -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold text-slate-400">COBERTURA COMPROMISOS TÉCNICOS</div>
          <div id="solvCoberturaVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div id="solvCoberturaStatus" class="text-[10px] font-semibold mt-1">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold text-slate-400">APALANCAMIENTO (PRIMAS/PN)</div>
          <div id="solvApalancamientoVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Exposición s/ Capital Propio</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
          <div class="text-[11px] font-semibold text-slate-400">PREMIOS A COBRAR / PRIMAS</div>
          <div id="solvCobranzaVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Índice de Cartera a Cobrar</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-purple-500">
          <div class="text-[11px] font-semibold text-slate-400">PATRIMONIO NETO TOTAL</div>
          <div id="solvPnVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Solvencia Patrimonial</div>
        </div>
      </div>

      <!-- Full Market Solvency Ranking -->
      <div class="glass-card p-5 rounded-xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-ranking-star text-amber-400"></i> Ranking General de Solvencia y Ratio Combinado
          </h3>
          <span class="text-xs text-slate-400">Ordenado por Cobertura Regulatoria</span>
        </div>
        <div class="overflow-x-auto max-h-[450px]">
          <table class="w-full text-left text-xs">
            <thead class="text-slate-400 bg-slate-900 sticky top-0 border-b border-slate-700">
              <tr>
                <th class="py-2.5 px-3">Aseguradora</th>
                <th class="py-2.5 px-3">Segmento</th>
                <th class="py-2.5 px-3 text-right">Cobertura (x)</th>
                <th class="py-2.5 px-3 text-right">Ratio Combinado</th>
                <th class="py-2.5 px-3 text-right">Apalancamiento</th>
                <th class="py-2.5 px-3 text-right">Patrimonio Neto</th>
                <th class="py-2.5 px-3 text-right">Activo Total</th>
              </tr>
            </thead>
            <tbody id="solvencyRankingTableBody" class="divide-y divide-slate-800 font-mono"></tbody>
          </table>
        </div>
      </div>

    </section>

  </main>

  <!-- FOOTER -->
  <footer class="bg-slate-950 border-t border-slate-800/80 py-4 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
      <div>
        <span>Desarrollado para el Análisis Integral del Mercado Asegurador</span> • Normativa SSN / RGAA
      </div>
      <div class="font-mono text-[11px] text-slate-400">
        SINENSUP Engine • Período 2026-2
      </div>
    </div>
  </footer>

  <!-- EMBEDDED DATASET FOR ZERO-CORS PORTABILITY -->
  <script>
    window.DATA_SINENSUP = {raw_json_str};
  </script>

  <!-- APPLICATION LOGIC -->
  <script>
    // State management
    let state = {{
      currentTab: 'vision-mercado',
      selectedSegment: 'Todos',
      selectedCompanyCode: '0002',
      ramosScope: 'cia'
    }};

    // Formatters
    function formatARS(val) {{
      if (val === undefined || val === null || isNaN(val)) return '$0';
      const absVal = Math.abs(val);
      if (absVal >= 1e12) {{
        return (val < 0 ? '-' : '') + '$' + (absVal / 1e12).toFixed(2) + ' B';
      }} else if (absVal >= 1e9) {{
        return (val < 0 ? '-' : '') + '$' + (absVal / 1e9).toFixed(2) + ' MM';
      }} else if (absVal >= 1e6) {{
        return (val < 0 ? '-' : '') + '$' + (absVal / 1e6).toFixed(2) + ' M';
      }} else {{
        return (val < 0 ? '-' : '') + '$' + absVal.toLocaleString('es-AR', {{ maximumFractionDigits: 0 }});
      }}
    }}

    function formatPercent(val) {{
      if (val === undefined || val === null || isNaN(val)) return '0.0%';
      return val.toFixed(1) + '%';
    }}

    // Initialization
    document.addEventListener('DOMContentLoaded', () => {{
      initDashboard();
      lucide.createIcons();
    }});

    function initDashboard() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      document.getElementById('headerPeriodo').innerText = data.periodo || '2026-2';
      document.getElementById('headerTotalCias').innerText = data.total_entidades || '185';

      // Pick high-profile default company (e.g. Federación Patronal 0726 or La Segunda 0317)
      if (data.companies_by_code['0726']) {{
        state.selectedCompanyCode = '0726';
      }} else if (data.companies.length > 0) {{
        state.selectedCompanyCode = data.companies[0].cod_cia;
      }}

      buildSegmentPills();
      buildCompanyDropdown();
      setupSearchAutocomplete();
      renderAll();
    }}

    function buildSegmentPills() {{
      const data = window.DATA_SINENSUP;
      const container = document.getElementById('segmentPillsContainer');
      container.innerHTML = '';

      const segments = ['Todos', ...data.segmentos];
      segments.forEach(seg => {{
        const btn = document.createElement('button');
        btn.className = `px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${{
          state.selectedSegment === seg ? 'bg-brand-red text-white shadow-md shadow-brand-red/30' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
        }}`;
        btn.innerText = seg;
        btn.onclick = () => {{
          state.selectedSegment = seg;
          buildSegmentPills();
          renderAll();
        }};
        container.appendChild(btn);
      }});
    }}

    function buildCompanyDropdown() {{
      const data = window.DATA_SINENSUP;
      const select = document.getElementById('companyDropdownSelect');
      select.innerHTML = '';

      const sorted = [...data.companies].sort((a, b) => a.razon_social.localeCompare(b.razon_social));
      sorted.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c.cod_cia;
        opt.innerText = `${{c.cod_cia}} - ${{c.razon_social}}`;
        if (c.cod_cia === state.selectedCompanyCode) opt.selected = true;
        select.appendChild(opt);
      }});
    }}

    function setupSearchAutocomplete() {{
      const input = document.getElementById('globalCompanySearch');
      const dropdown = document.getElementById('searchResultsDropdown');

      input.addEventListener('input', (e) => {{
        const q = e.target.value.toLowerCase().trim();
        if (q.length < 2) {{
          dropdown.classList.add('hidden');
          return;
        }}

        const data = window.DATA_SINENSUP;
        const matches = data.companies.filter(c => 
          c.razon_social.toLowerCase().includes(q) || c.cod_cia.includes(q)
        ).slice(0, 10);

        if (matches.length === 0) {{
          dropdown.innerHTML = '<div class="p-3 text-slate-400">No se encontraron resultados</div>';
        }} else {{
          dropdown.innerHTML = matches.map(c => `
            <div onclick="selectCompany('${{c.cod_cia}}')" class="p-2.5 hover:bg-slate-800 cursor-pointer flex justify-between items-center border-b border-slate-800/50">
              <span class="font-semibold text-white">${{c.razon_social}}</span>
              <span class="font-mono text-slate-400 text-[10px]">${{c.cod_cia}} • ${{c.tipo_entidad}}</span>
            </div>
          `).join('');
        }}
        dropdown.classList.remove('hidden');
      }});

      document.addEventListener('click', (e) => {{
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {{
          dropdown.classList.add('hidden');
        }}
      }});
    }}

    function selectCompany(code) {{
      state.selectedCompanyCode = code;
      document.getElementById('globalCompanySearch').value = '';
      document.getElementById('searchResultsDropdown').classList.add('hidden');
      document.getElementById('companyDropdownSelect').value = code;
      switchTab('ficha-compania');
    }}

    function onCompanyDropdownChange(code) {{
      state.selectedCompanyCode = code;
      renderCompanyDetails();
    }}

    function switchTab(tabId) {{
      state.currentTab = tabId;
      ['vision-mercado', 'ficha-compania', 'ramos-suscripcion', 'inversiones-finanzas', 'solvencia-ratios'].forEach(id => {{
        const el = document.getElementById(`tab-${{id}}`);
        const btn = document.getElementById(`tabBtn-${{id}}`);
        if (id === tabId) {{
          el.classList.remove('hidden');
          btn.className = 'tab-btn active px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all';
        }} else {{
          el.classList.add('hidden');
          btn.className = 'tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2';
        }}
      }});
      renderAll();
    }}

    function getFilteredCompanies() {{
      const data = window.DATA_SINENSUP;
      if (state.selectedSegment === 'Todos') return data.companies;
      return data.companies.filter(c => c.tipo_entidad === state.selectedSegment);
    }}

    function renderAll() {{
      renderMarketOverview();
      renderCompanyDetails();
      renderRamosTab();
      renderInvestmentsTab();
      renderSolvencyTab();
    }}

    // ----------------------------------------------------
    // TAB 1 RENDER
    // ----------------------------------------------------
    function renderMarketOverview() {{
      const list = getFilteredCompanies();
      document.getElementById('filteredCiasCount').innerText = list.length;

      let totPrimasDev = 0, totPrimasEmit = 0, totActivo = 0, totSiniestros = 0, totGastos = 0, totNeto = 0;
      list.forEach(c => {{
        totPrimasDev += c.primas_devengadas || 0;
        totPrimasEmit += c.primas_emitidas || 0;
        totActivo += c.activo || 0;
        totSiniestros += c.siniestros || 0;
        totGastos += (c.gtos_produccion || 0) + (c.gtos_explotacion || 0);
        totNeto += c.resultado_neto || 0;
      }});

      const lossRatio = totPrimasDev > 0 ? (totSiniestros / totPrimasDev * 100) : 0;
      const combinedRatio = totPrimasDev > 0 ? ((totSiniestros + totGastos) / totPrimasDev * 100) : 0;

      document.getElementById('kpiPrimasDev').innerText = formatARS(totPrimasDev);
      document.getElementById('kpiPrimasEmit').innerText = formatARS(totPrimasEmit);
      document.getElementById('kpiActivos').innerText = formatARS(totActivo);
      document.getElementById('kpiLossRatio').innerText = formatPercent(lossRatio);
      document.getElementById('kpiCombinedRatio').innerText = formatPercent(combinedRatio);
      document.getElementById('kpiResNeto').innerText = formatARS(totNeto);

      // Top 10 Ranking table
      const sortedByPrimas = [...list].sort((a, b) => b.primas_devengadas - a.primas_devengadas).slice(0, 10);
      const rankingBody = document.getElementById('topRankingTableBody');
      rankingBody.innerHTML = sortedByPrimas.map((c, i) => `
        <tr class="hover:bg-slate-800/60 cursor-pointer" onclick="selectCompany('${{c.cod_cia}}')">
          <td class="py-2 px-2 font-medium text-white flex items-center gap-1.5">
            <span class="text-slate-500 font-mono text-[10px] w-4">${{i+1}}.</span>
            <span class="truncate max-w-[170px]" title="${{c.razon_social}}">${{c.razon_social}}</span>
          </td>
          <td class="py-2 px-2 text-right font-mono text-slate-200">${{formatARS(c.primas_devengadas)}}</td>
          <td class="py-2 px-2 text-right font-mono ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
          <td class="py-2 px-2 text-right font-mono ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_neto)}}</td>
        </tr>
      `).join('');

      renderMarketScatterPlot(list);
      renderMarketTable();
    }}

    function renderMarketScatterPlot(list) {{
      const valid = list.filter(c => c.primas_devengadas > 0);
      
      const trace = {{
        x: valid.map(c => Math.max(-120, Math.min(150, c.margen_tecnico))),
        y: valid.map(c => Math.max(-40, Math.min(80, c.roi_inversiones))),
        text: valid.map(c => `<b>${{c.razon_social}}</b><br>Primas Dev: ${{formatARS(c.primas_devengadas)}}<br>M. Técnico: ${{c.margen_tecnico.toFixed(1)}}%<br>ROI Inv: ${{c.roi_inversiones.toFixed(1)}}%<br>Ratio Comb: ${{c.combined_ratio.toFixed(1)}}%`),
        mode: 'markers',
        marker: {{
          size: valid.map(c => Math.max(8, Math.min(42, Math.sqrt(c.primas_devengadas / 1e8)))),
          color: valid.map(c => c.margen_tecnico >= 0 && c.roi_inversiones >= 0 ? '#10B981' : (c.margen_tecnico < 0 && c.roi_inversiones >= 0 ? '#F59E0B' : '#E20039')),
          opacity: 0.85,
          line: {{ color: '#FFFFFF', width: 1 }}
        }},
        type: 'scatter',
        hoverinfo: 'text'
      }};

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 45, r: 25, t: 20, b: 45 }},
        xaxis: {{
          title: 'Margen Técnico (%)',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          zerolinecolor: '#475569',
          zerolinewidth: 1.5
        }},
        yaxis: {{
          title: 'Rendimiento Inversiones (%)',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          zerolinecolor: '#475569',
          zerolinewidth: 1.5
        }},
        annotations: [
          {{ x: 70, y: 55, text: '<b>Ganadoras Integrales</b>', showarrow: false, font: {{ color: '#10B981', size: 10 }} }},
          {{ x: -60, y: 55, text: '<b>Dependencia Financiera</b>', showarrow: false, font: {{ color: '#F59E0B', size: 10 }} }},
          {{ x: -60, y: -25, text: '<b>En Riesgo</b>', showarrow: false, font: {{ color: '#E20039', size: 10 }} }}
        ]
      }};

      Plotly.newPlot('marketScatterPlot', [trace], layout, {{ responsive: true, displayModeBar: false }});
    }}

    function renderMarketTable() {{
      const list = getFilteredCompanies();
      const q = (document.getElementById('marketTableFilter')?.value || '').toLowerCase().trim();
      const filtered = q ? list.filter(c => c.razon_social.toLowerCase().includes(q) || c.cod_cia.includes(q)) : list;
      
      const sorted = [...filtered].sort((a, b) => b.primas_devengadas - a.primas_devengadas);
      const tbody = document.getElementById('marketFullTableBody');
      tbody.innerHTML = sorted.map(c => `
        <tr class="hover:bg-slate-800/60">
          <td class="py-2 px-3 text-slate-400">${{c.cod_cia}}</td>
          <td class="py-2 px-3 font-medium text-white truncate max-w-[200px]" title="${{c.razon_social}}">${{c.razon_social}}</td>
          <td class="py-2 px-3 text-slate-400 text-[11px]">${{c.tipo_entidad}}</td>
          <td class="py-2 px-3 text-right text-slate-200">${{formatARS(c.primas_devengadas)}}</td>
          <td class="py-2 px-3 text-right text-slate-300">${{formatARS(c.siniestros)}}</td>
          <td class="py-2 px-3 text-right">${{formatPercent(c.loss_ratio)}}</td>
          <td class="py-2 px-3 text-right ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
          <td class="py-2 px-3 text-right ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_tecnico)}}</td>
          <td class="py-2 px-3 text-right ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
          <td class="py-2 px-3 text-right font-bold ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_neto)}}</td>
          <td class="py-2 px-3 text-right text-slate-300">${{formatARS(c.activo)}}</td>
          <td class="py-2 px-3 text-center">
            <button onclick="selectCompany('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-[10px] font-semibold">Ver</button>
          </td>
        </tr>
      `).join('');
    }}

    // ----------------------------------------------------
    // TAB 2 RENDER: COMPANY DEEP DIVE
    // ----------------------------------------------------
    function renderCompanyDetails() {{
      const data = window.DATA_SINENSUP;
      const c = data.companies_by_code[state.selectedCompanyCode];
      if (!c) return;

      document.getElementById('selectedCiaTitle').innerText = c.razon_social;
      document.getElementById('selectedCiaBadge').innerText = c.tipo_entidad;
      document.getElementById('selectedCiaCode').innerText = c.cod_cia;

      document.getElementById('ciaKpiPrimasDev').innerText = formatARS(c.primas_devengadas);
      document.getElementById('ciaKpiCombined').innerText = formatPercent(c.combined_ratio);
      document.getElementById('ciaKpiCombined').className = `text-base font-bold font-mono mt-1 ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}`;
      
      document.getElementById('ciaKpiResTec').innerText = formatARS(c.resultado_tecnico);
      document.getElementById('ciaKpiResTec').className = `text-base font-bold font-mono mt-1 ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;

      document.getElementById('ciaKpiResFin').innerText = formatARS(c.resultado_financiero);
      document.getElementById('ciaKpiResFin').className = `text-base font-bold font-mono mt-1 ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;

      document.getElementById('ciaKpiResNeto').innerText = formatARS(c.resultado_neto);
      document.getElementById('ciaKpiResNeto').className = `text-base font-bold font-mono mt-1 ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;

      renderCompanyWaterfall(c);
      renderCompanyDonuts(c);
    }}

    function renderCompanyWaterfall(c) {{
      const wf = c.waterfall || [];
      if (wf.length === 0) return;

      const trace = {{
        type: 'waterfall',
        orientation: 'v',
        measure: wf.map(s => s.type === 'total' ? 'total' : 'relative'),
        x: wf.map(s => s.name),
        y: wf.map(s => s.amount),
        text: wf.map(s => formatARS(s.amount)),
        textposition: 'outside',
        connector: {{ line: {{ color: '#475569' }} }},
        decreasing: {{ marker: {{ color: '#E20039' }} }},
        increasing: {{ marker: {{ color: '#10B981' }} }},
        totals: {{ marker: {{ color: '#38BDF8' }} }}
      }};

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 50, r: 30, t: 30, b: 60 }},
        xaxis: {{ color: '#94A3B8', tickangle: -20 }},
        yaxis: {{ title: 'Importe (ARS)', color: '#94A3B8', gridcolor: '#1E293B' }}
      }};

      Plotly.newPlot('ciaWaterfallPlot', [trace], layout, {{ responsive: true, displayModeBar: false }});
    }}

    function renderCompanyDonuts(c) {{
      // Assets Donut
      const assetLabels = ['Disponibilidades', 'Inversiones', 'Créditos', 'Inmuebles', 'Otros Activos'];
      const assetVals = [c.disponibilidades, c.inversiones, c.creditos, c.inmuebles, (c.otros_activos || 0) + (c.bienes_uso || 0)];

      Plotly.newPlot('ciaAssetDonut', [{{
        labels: assetLabels,
        values: assetVals,
        hole: 0.45,
        type: 'pie',
        textinfo: 'label+percent',
        marker: {{ colors: ['#38BDF8', '#10B981', '#F59E0B', '#E20039', '#64748B'] }}
      }}], {{
        paper_bgcolor: 'transparent',
        margin: {{ l: 20, r: 20, t: 20, b: 20 }},
        showlegend: false,
        font: {{ color: '#E2E8F0', size: 11 }}
      }}, {{ responsive: true, displayModeBar: false }});

      // Liabilities Donut
      const liabLabels = ['Deudas', 'Compromisos Técnicos', 'Previsiones', 'Patrimonio Neto'];
      const liabVals = [c.deudas, c.compromisos_tecnicos, c.previsiones, Math.max(0, c.patrimonio_neto)];

      Plotly.newPlot('ciaLiabDonut', [{{
        labels: liabLabels,
        values: liabVals,
        hole: 0.45,
        type: 'pie',
        textinfo: 'label+percent',
        marker: {{ colors: ['#F87171', '#C084FC', '#FB923C', '#2DD4BF'] }}
      }}], {{
        paper_bgcolor: 'transparent',
        margin: {{ l: 20, r: 20, t: 20, b: 20 }},
        showlegend: false,
        font: {{ color: '#E2E8F0', size: 11 }}
      }}, {{ responsive: true, displayModeBar: false }});
    }}

    // ----------------------------------------------------
    // TAB 3 RENDER: RAMOS
    // ----------------------------------------------------
    function setRamosScope(scope) {{
      state.ramosScope = scope;
      document.getElementById('ramosScopeCiaBtn').className = `px-3 py-1 rounded ${{scope === 'cia' ? 'bg-brand-red text-white font-semibold' : 'text-slate-400 hover:text-white font-semibold'}}`;
      document.getElementById('ramosScopeMarketBtn').className = `px-3 py-1 rounded ${{scope === 'market' ? 'bg-brand-red text-white font-semibold' : 'text-slate-400 hover:text-white font-semibold'}}`;
      renderRamosTab();
    }}

    function renderRamosTab() {{
      const data = window.DATA_SINENSUP;
      let subList = [];

      if (state.ramosScope === 'cia') {{
        const c = data.companies_by_code[state.selectedCompanyCode];
        subList = (c && c.subramos) ? c.subramos : [];
      }} else {{
        subList = data.market_subramos || [];
      }}

      const topSub = subList.slice(0, 15);
      
      const tracePrimas = {{
        x: topSub.map(s => s.desc_subramo),
        y: topSub.map(s => s.primas),
        name: 'Primas Emitidas (ARS)',
        type: 'bar',
        marker: {{ color: '#38BDF8' }}
      }};

      const traceLoss = {{
        x: topSub.map(s => s.desc_subramo),
        y: topSub.map(s => s['siniestralidad_%'] || 0),
        name: 'Siniestralidad (%)',
        type: 'scatter',
        mode: 'lines+markers',
        yaxis: 'y2',
        marker: {{ color: '#E20039', size: 8 }},
        line: {{ color: '#E20039', width: 2 }}
      }};

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 50, r: 50, t: 20, b: 110 }},
        xaxis: {{ tickangle: -35, color: '#94A3B8' }},
        yaxis: {{ title: 'Primas (ARS)', color: '#94A3B8', gridcolor: '#1E293B' }},
        yaxis2: {{
          title: 'Siniestralidad (%)',
          overlaying: 'y',
          side: 'right',
          color: '#E20039',
          showgrid: false
        }},
        legend: {{ orientation: 'h', y: 1.15, x: 0.5, xanchor: 'center', font: {{ color: '#E2E8F0' }} }}
      }};

      Plotly.newPlot('subramosBarChart', [tracePrimas, traceLoss], layout, {{ responsive: true, displayModeBar: false }});

      // Subramos table
      const tbody = document.getElementById('subramosTableBody');
      tbody.innerHTML = topSub.map(s => `
        <tr class="hover:bg-slate-800/60">
          <td class="py-2 px-3 text-slate-400">${{s.cod_subramo || '-'}}</td>
          <td class="py-2 px-3 text-white font-medium">${{s.desc_subramo}}</td>
          <td class="py-2 px-3 text-right text-slate-200">${{formatARS(s.primas)}}</td>
          <td class="py-2 px-3 text-right text-slate-300">${{formatARS(s.siniestros)}}</td>
          <td class="py-2 px-3 text-right font-bold ${{s['siniestralidad_%'] > 60 ? 'text-rose-400' : 'text-emerald-400'}}">${{formatPercent(s['siniestralidad_%'])}}</td>
        </tr>
      `).join('');
    }}

    // ----------------------------------------------------
    // TAB 4 RENDER: INVERSIONES
    // ----------------------------------------------------
    function renderInvestmentsTab() {{
      const data = window.DATA_SINENSUP;
      const c = data.companies_by_code[state.selectedCompanyCode];
      if (!c) return;

      document.getElementById('invCiaName').innerText = c.razon_social;
      document.getElementById('invTotalVal').innerText = formatARS(c.inversiones);
      document.getElementById('invResFinVal').innerText = formatARS(c.resultado_financiero);
      document.getElementById('invRoiVal').innerText = formatPercent(c.roi_inversiones);

      const invs = c.investments || [];
      const listBody = document.getElementById('investmentsListBody');
      if (invs.length === 0) {{
        listBody.innerHTML = '<tr><td class="p-3 text-slate-400">Sin desglose nivel 3</td></tr>';
      }} else {{
        listBody.innerHTML = invs.map(item => `
          <tr class="hover:bg-slate-800/40">
            <td class="py-2 px-2 text-slate-300">${{item.desc_cuenta}}</td>
            <td class="py-2 px-2 text-right text-white font-bold">${{formatARS(item.importe)}}</td>
            <td class="py-2 px-2 text-right text-brand-blue">${{item.porcentaje}}%</td>
          </tr>
        `).join('');
      }}

      Plotly.newPlot('investmentsPieChart', [{{
        labels: invs.map(i => i.desc_cuenta),
        values: invs.map(i => i.importe),
        hole: 0.4,
        type: 'pie',
        textinfo: 'label+percent',
        marker: {{ colors: ['#38BDF8', '#10B981', '#F59E0B', '#C084FC', '#FB923C', '#94A3B8'] }}
      }}], {{
        paper_bgcolor: 'transparent',
        margin: {{ l: 20, r: 20, t: 20, b: 20 }},
        showlegend: false,
        font: {{ color: '#E2E8F0', size: 11 }}
      }}, {{ responsive: true, displayModeBar: false }});
    }}

    // ----------------------------------------------------
    // TAB 5 RENDER: SOLVENCIA
    // ----------------------------------------------------
    function renderSolvencyTab() {{
      const data = window.DATA_SINENSUP;
      const c = data.companies_by_code[state.selectedCompanyCode];
      if (!c) return;

      const cob = c.cobertura_reservas || 0;
      document.getElementById('solvCoberturaVal').innerText = cob.toFixed(2) + 'x';
      document.getElementById('solvCoberturaStatus').innerText = cob >= 1.0 ? '● Superávit Regulatorio' : '● Déficit de Cobertura';
      document.getElementById('solvCoberturaStatus').className = `text-[10px] font-semibold mt-1 ${{cob >= 1.0 ? 'text-emerald-400' : 'text-rose-400'}}`;

      document.getElementById('solvApalancamientoVal').innerText = (c.apalancamiento || 0).toFixed(2) + 'x';
      document.getElementById('solvCobranzaVal').innerText = formatPercent(c.calidad_cartera);
      document.getElementById('solvPnVal').innerText = formatARS(c.patrimonio_neto);

      const list = getFilteredCompanies();
      const sortedSolv = [...list].sort((a, b) => b.cobertura_reservas - a.cobertura_reservas);
      const tbody = document.getElementById('solvencyRankingTableBody');
      tbody.innerHTML = sortedSolv.map(item => `
        <tr class="hover:bg-slate-800/60 cursor-pointer" onclick="selectCompany('${{item.cod_cia}}')">
          <td class="py-2 px-3 font-medium text-white">${{item.razon_social}}</td>
          <td class="py-2 px-3 text-slate-400">${{item.tipo_entidad}}</td>
          <td class="py-2 px-3 text-right font-bold ${{item.cobertura_reservas >= 1.0 ? 'text-emerald-400' : 'text-rose-400'}}">${{item.cobertura_reservas.toFixed(2)}}x</td>
          <td class="py-2 px-3 text-right ${{item.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(item.combined_ratio)}}</td>
          <td class="py-2 px-3 text-right text-slate-300">${{item.apalancamiento.toFixed(2)}}x</td>
          <td class="py-2 px-3 text-right text-slate-200">${{formatARS(item.patrimonio_neto)}}</td>
          <td class="py-2 px-3 text-right text-slate-200">${{formatARS(item.activo)}}</td>
        </tr>
      `).join('');
    }}

    // Export to CSV
    function exportToCSV() {{
      const list = getFilteredCompanies();
      const headers = ['cod_cia', 'razon_social', 'tipo_entidad', 'primas_devengadas', 'primas_emitidas', 'siniestros', 'resultado_tecnico', 'resultado_financiero', 'resultado_neto', 'activo', 'inversiones', 'patrimonio_neto', 'loss_ratio', 'combined_ratio', 'cobertura_reservas'];
      
      let csv = headers.join(',') + '\\n';
      list.forEach(c => {{
        const row = [
          `"${{c.cod_cia}}"`,
          `"${{c.razon_social.replace(/"/g, '""')}}"`,
          `"${{c.tipo_entidad}}"`,
          c.primas_devengadas || 0,
          c.primas_emitidas || 0,
          c.siniestros || 0,
          c.resultado_tecnico || 0,
          c.resultado_financiero || 0,
          c.resultado_neto || 0,
          c.activo || 0,
          c.inversiones || 0,
          c.patrimonio_neto || 0,
          c.loss_ratio || 0,
          c.combined_ratio || 0,
          c.cobertura_reservas || 0
        ];
        csv += row.join(',') + '\\n';
      }});

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sinensup_mercado_asegurador_${{state.selectedSegment.toLowerCase().replace(/ /g, '_')}}.csv`;
      a.click();
    }}
  </script>
</body>
</html>
"""

    out_file = r"g:\Mi unidad\IA\Sinensup\index.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"index.html generated successfully ({os.path.getsize(out_file):,} bytes)")

if __name__ == '__main__':
    generate_html()
