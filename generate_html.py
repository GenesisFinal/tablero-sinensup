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
    .combobox-dropdown-menu {{
      z-index: 99999 !important;
      position: absolute !important;
      box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.95), 0 0 20px rgba(0, 0, 0, 0.7) !important;
    }}
    .header-card-sticky {{
      position: relative !important;
      z-index: 50 !important;
    }}
    .content-card-lower {{
      position: relative !important;
      z-index: 1 !important;
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
      <button onclick="switchTab('rankings-ramos')" id="tabBtn-rankings-ramos" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-ranking-star text-amber-400"></i> 4. Rankings por Rama
      </button>
      <button onclick="switchTab('inversiones-finanzas')" id="tabBtn-inversiones-finanzas" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-chart-line"></i> 5. Inversiones y Finanzas
      </button>
      <button onclick="switchTab('solvencia-ratios')" id="tabBtn-solvencia-ratios" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-scale-balanced"></i> 6. Solvencia y Ratios SSN
      </button>
      <button onclick="switchTab('ratios-gestion')" id="tabBtn-ratios-gestion" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-gauge-high"></i> 7. Ratios de Gestión
      </button>
      <button onclick="switchTab('balances')" id="tabBtn-balances" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all flex items-center gap-2">
        <i class="fa-solid fa-file-invoice-dollar text-emerald-400"></i> 8. Balances Contables
      </button>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">

    <!-- ======================================================== -->
    <!-- TAB 1: VISIÓN MERCADO -->
    <!-- ======================================================== -->
    <section id="tab-vision-mercado" class="space-y-6">
      
      <!-- 1. BANNER: DISTRIBUCIÓN POR TIPO DE ASEGURADORA (185 ENTIDADES) -->
      <div class="glass-card p-4 rounded-xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
          <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-building-columns text-brand-blue"></i> 1. Clasificación Institucional por Tipo de Aseguradora
          </span>
          <span class="text-[11px] font-mono text-slate-300">Total Producción Empresas: <b id="macroTotalVal" class="text-amber-400 font-bold">...</b></span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <!-- Patrimoniales y Mixtas -->
          <div onclick="setSegmentFilter('Patrimoniales y Mixtas')" 
               class="p-2.5 bg-slate-950/80 hover:bg-slate-800/80 cursor-pointer rounded-lg border border-slate-800 hover:border-sky-500/50 transition-all group">
            <div class="text-[10px] text-slate-400 group-hover:text-sky-300 uppercase font-sans font-semibold flex items-center justify-between">
              <span>Patrimoniales y Mixtas</span>
              <i class="fa-solid fa-arrow-right text-[9px] opacity-0 group-hover:opacity-100 transition-opacity text-sky-400"></i>
            </div>
            <div id="macroPatrimVal" class="text-sm font-bold text-sky-400 mt-0.5">...</div>
            <div id="macroPatrimSub" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>

          <!-- ART -->
          <div onclick="setSegmentFilter('Riesgos del Trabajo (ART)')" 
               class="p-2.5 bg-slate-950/80 hover:bg-slate-800/80 cursor-pointer rounded-lg border border-slate-800 hover:border-amber-500/50 transition-all group">
            <div class="text-[10px] text-slate-400 group-hover:text-amber-300 uppercase font-sans font-semibold flex items-center justify-between">
              <span>Riesgos del Trabajo (ART)</span>
              <i class="fa-solid fa-arrow-right text-[9px] opacity-0 group-hover:opacity-100 transition-opacity text-amber-400"></i>
            </div>
            <div id="macroArtVal" class="text-sm font-bold text-amber-400 mt-0.5">...</div>
            <div id="macroArtSub" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>

          <!-- Seguros de Personas -->
          <div onclick="setSegmentFilter('Seguros de Personas')" 
               class="p-2.5 bg-slate-950/80 hover:bg-slate-800/80 cursor-pointer rounded-lg border border-slate-800 hover:border-rose-500/50 transition-all group">
            <div class="text-[10px] text-slate-400 group-hover:text-rose-300 uppercase font-sans font-semibold flex items-center justify-between">
              <span>Seguros de Personas (Monorramo)</span>
              <i class="fa-solid fa-arrow-right text-[9px] opacity-0 group-hover:opacity-100 transition-opacity text-rose-400"></i>
            </div>
            <div id="macroPersonasVal" class="text-sm font-bold text-rose-400 mt-0.5">...</div>
            <div id="macroPersonasSub" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>

          <!-- Seguros de Retiro -->
          <div onclick="setSegmentFilter('Seguros de Retiro')" 
               class="p-2.5 bg-slate-950/80 hover:bg-slate-800/80 cursor-pointer rounded-lg border border-slate-800 hover:border-purple-500/50 transition-all group">
            <div class="text-[10px] text-slate-400 group-hover:text-purple-300 uppercase font-sans font-semibold flex items-center justify-between">
              <span>Seguros de Retiro</span>
              <i class="fa-solid fa-arrow-right text-[9px] opacity-0 group-hover:opacity-100 transition-opacity text-purple-400"></i>
            </div>
            <div id="macroRetiroVal" class="text-sm font-bold text-purple-400 mt-0.5">...</div>
            <div id="macroRetiroSub" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>
        </div>
      </div>

      <!-- 2. BANNER: DISTRIBUCIÓN POR CONJUNTO DE PRODUCTOS (SUBRAMOS REALES) -->
      <div class="glass-card p-4 rounded-xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
          <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-boxes-stacked text-amber-400"></i> 2. Clasificación Técnica por Línea Real de Producto (Subramos)
          </span>
          <span class="text-[11px] font-mono text-slate-400">Base Técnica: <b>Total Primas y Recargos Unificados ($29.91 B)</b></span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <!-- Productos Patrimoniales -->
          <div class="p-2.5 bg-slate-900/90 rounded-lg border border-sky-500/30">
            <div class="text-[10px] text-sky-300 uppercase font-sans font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-car"></i> Productos Patrimoniales
            </div>
            <div id="prodPatrimPrimas" class="text-sm font-bold text-sky-400 mt-1">...</div>
            <div id="prodPatrimDetails" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>

          <!-- Productos ART -->
          <div class="p-2.5 bg-slate-900/90 rounded-lg border border-amber-500/30">
            <div class="text-[10px] text-amber-300 uppercase font-sans font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-helmet-safety"></i> Productos Riesgos Trabajo
            </div>
            <div id="prodArtPrimas" class="text-sm font-bold text-amber-400 mt-1">...</div>
            <div id="prodArtDetails" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>

          <!-- Productos Personas y Vida -->
          <div class="p-2.5 bg-slate-900/90 rounded-lg border border-rose-500/40 bg-rose-500/5">
            <div class="text-[10px] text-rose-300 uppercase font-sans font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-heart-pulse"></i> Productos Personas y Vida
            </div>
            <div id="prodPersonasPrimas" class="text-sm font-bold text-rose-400 mt-1">...</div>
            <div id="prodPersonasDetails" class="text-[10px] text-rose-200 mt-0.5">...</div>
          </div>

          <!-- Productos Retiro y Rentas -->
          <div class="p-2.5 bg-slate-900/90 rounded-lg border border-purple-500/30">
            <div class="text-[10px] text-purple-300 uppercase font-sans font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-piggy-bank"></i> Productos Retiro y Rentas
            </div>
            <div id="prodRetiroPrimas" class="text-sm font-bold text-purple-400 mt-1">...</div>
            <div id="prodRetiroDetails" class="text-[10px] text-slate-400 mt-0.5">...</div>
          </div>
        </div>

        <!-- Personas Cross-Selling Insight Box -->
        <div id="personasInsightBox" class="mt-2.5 p-2 bg-slate-900/80 rounded-lg border border-slate-800 text-[11px] text-slate-300 flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <i class="fa-solid fa-circle-info text-rose-400"></i>
            <span><b>Efecto Multirramo en Personas:</b> El <b>48.2% ($1.80 B)</b> de los productos de Personas y Vida es emitido por Aseguradoras Mixtas, y el <b>50.0% ($1.87 B)</b> por Aseguradoras exclusivas de Personas.</span>
          </div>
          <span class="font-mono text-rose-300 font-bold">Total Ramo Personas: $3.74 B (12.5% del mercado)</span>
        </div>
      </div>

      <!-- Segment Filter Pills -->
      <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-filter text-brand-red"></i> Filtrar Aseguradoras por Tipo:</span>
          <div id="segmentPillsContainer" class="flex flex-wrap gap-1.5"></div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades en el segmento: <span id="filteredCiasCount" class="font-mono font-bold text-white">185</span>
        </div>
      </div>

      <!-- Macro KPI Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Primas Devengadas</div>
          <div id="kpiPrimasDev" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Base Técnica 100%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-slate-400">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Primas Emitidas</div>
          <div id="kpiPrimasEmit" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Emisión Bruta</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Activo Administrado</div>
          <div id="kpiActivos" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Total Activo</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Siniestralidad Dev.</div>
          <div id="kpiLossRatio" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Loss Ratio Medio</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Ratio Combinado</div>
          <div id="kpiCombinedRatio" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Técnico + Gastos</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-indigo-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">Resultado Neto</div>
          <div id="kpiResNeto" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Consolidado Final</div>
        </div>
      </div>

      <!-- 1. FULL WIDTH: Interactive Strategic Scatter Plot Matrix with Company Highlighter -->
      <div class="glass-card header-card-sticky p-5 rounded-xl w-full relative z-30 overflow-visible">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-crosshairs text-brand-red"></i> Matriz Estratégica: Margen Técnico vs. Rendimiento Financiero
            </h3>
            <p class="text-xs text-slate-400">Selecciona o haz clic en cualquier burbuja para resaltarla con su ficha y métricas</p>
          </div>

            <!-- Searchable Highlight Combobox -->
            <div class="relative w-56 sm:w-64" id="scatterComboboxContainer">
              <button type="button" onclick="toggleCombobox('scatterCombobox')" id="scatterComboboxBtn" class="w-full flex items-center justify-between px-2.5 py-1 bg-slate-900 border border-slate-700 rounded-lg text-xs text-amber-300 font-semibold focus:outline-none hover:border-amber-400 transition-all">
                <span id="scatterComboboxLabel" class="truncate">🔍 Resaltar aseguradora...</span>
                <i class="fa-solid fa-chevron-down text-slate-400 text-[9px] ml-1.5 flex-shrink-0"></i>
              </button>
              <div id="scatterComboboxDropdown" class="hidden absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-[100] p-2 text-xs backdrop-blur-md max-h-72 flex flex-col">
                <div class="relative mb-2">
                  <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                  <input type="text" id="scatterComboboxInput" oninput="filterCombobox('scatterCombobox', this.value)" placeholder="Tipea nombre o código..." class="w-full pl-7 pr-2 py-1 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400 font-normal">
                </div>
                <div id="scatterComboboxList" class="overflow-y-auto max-h-56 divide-y divide-slate-800/40"></div>
              </div>
            </div>
            <button id="clearHighlightBtn" onclick="highlightScatterCompany('')" class="hidden px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors" title="Quitar resaltado">
              <i class="fa-solid fa-xmark text-rose-400"></i>
            </button>

            <!-- Quick La Segunda Pills -->
            <div class="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/30">
              <span class="text-[10px] font-bold text-amber-300 mr-1"><i class="fa-solid fa-star"></i> La Segunda:</span>
              <button onclick="highlightScatterCompany('0317')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Seguros Generales">0317</button>
              <button onclick="highlightScatterCompany('0618')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda ART">0618</button>
              <button onclick="highlightScatterCompany('0117')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Personas">0117</button>
              <button onclick="highlightScatterCompany('0436')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Retiro">0436</button>
            </div>

            <!-- Zoom, Pan, Reset & Download PNG -->
            <div class="flex items-center gap-1">
              <button onclick="zoomScatterPlot(0.7)" title="Acercar Zoom (+)" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors">
                <i class="fa-solid fa-magnifying-glass-plus text-brand-blue"></i>
              </button>
              <button onclick="zoomScatterPlot(1.4)" title="Alejar Zoom (-)" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors">
                <i class="fa-solid fa-magnifying-glass-minus text-brand-blue"></i>
              </button>
              <button id="panToggleBtn" onclick="toggleScatterPan()" title="Desplazar / Pan (arrastrar el gráfico)" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors">
                <i class="fa-solid fa-up-down-left-right text-amber-400"></i>
              </button>
              <button onclick="resetScatterPlotZoom()" title="Restablecer vista / Reset Axes" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1.5">
                <i class="fa-solid fa-arrows-rotate text-emerald-400"></i> Centrar
              </button>
              <button onclick="downloadScatterPlotPNG()" title="Descargar imagen PNG" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1.5">
                <i class="fa-solid fa-camera text-sky-400"></i> PNG
              </button>
            </div>
          </div>
        </div>

        <!-- 4 Quadrants Legend Bar -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-[11px] font-semibold bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
          <div class="flex items-center gap-1.5 text-emerald-400"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> <b>Q1: Ganadoras Integrales</b> (Téc + / Fin +)</div>
          <div class="flex items-center gap-1.5 text-amber-400"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> <b>Q2: Dependencia Financiera</b> (Téc - / Fin +)</div>
          <div class="flex items-center gap-1.5 text-sky-400"><span class="w-2.5 h-2.5 rounded-full bg-sky-500"></span> <b>Q3: Técnicas Puras</b> (Téc + / Fin -)</div>
          <div class="flex items-center gap-1.5 text-rose-400"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> <b>Q4: En Riesgo Operativo</b> (Téc - / Fin -)</div>
        </div>

        <div id="marketScatterPlot" class="w-full h-[520px]"></div>
      </div>

      <!-- 2. FULL WIDTH: Top Aseguradoras Ranking Table -->
      <!-- 2. FULL WIDTH: Top Aseguradoras y Grupos Económicos Ranking -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-trophy text-amber-400"></i> Ranking de Producción y Concentración del Mercado
            </h3>
            <p class="text-xs text-slate-400">Compara el liderazgo de mercado por Grupos Económicos Consolidados o por Aseguradoras Individuales</p>
          </div>
          
          <!-- Mode Switch: Grupos vs Aseguradoras -->
          <div class="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-700">
            <button type="button" onclick="setRankingMode('groups')" id="rankingModeBtn-groups" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5">
              <i class="fa-solid fa-building-columns"></i> 🏛️ Grupos Aseguradores (Top 17)
            </button>
            <button type="button" onclick="setRankingMode('companies')" id="rankingModeBtn-companies" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5">
              <i class="fa-solid fa-building"></i> 🏢 Aseguradoras Individuales
            </button>
          </div>
        </div>

        <!-- Groups Ranking Table View -->
        <div id="groupsRankingContainer" class="w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/90 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2.5 px-2 text-center w-8">#</th>
                <th class="py-2.5 px-2 text-left w-56">Grupo Asegurador</th>
                <th class="py-2.5 px-2 text-center w-16">Cías</th>
                <th class="py-2.5 px-2 text-right">Primas Emitidas</th>
                <th class="py-2.5 px-2 text-right w-24">Market Share</th>
                <th class="py-2.5 px-2 text-right">Primas Dev.</th>
                <th class="py-2.5 px-2 text-right">Loss Ratio</th>
                <th class="py-2.5 px-2 text-right">Comb. Ratio</th>
                <th class="py-2.5 px-2 text-right">Res. Técnico</th>
                <th class="py-2.5 px-2 text-right">Res. Financiero</th>
                <th class="py-2.5 px-2 text-right">Res. Neto</th>
                <th class="py-2.5 px-2 text-right">Activo</th>
                <th class="py-2.5 px-2 text-right">Patrimonio Neto</th>
                <th class="py-2.5 px-2 text-center w-24">Desglose</th>
              </tr>
            </thead>
            <tbody id="groupsRankingTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>

        <!-- Individual Companies Table View -->
        <div id="companiesRankingContainer" class="hidden w-full overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/90 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2 px-2 text-center w-8">#</th>
                <th class="py-2 px-2 whitespace-nowrap text-left w-48 max-w-[200px]">Razón Social</th>
                <th class="py-2 px-2 text-center w-12">Tipo</th>
                <th class="py-2.5 px-2 text-right">Primas Emitidas</th>
                <th class="py-2.5 px-2 text-right">Primas Dev.</th>
                <th class="py-2.5 px-2 text-right">Siniestros</th>
                <th class="py-2.5 px-2 text-right">Loss Ratio</th>
                <th class="py-2.5 px-2 text-right">Comb. Ratio</th>
                <th class="py-2.5 px-2 text-right">Res. Técnico</th>
                <th class="py-2.5 px-2 text-right">Res. Financiero</th>
                <th class="py-2.5 px-2 text-right">Res. Neto</th>
                <th class="py-2.5 px-2 text-right">Activo</th>
                <th class="py-2.5 px-2 text-center w-14">Acción</th>
              </tr>
            </thead>
            <tbody id="topRankingTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

      <!-- Modal / Drawer: Detalle Societario del Grupo Asegurador -->
      <div id="groupDetailModal" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="glass-card bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
          <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
            <div>
              <div class="flex items-center gap-3">
                <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">🏛️ GRUPO ECONÓMICO</span>
                <h3 id="groupModalTitle" class="text-base font-bold text-white">...</h3>
              </div>
              <p id="groupModalSubtitle" class="text-xs text-slate-400 mt-1">...</p>
            </div>
            <button onclick="closeGroupModal()" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold">
              ✕
            </button>
          </div>
          
          <!-- Group Summary KPIs -->
          <div id="groupModalKpis" class="p-4 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60 border-b border-slate-800"></div>

          <!-- Members List -->
          <div class="p-5 overflow-y-auto space-y-3 flex-1">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-layer-group text-emerald-400"></i> Composición Societaria y Aporte por Aseguradora:
            </h4>
            <div id="groupModalMembersList" class="divide-y divide-slate-800/80 rounded-xl border border-slate-800 bg-slate-950/40"></div>
          </div>

          <!-- Footer Actions -->
          <div class="p-4 border-t border-slate-800 bg-slate-950/50 flex flex-wrap items-center justify-between gap-3">
            <span class="text-[11px] text-slate-400">Fuente: Base Oficial SSN • Período 2026-2</span>
            <div class="flex items-center gap-2">
              <button id="groupModalBalanceBtn" class="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20">
                <i class="fa-solid fa-tree"></i> Ver Balance Consolidado (Tab 7)
              </button>
              <button onclick="closeGroupModal()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. FULL WIDTH: Base Consolidada del Mercado Asegurador (185 Entidades) -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-table-list text-brand-blue"></i> Base Consolidada del Mercado Asegurador (185 Entidades)
            </h3>
            <p class="text-xs text-slate-400">Explora, filtra y compara todas las compañías registradas</p>
          </div>
          <input type="text" id="marketTableFilter" oninput="renderMarketTable()" placeholder="Filtrar por nombre..." 
                 class="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-brand-blue w-64">
        </div>
        <div class="w-full overflow-x-auto max-h-[480px]">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/90 sticky top-0 z-10 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2 px-2 whitespace-nowrap text-left w-48 max-w-[200px]">Razón Social</th>
                <th class="py-2 px-2 text-center w-12">Tipo</th>
                <th class="py-2.5 px-2 text-right">Primas Emitidas</th>
                <th class="py-2.5 px-2 text-right">Primas Dev.</th>
                <th class="py-2.5 px-2 text-right">Siniestros</th>
                <th class="py-2.5 px-2 text-right">Loss Ratio</th>
                <th class="py-2.5 px-2 text-right">Comb. Ratio</th>
                <th class="py-2.5 px-2 text-right">Res. Técnico</th>
                <th class="py-2.5 px-2 text-right">Res. Financiero</th>
                <th class="py-2.5 px-2 text-right">Res. Neto</th>
                <th class="py-2.5 px-2 text-right">Activo</th>
                <th class="py-2.5 px-2 text-center w-14">Acción</th>
              </tr>
            </thead>
            <tbody id="marketFullTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 2: FICHA DE LA ASEGURADORA -->
    <!-- ======================================================== -->
    <section id="tab-ficha-compania" class="hidden space-y-6">
      
      <!-- Company Selector Header -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-brand-red flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="selectedCiaTitle" class="text-lg font-bold text-white">...</h2>
            <span id="selectedCiaBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-brand-red/20 text-brand-red border border-brand-red/30">...</span>
          </div>
          <p class="text-xs text-slate-400 mt-1">Código SSN: <span id="selectedCiaCode" class="font-mono text-white font-bold">...</span> | Período: <span class="font-mono text-slate-300">2026-2</span></p>
        </div>
        
        <div class="flex items-center gap-3">
          <div class="relative w-64 sm:w-80" id="ciaComboboxContainer">
            <button type="button" onclick="toggleCombobox('ciaCombobox')" id="ciaComboboxBtn" class="w-full flex items-center justify-between px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none hover:border-brand-red transition-all">
              <span id="ciaComboboxLabel" class="truncate">...</span>
              <i class="fa-solid fa-chevron-down text-slate-400 text-[10px] ml-2 flex-shrink-0"></i>
            </button>
            <div id="ciaComboboxDropdown" class="hidden combobox-dropdown-menu top-full right-0 w-full sm:w-96 mt-1 bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs max-h-80 flex flex-col">
              <div class="relative mb-2">
                <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                <input type="text" id="ciaComboboxInput" oninput="filterCombobox('ciaCombobox', this.value)" placeholder="Escribe para buscar aseguradora..." class="w-full pl-7 pr-2 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-red font-normal">
              </div>
              <div id="ciaComboboxList" class="overflow-y-auto max-h-64 divide-y divide-slate-800/40"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Company Mini KPI Cards (6 Cards with Primas Emitidas & Variación de Reservas) -->
      <div class="content-card-lower grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-slate-400">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">PRIMAS EMITIDAS</div>
          <div id="ciaKpiPrimasEmit" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Producción Bruta</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">VAR. RESERVAS / CT</div>
          <div id="ciaKpiVarReservas" class="text-base font-bold font-mono text-amber-300 mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Compromisos Técnicos</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">PRIMAS DEVENGADAS</div>
          <div id="ciaKpiPrimasDev" class="text-base font-bold font-mono text-brand-blue mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Base Devengada 100%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">RATIO COMBINADO</div>
          <div id="ciaKpiCombined" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Costo + Gastos</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO TÉCNICO</div>
          <div id="ciaKpiResTec" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Margen Suscripción</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-purple-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO NETO</div>
          <div id="ciaKpiResNeto" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Final del Período</div>
        </div>
      </div>

      <!-- Waterfall Chart -->
      <div class="glass-card p-5 rounded-xl">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-waterfall text-brand-blue"></i> Estado de Resultados: Cascada de Rentabilidad
            </h3>
            <p class="text-xs text-slate-400">Evolución contable desde Primas Emitidas y Variación de Reservas Matemáticas / Riesgos en Curso hasta Resultado Neto (SSN Moneda Homogénea)</p>
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
            <p class="text-xs text-slate-400">Barras = Primas Emitidas (ARS) | Línea y Etiquetas = Siniestralidad s/ Emisión (%)</p>
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
                <th class="py-2.5 px-3 text-right">Siniestralidad s/ Emisión (%)</th>
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
      
      <!-- Company Selector Header in Tab 4 -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-amber-500 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="invSelectedTitle" class="text-lg font-bold text-white">...</h2>
            <span id="invSelectedBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">...</span>
          </div>
          <p class="text-xs text-slate-400 mt-1">Análisis de Cartera de Inversiones (1.02) y Rendimiento Financiero SSN</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-semibold flex items-center gap-1">
              <i class="fa-solid fa-building text-amber-400"></i> Aseguradora:
            </span>
            <div class="relative w-64 sm:w-80" id="invComboboxContainer">
              <button type="button" onclick="toggleCombobox('invCombobox')" id="invComboboxBtn" class="w-full flex items-center justify-between px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none hover:border-amber-400 transition-all">
                <span id="invComboboxLabel" class="truncate">...</span>
                <i class="fa-solid fa-chevron-down text-slate-400 text-[10px] ml-2 flex-shrink-0"></i>
              </button>
              <div id="invComboboxDropdown" class="hidden combobox-dropdown-menu top-full right-0 w-full sm:w-96 mt-1 bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs max-h-80 flex flex-col">
                <div class="relative mb-2">
                  <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                  <input type="text" id="invComboboxInput" oninput="filterCombobox('invCombobox', this.value)" placeholder="Escribe para buscar aseguradora..." class="w-full pl-7 pr-2 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400 font-normal">
                </div>
                <div id="invComboboxList" class="overflow-y-auto max-h-64 divide-y divide-slate-800/40"></div>
              </div>
            </div>
          </div>

          <!-- Quick La Segunda Pills -->
          <div class="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/30">
            <span class="text-[10px] font-bold text-amber-300 mr-1">★ La Segunda:</span>
            <button onclick="onCompanyDropdownChange('0317')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Seguros Generales">0317</button>
            <button onclick="onCompanyDropdownChange('0618')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda ART">0618</button>
            <button onclick="onCompanyDropdownChange('0117')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Personas">0117</button>
            <button onclick="onCompanyDropdownChange('0436')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Retiro">0436</button>
          </div>
        </div>
      </div>

      <!-- Scope Selector Pills (Aseguradora vs Tipo de Empresa vs Mercado Total) -->
      <div class="content-card-lower flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-layer-group text-amber-400"></i> Alcance del Análisis:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setInvScope('cia')" id="invScopeBtn-cia" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 font-bold transition-all shadow-md shadow-amber-500/20">🏢 Aseguradora Seleccionada</button>
            <button onclick="setInvScope('market')" id="invScopeBtn-market" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🌐 Mercado Total (185 Cías)</button>
            <button onclick="setInvScope('Patrimoniales y Mixtas')" id="invScopeBtn-Patrimoniales y Mixtas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🚗 Patrimoniales y Mixtas</button>
            <button onclick="setInvScope('Riesgos del Trabajo (ART)')" id="invScopeBtn-Riesgos del Trabajo (ART)" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🦺 Riesgos del Trabajo (ART)</button>
            <button onclick="setInvScope('Seguros de Personas')" id="invScopeBtn-Seguros de Personas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">❤️ Seguros de Personas</button>
            <button onclick="setInvScope('Seguros de Retiro')" id="invScopeBtn-Seguros de Retiro" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏦 Seguros de Retiro</button>
          </div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades analizadas: <span id="invEntitiesCount" class="font-mono font-bold text-white">1</span>
        </div>
      </div>

      <!-- Financial KPI Cards (4 Cards) -->
      <div class="content-card-lower grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-400">
          <div class="text-[11px] font-semibold uppercase text-slate-400">TOTAL INVERSIONES (1.02)</div>
          <div id="invTotalVal" class="text-base font-bold font-mono text-amber-300 mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Cartera de Activos Financieros</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">RESULTADO FINANCIERO NETO</div>
          <div id="invResFinVal" class="text-base font-bold font-mono text-white mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Ganancias - Pérdidas Fin.</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold uppercase text-slate-400">RENDIMIENTO FINANCIERO (ROI)</div>
          <div id="invRoiVal" class="text-base font-bold font-mono text-brand-blue mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Res. Fin. / Inversiones</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-purple-500">
          <div class="text-[11px] font-semibold uppercase text-slate-400">INVERSIONES / ACTIVO TOTAL</div>
          <div id="invAssetShareVal" class="text-base font-bold font-mono text-purple-300 mt-1">...</div>
          <div class="text-[10px] text-slate-400 mt-1">Densidad Financiera del Activo</div>
        </div>
      </div>

      <!-- Detail Table & Donut Chart -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-5 glass-card p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-list-ol text-amber-400"></i> Desglose por Instrumento Financiero
            </h3>
            <span class="text-[10px] font-mono text-slate-400">Plan de Cuentas SSN (1.02)</span>
          </div>
          
          <div class="overflow-y-auto max-h-72">
            <table class="w-full text-left text-xs font-mono">
              <thead class="text-slate-400 bg-slate-900 sticky top-0 border-b border-slate-700 text-[11px]">
                <tr>
                  <th class="py-2 px-2">Instrumento</th>
                  <th class="py-2 px-2 text-right">Importe</th>
                  <th class="py-2 px-2 text-right">% Cartera</th>
                </tr>
              </thead>
              <tbody id="investmentsListBody" class="divide-y divide-slate-800"></tbody>
            </table>
          </div>
        </div>

        <div class="lg:col-span-7 glass-card p-5 rounded-xl">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-chart-pie text-emerald-400"></i> Composición y Asset Allocation del Portafolio
            </h3>
            <span id="invDonutSubtitle" class="text-xs text-slate-400 font-mono">...</span>
          </div>
          <div id="investmentsDonutChart" class="w-full h-72"></div>
        </div>
      </div>

      <!-- Top 20 Financial Rankings Section -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-ranking-star text-amber-400"></i> Rankings Financieros: Top 20 Aseguradoras
            </h3>
            <p class="text-xs text-slate-400">Selecciona el criterio de ordenamiento para explorar los líderes de mercado</p>
          </div>

          <!-- Ranking Metric Tabs -->
          <div class="flex flex-wrap items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs">
            <button onclick="setInvTopMetric('activo')" id="invTopMetricBtn-activo" class="px-3 py-1 rounded bg-amber-500 text-slate-950 font-bold">🏛️ Mayor Activo</button>
            <button onclick="setInvTopMetric('patrimonio_neto')" id="invTopMetricBtn-patrimonio_neto" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">⚖️ Mayor Patrimonio</button>
            <button onclick="setInvTopMetric('resultado_financiero')" id="invTopMetricBtn-resultado_financiero" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">📈 Mayor Res. Financiero</button>
            <button onclick="setInvTopMetric('inversiones')" id="invTopMetricBtn-inversiones" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">💰 Mayor Inversión (1.02)</button>
          </div>
        </div>

        <div class="w-full overflow-hidden">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/90 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2 px-2 text-center w-8">#</th>
                <th class="py-2 px-2 whitespace-nowrap text-left w-48 max-w-[200px]">Razón Social</th>
                <th class="py-2 px-2 text-center w-12">Tipo</th>
                <th class="py-2.5 px-2 text-right font-bold text-amber-300">Total Inversiones</th>
                <th class="py-2.5 px-2 text-right">Activo Total</th>
                <th class="py-2.5 px-2 text-right">Patrimonio Neto</th>
                <th class="py-2.5 px-2 text-right">Res. Financiero</th>
                <th class="py-2.5 px-2 text-right">ROI (%)</th>
                <th class="py-2.5 px-2 text-center w-14">Acción</th>
              </tr>
            </thead>
            <tbody id="invTopRankingTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 5: SOLVENCIA Y RATIOS SSN -->
    <!-- ======================================================== -->
    <section id="tab-solvencia-ratios" class="hidden space-y-6">
      
      <!-- Company Selector Header in Tab 5 -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-emerald-500 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="solvSelectedTitle" class="text-lg font-bold text-white">...</h2>
            <span id="solvSelectedBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">...</span>
          </div>
          <p id="solvSelectedSubtitle" class="text-xs text-slate-400 mt-1">Indicadores de Solvencia, Cobertura de Compromisos Técnicos y Ratios Regulatorios SSN</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-semibold flex items-center gap-1">
              <i class="fa-solid fa-building text-emerald-400"></i> Aseguradora:
            </span>
            <div class="relative w-64 sm:w-80" id="solvComboboxContainer">
              <button type="button" onclick="toggleCombobox('solvCombobox')" id="solvComboboxBtn" class="w-full flex items-center justify-between px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none hover:border-emerald-400 transition-all">
                <span id="solvComboboxLabel" class="truncate">...</span>
                <i class="fa-solid fa-chevron-down text-slate-400 text-[10px] ml-2 flex-shrink-0"></i>
              </button>
              <div id="solvComboboxDropdown" class="hidden combobox-dropdown-menu top-full right-0 w-full sm:w-96 mt-1 bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs max-h-80 flex flex-col">
                <div class="relative mb-2">
                  <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                  <input type="text" id="solvComboboxInput" oninput="filterCombobox('solvCombobox', this.value)" placeholder="Escribe para buscar aseguradora..." class="w-full pl-7 pr-2 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 font-normal">
                </div>
                <div id="solvComboboxList" class="overflow-y-auto max-h-64 divide-y divide-slate-800/40"></div>
              </div>
            </div>
          </div>

          <!-- Quick La Segunda Pills -->
          <div class="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/30">
            <span class="text-[10px] font-bold text-amber-300 mr-1">★ La Segunda:</span>
            <button onclick="onCompanyDropdownChange('0317')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Seguros Generales">0317</button>
            <button onclick="onCompanyDropdownChange('0618')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda ART">0618</button>
            <button onclick="onCompanyDropdownChange('0117')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Personas">0117</button>
            <button onclick="onCompanyDropdownChange('0436')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Retiro">0436</button>
          </div>
        </div>
      </div>

      <!-- Scope Selector Pills (Aseguradora vs Todas vs Tipo de Empresa) -->
      <div class="content-card-lower flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-layer-group text-emerald-400"></i> Alcance del Análisis:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setSolvScope('cia')" id="solvScopeBtn-cia" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏢 Aseguradora Seleccionada</button>
            <button onclick="setSolvScope('Todos')" id="solvScopeBtn-Todos" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 font-bold transition-all shadow-md shadow-emerald-500/20">🌐 Mercado Total (185 Cías)</button>
            <button onclick="setSolvScope('Patrimoniales y Mixtas')" id="solvScopeBtn-Patrimoniales y Mixtas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🚗 Patrimoniales y Mixtas</button>
            <button onclick="setSolvScope('Riesgos del Trabajo (ART)')" id="solvScopeBtn-Riesgos del Trabajo (ART)" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🦺 Riesgos del Trabajo (ART)</button>
            <button onclick="setSolvScope('Seguros de Personas')" id="solvScopeBtn-Seguros de Personas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">❤️ Seguros de Personas</button>
            <button onclick="setSolvScope('Seguros de Retiro')" id="solvScopeBtn-Seguros de Retiro" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏦 Seguros de Retiro</button>
          </div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades analizadas: <span id="solvEntitiesCount" class="font-mono font-bold text-white">185</span>
        </div>
      </div>

      <!-- Solvency Cards (Agregadas por Alcance o Individuales) -->
      <div class="content-card-lower grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">COBERTURA COMPROMISOS TÉCNICOS</div>
          <div id="solvCoberturaVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div id="solvCoberturaStatus" class="text-[10px] font-semibold mt-1">...</div>
          <div id="solvCoberturaSub" class="text-[10px] text-slate-400 mt-1 truncate">...</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">APALANCAMIENTO (PRIMAS/PN)</div>
          <div id="solvApalancamientoVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div id="solvApalancamientoSub" class="text-[10px] text-slate-400 mt-1">Exposición s/ Capital Propio</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">PREMIOS A COBRAR / PRIMAS</div>
          <div id="solvCobranzaVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div id="solvCobranzaSub" class="text-[10px] text-slate-400 mt-1">Índice de Cartera a Cobrar</div>
        </div>
        <div class="glass-card p-4 rounded-xl border-l-4 border-l-purple-500">
          <div class="text-[11px] font-semibold text-slate-400 uppercase">PATRIMONIO NETO TOTAL</div>
          <div id="solvPnVal" class="text-xl font-bold font-mono text-white mt-1">...</div>
          <div id="solvPnSub" class="text-[10px] text-slate-400 mt-1">Solvencia Patrimonial</div>
        </div>
      </div>

      <!-- Full Market Solvency Table with Sorters -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-ranking-star text-amber-400"></i> Tabla Comparativa de Solvencia y Ratios SSN
            </h3>
            <p class="text-xs text-slate-400">Compara los indicadores de solvencia, liquidez y apalancamiento del mercado</p>
          </div>

          <!-- Sorter Tabs -->
          <div class="flex flex-wrap items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs">
            <button onclick="setSolvSortMetric('cobertura_reservas')" id="solvSortBtn-cobertura_reservas" class="px-3 py-1 rounded bg-emerald-500 text-slate-950 font-bold">🛡️ Mayor Cobertura</button>
            <button onclick="setSolvSortMetric('combined_ratio')" id="solvSortBtn-combined_ratio" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">⚡ Menor Ratio Comb.</button>
            <button onclick="setSolvSortMetric('patrimonio_neto')" id="solvSortBtn-patrimonio_neto" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">🏛️ Mayor Patrimonio</button>
            <button onclick="setSolvSortMetric('apalancamiento')" id="solvSortBtn-apalancamiento" class="px-3 py-1 rounded text-slate-400 hover:text-white font-semibold">📉 Menor Apalancamiento</button>
          </div>
        </div>

        <div class="w-full overflow-hidden">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/90 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2 px-2 text-center w-8">#</th>
                <th class="py-2 px-2 whitespace-nowrap text-left w-48 max-w-[200px]">Razón Social</th>
                <th class="py-2 px-2 text-center w-12">Tipo</th>
                <th class="py-2.5 px-2 text-right font-bold text-emerald-300">Cobertura (x)</th>
                <th class="py-2.5 px-2 text-right">Ratio Comb.</th>
                <th class="py-2.5 px-2 text-right">Apalancamiento</th>
                <th class="py-2.5 px-2 text-right">Premios / Primas</th>
                <th class="py-2.5 px-2 text-right">Patrimonio Neto</th>
                <th class="py-2.5 px-2 text-right">Activo Total</th>
                <th class="py-2.5 px-2 text-center w-14">Acción</th>
              </tr>
            </thead>
            <tbody id="solvencyRankingTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 6: RATIOS DE GESTIÓN & SCORECARD (NUEVO) -->
    <!-- ======================================================== -->
    <section id="tab-ratios-gestion" class="hidden space-y-6">
      
      <!-- Company Selector Header in Tab 6 -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-indigo-500 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="gestSelectedTitle" class="text-lg font-bold text-white">...</h2>
            <span id="gestSelectedBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">...</span>
          </div>
          <p id="gestSelectedSubtitle" class="text-xs text-slate-400 mt-1">Tablero de Control de Gestión, Semáforos de Alerta Temprana y Comparativa Benchmark</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-semibold flex items-center gap-1">
              <i class="fa-solid fa-building text-indigo-400"></i> Aseguradora:
            </span>
            <div class="relative w-64 sm:w-80" id="gestComboboxContainer">
              <button type="button" onclick="toggleCombobox('gestCombobox')" id="gestComboboxBtn" class="w-full flex items-center justify-between px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none hover:border-indigo-400 transition-all">
                <span id="gestComboboxLabel" class="truncate">...</span>
                <i class="fa-solid fa-chevron-down text-slate-400 text-[10px] ml-2 flex-shrink-0"></i>
              </button>
              <div id="gestComboboxDropdown" class="hidden combobox-dropdown-menu top-full right-0 w-full sm:w-96 mt-1 bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs max-h-80 flex flex-col">
                <div class="relative mb-2">
                  <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                  <input type="text" id="gestComboboxInput" oninput="filterCombobox('gestCombobox', this.value)" placeholder="Escribe para buscar aseguradora..." class="w-full pl-7 pr-2 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-400 font-normal">
                </div>
                <div id="gestComboboxList" class="overflow-y-auto max-h-64 divide-y divide-slate-800/40"></div>
              </div>
            </div>
          </div>

          <!-- Quick La Segunda Pills -->
          <div class="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/30">
            <span class="text-[10px] font-bold text-amber-300 mr-1">★ La Segunda:</span>
            <button onclick="onCompanyDropdownChange('0317')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Seguros Generales">0317</button>
            <button onclick="onCompanyDropdownChange('0618')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda ART">0618</button>
            <button onclick="onCompanyDropdownChange('0117')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Personas">0117</button>
            <button onclick="onCompanyDropdownChange('0436')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Retiro">0436</button>
          </div>
        </div>
      </div>

      <!-- Scope Selector Pills (Aseguradora vs Todas vs Tipo de Empresa) -->
      <div class="content-card-lower flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-layer-group text-indigo-400"></i> Alcance del Análisis:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setGestScope('cia')" id="gestScopeBtn-cia" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏢 Aseguradora Seleccionada</button>
            <button onclick="setGestScope('Todos')" id="gestScopeBtn-Todos" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-500 text-white font-bold transition-all shadow-md shadow-indigo-500/20">🌐 Mercado Total (185 Cías)</button>
            <button onclick="setGestScope('Patrimoniales y Mixtas')" id="gestScopeBtn-Patrimoniales y Mixtas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🚗 Patrimoniales y Mixtas</button>
            <button onclick="setGestScope('Riesgos del Trabajo (ART)')" id="gestScopeBtn-Riesgos del Trabajo (ART)" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🦺 Riesgos del Trabajo (ART)</button>
            <button onclick="setGestScope('Seguros de Personas')" id="gestScopeBtn-Seguros de Personas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">❤️ Seguros de Personas</button>
            <button onclick="setGestScope('Seguros de Retiro')" id="gestScopeBtn-Seguros de Retiro" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏦 Seguros de Retiro</button>
          </div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades analizadas: <span id="gestEntitiesCount" class="font-mono font-bold text-white">185</span>
        </div>
      </div>

      <!-- SCORECARD 4 DIMENSIONES CON SEMÁFOROS -->
      
      <!-- Dimensión 1: Suscripción & Eficiencia Operativa -->
      <div class="glass-card p-5 rounded-xl space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
            <h3 class="text-xs font-bold text-white uppercase tracking-wider">I. Suscripción y Eficiencia Operativa</h3>
          </div>
          <span class="text-[11px] text-slate-400">Base Devengada SSN</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <!-- Ratio Combinado -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Ratio Combinado</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiCombinedVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiCombinedBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiCombinedBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <!-- Loss Ratio -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Loss Ratio (Siniestralidad)</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiLossVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiLossBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiLossBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <!-- Costo de Adquisición -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Costo Adquisición (Prod.)</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiCommVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiCommBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiCommBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <!-- Gastos de Explotación -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Carga Estructura (Admin)</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiExpVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiExpBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiExpBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <!-- Tasa de Retención -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Retención de Riesgo</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiRetVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiRetBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiRetBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
        </div>
      </div>

      <!-- Dimensión 2 & 3: Financiero & Solvencia -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Dimensión 2: Gestión Financiera -->
        <div class="glass-card p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              <h3 class="text-xs font-bold text-white uppercase tracking-wider">II. Rendimiento Financiero & Inversiones</h3>
            </div>
            <span class="text-[11px] text-slate-400">Asset Management</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Rendimiento Inversiones (ROI)</div>
              <div class="flex items-baseline justify-between mt-1">
                <span id="gKpiRoiVal" class="text-lg font-bold font-mono text-white">...</span>
                <span id="gKpiRoiBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
              </div>
              <div id="gKpiRoiBench" class="text-[9px] text-slate-400 mt-1">...</div>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Densidad Inversiones / Activo</div>
              <div class="flex items-baseline justify-between mt-1">
                <span id="gKpiDensVal" class="text-lg font-bold font-mono text-white">...</span>
                <span id="gKpiDensBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
              </div>
              <div id="gKpiDensBench" class="text-[9px] text-slate-400 mt-1">...</div>
            </div>
          </div>
        </div>

        <!-- Dimensión 3: Solvencia & Liquidez -->
        <div class="glass-card p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <h3 class="text-xs font-bold text-white uppercase tracking-wider">III. Solvencia, Liquidez & Cobranzas</h3>
            </div>
            <span class="text-[11px] text-slate-400">Normativa SSN</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Cobertura SSN</div>
              <div class="flex items-baseline justify-between mt-1">
                <span id="gKpiCobVal" class="text-lg font-bold font-mono text-white">...</span>
                <span id="gKpiCobBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
              </div>
              <div id="gKpiCobBench" class="text-[9px] text-slate-400 mt-1">...</div>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Apalancamiento</div>
              <div class="flex items-baseline justify-between mt-1">
                <span id="gKpiApalVal" class="text-lg font-bold font-mono text-white">...</span>
                <span id="gKpiApalBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
              </div>
              <div id="gKpiApalBench" class="text-[9px] text-slate-400 mt-1">...</div>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Cartera a Cobrar</div>
              <div class="flex items-baseline justify-between mt-1">
                <span id="gKpiCobranzaVal" class="text-lg font-bold font-mono text-white">...</span>
                <span id="gKpiCobranzaBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
              </div>
              <div id="gKpiCobranzaBench" class="text-[9px] text-slate-400 mt-1">...</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dimensión 4: Rentabilidad & Creación de Valor -->
      <div class="glass-card p-5 rounded-xl space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
            <h3 class="text-xs font-bold text-white uppercase tracking-wider">IV. Rentabilidad Final & Creación de Valor</h3>
          </div>
          <span class="text-[11px] text-slate-400">Retorno sobre Capital</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">ROE (Retorno s/ PN)</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiRoeVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiRoeBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiRoeBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">ROA (Retorno s/ Activo)</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiRoaVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiRoaBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiRoaBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Margen Técnico Operativo</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiMargenTecVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiMargenTecBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiMargenTecBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div class="text-[10px] text-slate-400 uppercase font-semibold">Margen Neto Final</div>
            <div class="flex items-baseline justify-between mt-1">
              <span id="gKpiMargenNetoVal" class="text-lg font-bold font-mono text-white">...</span>
              <span id="gKpiMargenNetoBadge" class="text-[10px] font-bold px-1.5 py-0.5 rounded">...</span>
            </div>
            <div id="gKpiMargenNetoBench" class="text-[9px] text-slate-400 mt-1">...</div>
          </div>
        </div>
      </div>

      <!-- 1. FULL WIDTH: RADAR / SPIDER CHART DE EFICIENCIA -->
      <div class="glass-card p-5 rounded-xl w-full space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-chart-line text-indigo-400"></i> Radar de Eficiencia Aseguradora (6 Ejes)
            </h3>
            <p class="text-xs text-slate-400">Evaluación multidimensional: silueta de la aseguradora vs. promedio benchmark del segmento</p>
          </div>
          <span class="text-xs text-slate-400 font-mono bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-700">Escala 0 (Centro / Déficit) a 100 (Borde / Óptimo)</span>
        </div>

        <div id="managementRadarChart" class="w-full h-[460px]"></div>

        <!-- Desglose de los 6 Ejes en Grid de 6 columnas -->
        <div class="pt-3 border-t border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-circle-info text-indigo-400"></i> Desglose de Rendimiento por Eje (Puntajes y Valores de Balance)
            </span>
            <span class="text-[10px] text-slate-400 font-mono">Puntaje Normalizado (0-100) y Comparativa vs. Benchmark</span>
          </div>
          <div id="radarAxesBreakdown" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs font-mono"></div>
        </div>
      </div>

      <!-- 2. FULL WIDTH: DIAGNÓSTICO EJECUTIVO AUTOMATIZADO -->
      <div class="glass-card p-5 rounded-xl w-full space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-clipboard-check text-emerald-400"></i> Diagnóstico Ejecutivo Automatizado
            </h3>
            <p class="text-xs text-slate-400">Resumen cualitativo y cuantitativo derivado de la matriz de semáforos inteligentes</p>
          </div>

          <!-- Traffic light legend -->
          <div class="flex items-center gap-3 text-xs bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
            <span class="text-emerald-400 font-semibold flex items-center gap-1">🟢 Saludable (Óptimo)</span>
            <span class="text-amber-400 font-semibold flex items-center gap-1">🟡 Precaución (Tolerancia)</span>
            <span class="text-rose-400 font-semibold flex items-center gap-1">🔴 Alerta (Déficit/Crítico)</span>
          </div>
        </div>

        <div id="execDiagnosticContent" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300">
          <!-- Dynamically populated into 2 columns (Fortalezas vs Desvíos) -->
        </div>
      </div>

      <!-- TABLA CLASIFICATORIA CON SEMÁFOROS Y FILTROS RÁPIDOS -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-list-check text-indigo-400"></i> Matriz General de Ratios de Gestión & Semáforos
            </h3>
            <p class="text-xs text-slate-400">Evaluación multidimensional de todas las entidades del segmento</p>
          </div>

          <!-- Quick Alert Filters -->
          <div class="flex flex-wrap items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-700 text-xs">
            <button onclick="setGestFilterMode('all')" id="gestFiltBtn-all" class="px-2.5 py-1 rounded bg-indigo-500 text-white font-bold">Todas</button>
            <button onclick="setGestFilterMode('loss_high')" id="gestFiltBtn-loss_high" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-semibold">🔴 Pérdida Téc. (>100%)</button>
            <button onclick="setGestFilterMode('cob_low')" id="gestFiltBtn-cob_low" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-semibold">🔴 Déficit SSN (<1.0x)</button>
            <button onclick="setGestFilterMode('integral_win')" id="gestFiltBtn-integral_win" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-semibold">🟢 Ganancia Integral</button>
            <button onclick="setGestFilterMode('slow_collect')" id="gestFiltBtn-slow_collect" class="px-2.5 py-1 rounded text-slate-400 hover:text-white font-semibold">🟡 Cobranza Lenta (>35%)</button>
          </div>
        </div>

        <div class="w-full overflow-x-auto max-h-[500px]">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/95 sticky top-0 z-10 border-b border-slate-700 text-[11px]">
              <tr>
                <th class="py-2 px-2 text-center w-8">#</th>
                <th class="py-2 px-2 whitespace-nowrap text-left w-44 max-w-[180px]">Razón Social</th>
                <th class="py-2 px-2 text-center w-12">Tipo</th>
                <th class="py-2 px-2 text-right">Ratio Comb.</th>
                <th class="py-2 px-2 text-right">Loss Ratio</th>
                <th class="py-2 px-2 text-right">Comisiones</th>
                <th class="py-2 px-2 text-right">Admin</th>
                <th class="py-2 px-2 text-right">ROI Inv.</th>
                <th class="py-2 px-2 text-right">Cobertura</th>
                <th class="py-2 px-2 text-right">Apalanc.</th>
                <th class="py-2 px-2 text-right">Premios/Primas</th>
                <th class="py-2 px-2 text-right">ROE</th>
                <th class="py-2 px-2 text-center w-14">Acción</th>
              </tr>
            </thead>
            <tbody id="managementTableBody" class="divide-y divide-slate-800 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 7: BALANCES CONTABLES SSN (ÁRBOL MULTINIVEL) -->
    <!-- ======================================================== -->
    <section id="tab-balances" class="hidden space-y-6">
      
      <!-- Company / Scope Selector Header -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-emerald-500 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h2 id="balSelectedTitle" class="text-lg font-bold text-white">Mercado Total Consolidado</h2>
            <span id="balSelectedBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">185 Cías</span>
          </div>
          <p id="balSelectedSubtitle" class="text-xs text-slate-400 mt-1">Plan de Cuentas Oficial SSN • Apertura Jerárquica Multinivel por Cuentas e Importes</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-semibold flex items-center gap-1">
              <i class="fa-solid fa-building text-emerald-400"></i> Aseguradora:
            </span>
            <div class="relative w-64 sm:w-80" id="balComboboxContainer">
              <button type="button" onclick="toggleCombobox('balCombobox')" id="balComboboxBtn" class="w-full flex items-center justify-between px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none hover:border-emerald-400 transition-all">
                <span id="balComboboxLabel" class="truncate">Seleccionar aseguradora...</span>
                <i class="fa-solid fa-chevron-down text-slate-400 text-[10px] ml-2 flex-shrink-0"></i>
              </button>
              <div id="balComboboxDropdown" class="hidden combobox-dropdown-menu top-full right-0 w-full sm:w-96 mt-1 bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs max-h-80 flex flex-col">
                <div class="relative mb-2">
                  <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                  <input type="text" id="balComboboxInput" oninput="filterCombobox('balCombobox', this.value)" placeholder="Escribe para buscar aseguradora..." class="w-full pl-7 pr-2 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 font-normal">
                </div>
                <div id="balComboboxList" class="overflow-y-auto max-h-64 divide-y divide-slate-800/40"></div>
              </div>
            </div>
          </div>

          <!-- Quick La Segunda Pills -->
          <div class="flex items-center gap-1 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/30">
            <span class="text-[10px] font-bold text-amber-300 mr-1">★ La Segunda:</span>
            <button onclick="onCompanyDropdownChange('0317')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Seguros Generales">0317</button>
            <button onclick="onCompanyDropdownChange('0618')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda ART">0618</button>
            <button onclick="onCompanyDropdownChange('0117')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Personas">0117</button>
            <button onclick="onCompanyDropdownChange('0436')" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 transition-colors" title="La Segunda Retiro">0436</button>
          </div>
        </div>
      </div>

      <!-- Scope Selector Pills (Aseguradora vs Todas vs Tipo de Empresa vs Grupo) -->
      <div class="content-card-lower flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-layer-group text-emerald-400"></i> Alcance del Balance:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setBalScope('market')" id="balScopeBtn-market" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 font-bold transition-all shadow-md shadow-emerald-500/20">🌐 Mercado Total (185 Cías)</button>
            <button onclick="setBalScope('group')" id="balScopeBtn-group" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-amber-300 hover:bg-slate-700 transition-all font-bold">🏛️ Grupo Asegurador</button>
            <button onclick="setBalScope('Patrimoniales y Mixtas')" id="balScopeBtn-Patrimoniales y Mixtas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🚗 Patrimoniales y Mixtas</button>
            <button onclick="setBalScope('Riesgos del Trabajo (ART)')" id="balScopeBtn-Riesgos del Trabajo (ART)" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🦺 Riesgos del Trabajo (ART)</button>
            <button onclick="setBalScope('Seguros de Personas')" id="balScopeBtn-Seguros de Personas" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">❤️ Seguros de Personas</button>
            <button onclick="setBalScope('Seguros de Retiro')" id="balScopeBtn-Seguros de Retiro" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏦 Seguros de Retiro</button>
            <button onclick="setBalScope('cia')" id="balScopeBtn-cia" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">🏢 Empresa Seleccionada</button>
          </div>
        </div>
        <div class="text-xs text-slate-400">
          Entidades consolidadas: <span id="balEntitiesCount" class="font-mono font-bold text-white">185</span>
        </div>
      </div>

      <!-- Statement Selector Switch (5 Tabs: Patrimonial, EDR, Estructura Tec, Estructura Fin, Tec por Ramo) -->
      <div class="content-card-lower glass-card p-3 rounded-xl flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold"><i class="fa-solid fa-book-open text-amber-400"></i> Estado Contable:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setBalStatement('patrimonial')" id="balStmtBtn-patrimonial" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20">🏛️ Estado Patrimonial</button>
            <button onclick="setBalStatement('edr')" id="balStmtBtn-edr" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">📈 Estado de Resultados (EDR)</button>
            <button onclick="setBalStatement('tec')" id="balStmtBtn-tec" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">⚡ Estructura Técnica</button>
            <button onclick="setBalStatement('fin')" id="balStmtBtn-fin" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">💰 Estructura Financiera</button>
            <button onclick="setBalStatement('ramo')" id="balStmtBtn-ramo" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">📦 Estructura Técnica por Ramo</button>
          </div>
        </div>

        <!-- Subramo Dropdown (only visible when 'ramo' is active) -->
        <div id="balSubramoContainer" class="hidden flex items-center gap-2">
          <span class="text-xs text-amber-300 font-semibold"><i class="fa-solid fa-tag"></i> Subramo:</span>
          <select id="balSubramoSelect" onchange="setBalSubramo(this.value)" class="px-3 py-1.5 bg-slate-900 border border-amber-500/50 rounded-lg text-xs text-amber-200 font-semibold focus:outline-none max-w-[260px] truncate"></select>
        </div>
      </div>

      <!-- Balance Summary KPI Banner -->
      <div id="balKpiBanner" class="content-card-lower grid grid-cols-2 sm:grid-cols-4 gap-4">
        <!-- Dynamically populated according to statement type -->
      </div>

      <!-- Interactive Tree Action Bar (Global Controls & Account Search) -->
      <div class="content-card-lower glass-card p-4 rounded-xl flex flex-wrap items-center justify-between gap-3 border border-slate-800">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs text-slate-400 font-semibold flex items-center gap-1"><i class="fa-solid fa-folder-tree text-brand-blue"></i> Controles del Árbol:</span>
          <button type="button" onclick="expandAllBalNodes()" class="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/40 text-xs font-bold text-emerald-300 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm">
            <span class="text-emerald-400 font-mono font-black text-sm leading-none">+</span> Expandir Todo
          </button>
          <button type="button" onclick="collapseBalToLevel(2)" class="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/40 text-xs font-bold text-amber-300 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm">
            <span class="text-amber-400 font-mono font-black text-sm leading-none">≡</span> Colapsar a Rubros (N2)
          </button>
          <button type="button" onclick="collapseBalToLevel(1)" class="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/40 text-xs font-bold text-rose-300 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm">
            <span class="text-rose-400 font-mono font-black text-sm leading-none">−</span> Colapsar a Capítulos (N1)
          </button>
        </div>

        <div class="flex items-center gap-3">
          <!-- Search within balance -->
          <div class="relative w-56 sm:w-72">
            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
            <input type="text" id="balAccountSearchInput" oninput="filterBalTree(this.value)" placeholder="Buscar cuenta o código..." class="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-blue font-normal">
          </div>

          <!-- Export button -->
          <button onclick="exportBalanceCSV()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20">
            <i class="fa-solid fa-file-excel"></i> Exportar CSV
          </button>
        </div>
      </div>

      <!-- Balance Hierarchical Tree Table -->
      <div class="content-card-lower glass-card p-5 rounded-xl w-full">
        <div class="w-full overflow-x-auto max-h-[700px]">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/95 sticky top-0 z-10 border-b border-slate-700 text-[11px] font-mono">
              <tr>
                <th class="py-2.5 px-3 text-center w-12">Abrir</th>
                <th class="py-2.5 px-3 text-left w-48 font-mono">Código de Cuenta</th>
                <th class="py-2.5 px-3 text-left">Denominación / Rubro Contable SSN</th>
                <th class="py-2.5 px-3 text-right font-bold text-white">Saldo ($ ARS)</th>
                <th class="py-2.5 px-3 text-right w-28">% Capítulo</th>
                <th class="py-2.5 px-3 text-center w-16">Nivel</th>
              </tr>
            </thead>
            <tbody id="balanceTreeTableBody" class="divide-y divide-slate-800/60 font-mono text-[11px]"></tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 4: RANKINGS DE PRODUCCIÓN POR RAMOS Y SUBRAMOS -->
    <!-- ======================================================== -->
    <section id="tab-rankings-ramos" class="hidden space-y-6">
      
      <!-- Hierarchical Selector Header (Macro-Sección -> Ramo Agrupado -> Subramo / Todo el Ramo) -->
      <div class="glass-card header-card-sticky p-5 rounded-xl border-l-4 border-l-amber-500 flex flex-col gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-3">
              <h2 id="rrSelectedTitle" class="text-lg font-bold text-white">Ranking de Producción por Ramos</h2>
              <span id="rrSelectedBadge" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">Subramo SSN</span>
            </div>
            <p id="rrSelectedSubtitle" class="text-xs text-slate-400 mt-1">Explora el liderazgo de mercado, cuotas de emisión y siniestralidad técnica por rama o subrama</p>
          </div>

          <!-- Mode Switch: Grupos vs Aseguradoras -->
          <div class="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-700">
            <button type="button" onclick="setRamosRankMode('groups')" id="rrModeBtn-groups" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5">
              <i class="fa-solid fa-building-columns"></i> 🏛️ Grupos Aseguradores
            </button>
            <button type="button" onclick="setRamosRankMode('companies')" id="rrModeBtn-companies" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5">
              <i class="fa-solid fa-building"></i> 🏢 Aseguradoras Individuales
            </button>
          </div>
        </div>

        <!-- 3-Tier Navigation Controls -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-slate-800">
          <!-- 1. Macro Sección -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <i class="fa-solid fa-layer-group text-amber-400"></i> 1. Macro-Sección:
            </label>
            <div id="rrSectionButtons" class="flex flex-wrap gap-1.5"></div>
          </div>

          <!-- 2. Ramo Agrupado -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <i class="fa-solid fa-folder-tree text-emerald-400"></i> 2. Ramo Agrupado:
            </label>
            <div id="rrGroupButtons" class="flex flex-wrap gap-1.5"></div>
          </div>

          <!-- 3. Apertura de Subramo -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
              <i class="fa-solid fa-tags text-sky-400"></i> 3. Nivel de Apertura / Subramo:
            </label>
            <select id="rrSubramoSelect" onchange="setRamosSubramo(this.value)" class="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-amber-400 w-full">
            </select>
          </div>
        </div>
      </div>

      <!-- KPI Summary Cards of Selected Branch -->
      <div id="rrKpiBanner" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5"></div>

      <!-- Concentration & Market Share Chart -->
      <div class="glass-card p-5 rounded-xl">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-chart-pie text-amber-400"></i> Concentración de Mercado (Top 10 de la Rama)
            </h3>
            <p class="text-xs text-slate-400">Distribución de Primas Emitidas y Cuotas de Mercado de los líderes en esta rama</p>
          </div>
        </div>
        <div id="rrMarketSharePlot" class="w-full h-72"></div>
      </div>

      <!-- Branch Ranking Table -->
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-trophy text-amber-400"></i> Ranking Completo en la Rama
            </h3>
            <p class="text-xs text-slate-400">Entidades operativas ordenadas por Primas Emitidas en la rama seleccionada</p>
          </div>
          
          <div class="flex items-center gap-3">
            <input type="text" id="rrTableFilter" oninput="filterRamosRankingTable(this.value)" placeholder="Buscar aseguradora o grupo..." 
                   class="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-amber-400 w-60">
            <button onclick="exportRamosRankCSV()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1.5">
              <i class="fa-solid fa-file-csv text-brand-green"></i> Exportar
            </button>
          </div>
        </div>

        <div class="w-full overflow-x-auto max-h-[600px]">
          <table class="w-full text-left text-xs border-collapse table-auto">
            <thead class="text-slate-400 bg-slate-900/95 sticky top-0 z-10 border-b border-slate-700 text-[11px] font-mono">
              <tr>
                <th class="py-2.5 px-2 text-center w-8">#</th>
                <th class="py-2.5 px-2 text-left w-56">Aseguradora / Grupo Económico</th>
                <th class="py-2.5 px-2 text-center w-16">Tipo / Cías</th>
                <th class="py-2.5 px-2 text-right font-bold text-white">Primas Emitidas</th>
                <th class="py-2.5 px-2 text-right w-28">Market Share</th>
                <th class="py-2.5 px-2 text-right">Siniestros</th>
                <th class="py-2.5 px-2 text-right">Siniestralidad (Loss Ratio)</th>
                <th class="py-2.5 px-2 text-right font-bold">Resultado Técnico</th>
                <th class="py-2.5 px-2 text-center w-16">Acción</th>
              </tr>
            </thead>
            <tbody id="rrTableBody" class="divide-y divide-slate-800/60 font-mono text-[11px]"></tbody>
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
      selectedCompanyCode: '0436',
      highlightedCiaCode: null,
      marketRankingMode: 'groups',
      selectedGroupId: 'sancor',
      ramosRankSections: ['personas'],
      ramosRankGroups: ['vida'],
      ramosRankSubramo: 'all',
      ramosRankMode: 'groups',
      ramosRankSearchQuery: '',
      ramosScope: 'cia',
      invScope: 'cia',
      invTopMetric: 'activo',
      solvScope: 'Todos',
      solvSortMetric: 'cobertura_reservas',
      gestScope: 'cia',
      gestFilterMode: 'all',
      balScope: 'market',
      balStatement: 'patrimonial',
      balSubramo: '1.030.01',
      balSearchQuery: '',
      balExpandedNodes: new Set([
        '1.00.00.00.00.00.00.00', '2.00.00.00.00.00.00.00', '3.00.00.00.00.00.00.00',
        '4.00.00.00.00.00.00.00', '5.00.00.00.00.00.00.00',
        '1.01.00.00.00.00.00.00', '1.02.00.00.00.00.00.00', '1.03.00.00.00.00.00.00',
        '1.04.00.00.00.00.00.00', '1.05.00.00.00.00.00.00', '1.06.00.00.00.00.00.00',
        '2.01.00.00.00.00.00.00', '2.02.00.00.00.00.00.00', '2.03.00.00.00.00.00.00',
        '3.01.00.00.00.00.00.00', '3.02.00.00.00.00.00.00', '3.03.00.00.00.00.00.00',
        '3.04.00.00.00.00.00.00', '3.05.00.00.00.00.00.00',
        '4.01.00.00.00.00.00.00', '4.02.00.00.00.00.00.00',
        '5.01.00.00.00.00.00.00', '5.02.00.00.00.00.00.00'
      ])
    }};

    // Standardized Financial Notation:
    // B = Billones (10^12)
    // MM = Miles de Millones (10^9)
    // M = Millones (10^6)
    // K = Miles (10^3)
    function formatARS(val) {{
      if (val === undefined || val === null || isNaN(val)) return '$0';
      const absVal = Math.abs(val);
      const sign = val < 0 ? '-' : '';
      if (absVal >= 1e12) {{
        return sign + '$' + (absVal / 1e12).toFixed(2) + ' B';
      }} else if (absVal >= 1e9) {{
        return sign + '$' + (absVal / 1e9).toFixed(2) + ' MM';
      }} else if (absVal >= 1e6) {{
        return sign + '$' + (absVal / 1e6).toFixed(2) + ' M';
      }} else if (absVal >= 1e3) {{
        return sign + '$' + (absVal / 1e3).toFixed(1) + ' K';
      }} else {{
        return sign + '$' + absVal.toLocaleString('es-AR', {{ maximumFractionDigits: 0 }});
      }}
    }}

    function formatARSCompact(val) {{
      return formatARS(val);
    }}

    function formatPercent(val) {{
      if (val === undefined || val === null || isNaN(val)) return '0.0%';
      return val.toFixed(1) + '%';
    }}

    function getTipoBadge(tipo) {{
      if (tipo === 'Patrimoniales y Mixtas') {{
        return '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30" title="Patrimoniales y Mixtas">PM</span>';
      }} else if (tipo === 'Riesgos del Trabajo (ART)') {{
        return '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30" title="Riesgos del Trabajo (ART)">ART</span>';
      }} else if (tipo === 'Seguros de Personas') {{
        return '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30" title="Seguros de Personas">SP</span>';
      }} else if (tipo === 'Seguros de Retiro') {{
        return '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30" title="Seguros de Retiro">SR</span>';
      }}
      return `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">${{tipo}}</span>`;
    }}

    // Traffic light badge evaluator
    function getTrafficLightBadge(val, metric) {{
      if (val === undefined || val === null || isNaN(val)) return '<span class="text-slate-500">-</span>';
      
      let status = 'green', label = 'Óptimo';

      if (metric === 'combined_ratio') {{
        if (val <= 100.0) {{ status = 'green'; label = 'Ganancia'; }}
        else if (val <= 108.0) {{ status = 'yellow'; label = 'Tolerancia'; }}
        else {{ status = 'red'; label = 'Pérdida'; }}
      }} else if (metric === 'loss_ratio') {{
        if (val <= 65.0) {{ status = 'green'; label = 'Baja'; }}
        else if (val <= 75.0) {{ status = 'yellow'; label = 'Normal'; }}
        else {{ status = 'red'; label = 'Elevada'; }}
      }} else if (metric === 'comm_ratio') {{
        if (val <= 18.0) {{ status = 'green'; label = 'Eficiente'; }}
        else if (val <= 25.0) {{ status = 'yellow'; label = 'Medio'; }}
        else {{ status = 'red'; label = 'Alto'; }}
      }} else if (metric === 'exp_ratio') {{
        if (val <= 18.0) {{ status = 'green'; label = 'Controlado'; }}
        else if (val <= 25.0) {{ status = 'yellow'; label = 'Moderado'; }}
        else {{ status = 'red'; label = 'Excesivo'; }}
      }} else if (metric === 'retencion_ratio') {{
        if (val >= 65.0 && val <= 90.0) {{ status = 'green'; label = 'Equilibrada'; }}
        else if (val >= 50.0 && val <= 95.0) {{ status = 'yellow'; label = 'Atención'; }}
        else {{ status = 'red'; label = 'Desbalance'; }}
      }} else if (metric === 'roi_inversiones') {{
        if (val >= 3.0) {{ status = 'green'; label = 'Rentable'; }}
        else if (val >= 0.0) {{ status = 'yellow'; label = 'Neutro'; }}
        else {{ status = 'red'; label = 'Negativo'; }}
      }} else if (metric === 'densidad_inversiones') {{
        if (val >= 65.0) {{ status = 'green'; label = 'Alta'; }}
        else if (val >= 50.0) {{ status = 'yellow'; label = 'Media'; }}
        else {{ status = 'red'; label = 'Baja'; }}
      }} else if (metric === 'cobertura_reservas') {{
        if (val >= 1.15) {{ status = 'green'; label = 'Superávit'; }}
        else if (val >= 1.00) {{ status = 'yellow'; label = 'Límite SSN'; }}
        else {{ status = 'red'; label = 'Déficit'; }}
      }} else if (metric === 'apalancamiento') {{
        if (val <= 2.50) {{ status = 'green'; label = 'Holgado'; }}
        else if (val <= 3.50) {{ status = 'yellow'; label = 'Moderado'; }}
        else {{ status = 'red'; label = 'Exigido'; }}
      }} else if (metric === 'calidad_cartera') {{
        if (val <= 30.0) {{ status = 'green'; label = 'Rápida'; }}
        else if (val <= 42.0) {{ status = 'yellow'; label = 'Regular'; }}
        else {{ status = 'red'; label = 'Lenta'; }}
      }} else if (metric === 'roe' || metric === 'margen_neto') {{
        if (val >= 5.0) {{ status = 'green'; label = 'Rentable'; }}
        else if (val >= 0.0) {{ status = 'yellow'; label = 'Neutro'; }}
        else {{ status = 'red'; label = 'Pérdida'; }}
      }}

      if (status === 'green') {{
        return `<span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded text-[9px] font-bold">🟢 ${{label}}</span>`;
      }} else if (status === 'yellow') {{
        return `<span class="bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded text-[9px] font-bold">🟡 ${{label}}</span>`;
      }} else {{
        return `<span class="bg-rose-500/20 text-rose-300 border border-rose-500/30 px-1.5 py-0.5 rounded text-[9px] font-bold">🔴 ${{label}}</span>`;
      }}
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

      // 1. Set macro entity values
      const me = data.macro_entidades || data.macro_ramos;
      if (me) {{
        const totEmit = me.total_mercado_emitidas;
        const totDev = me.total_mercado_devengadas;

        document.getElementById('macroTotalVal').innerText = `${{formatARS(totEmit)}} Emitidas (${{formatARS(totDev)}} Dev.)`;

        // Patrimoniales
        document.getElementById('macroPatrimVal').innerText = formatARS(me.patrimoniales_emitidas);
        document.getElementById('macroPatrimSub').innerText = `Dev: ${{formatARS(me.patrimoniales_devengadas)}} • ${{((me.patrimoniales_emitidas / totEmit) * 100).toFixed(1)}}% (${{me.patrimoniales_entidades}} Cías)`;

        // ART
        document.getElementById('macroArtVal').innerText = formatARS(me.art_emitidas);
        document.getElementById('macroArtSub').innerText = `Dev: ${{formatARS(me.art_devengadas)}} • ${{((me.art_emitidas / totEmit) * 100).toFixed(1)}}% (${{me.art_entidades}} Cías)`;

        // Personas
        document.getElementById('macroPersonasVal').innerText = formatARS(me.personas_emitidas);
        document.getElementById('macroPersonasSub').innerText = `Dev: ${{formatARS(me.personas_devengadas)}} • ${{((me.personas_emitidas / totEmit) * 100).toFixed(1)}}% (${{me.personas_entidades}} Cías)`;

        // Retiro
        document.getElementById('macroRetiroVal').innerText = formatARS(me.retiro_emitidas);
        document.getElementById('macroRetiroSub').innerText = `Dev: ${{formatARS(me.retiro_devengadas)}} • ${{((me.retiro_emitidas / totEmit) * 100).toFixed(1)}}% (${{me.retiro_entidades}} Cías)`;
      }}

      // 2. Set macro product line values
      const mp = data.macro_productos;
      if (mp) {{
        // Patrimoniales
        document.getElementById('prodPatrimPrimas').innerText = formatARS(mp.patrimoniales.primas);
        document.getElementById('prodPatrimDetails').innerText = `${{mp.patrimoniales.participacion}}% Mercado • Sin: ${{mp.patrimoniales.siniestralidad}}% (Siniestros: ${{formatARS(mp.patrimoniales.siniestros)}})`;

        // ART
        document.getElementById('prodArtPrimas').innerText = formatARS(mp.art.primas);
        document.getElementById('prodArtDetails').innerText = `${{mp.art.participacion}}% Mercado • Sin: ${{mp.art.siniestralidad}}% (Siniestros: ${{formatARS(mp.art.siniestros)}})`;

        // Personas
        document.getElementById('prodPersonasPrimas').innerText = formatARS(mp.personas.primas);
        document.getElementById('prodPersonasDetails').innerText = `${{mp.personas.participacion}}% Mercado • Sin: ${{mp.personas.siniestralidad}}% (Siniestros: ${{formatARS(mp.personas.siniestros)}})`;

        // Retiro
        document.getElementById('prodRetiroPrimas').innerText = formatARS(mp.retiro.primas);
        document.getElementById('prodRetiroDetails').innerText = `${{mp.retiro.participacion}}% Mercado • Sin: ${{mp.retiro.siniestralidad}}% (Siniestros: ${{formatARS(mp.retiro.siniestros)}})`;
      }}

      // Populate Balances subramos select
      initBalancesSubramos();

      // Pick default high profile company (0436 or 0117 or 0317)
      if (data.companies_by_code['0436']) {{
        state.selectedCompanyCode = '0436';
      }} else if (data.companies_by_code['0117']) {{
        state.selectedCompanyCode = '0117';
      }} else if (data.companies_by_code['0317']) {{
        state.selectedCompanyCode = '0317';
      }} else if (data.companies.length > 0) {{
        state.selectedCompanyCode = data.companies[0].cod_cia;
      }}

      buildSegmentPills();
      updateAllComboboxLabels();
      setupSearchAutocomplete();
      initBalancesSubramos();
      initRamosRankingsTab();
      renderAll();
    }}

    function initBalancesSubramos() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.subramos_catalog) return;
      const select = document.getElementById('balSubramoSelect');
      if (!select) return;
      select.innerHTML = data.subramos_catalog.map(s => `
        <option value="${{s.cod}}">${{s.cod}} - ${{s.desc}}</option>
      `).join('');
      if (data.subramos_catalog.length > 0) {{
        state.balSubramo = data.subramos_catalog[0].cod;
      }}
    }}

    function setSegmentFilter(seg) {{
      state.selectedSegment = seg;
      buildSegmentPills();
      updateAllComboboxLabels();
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
        btn.onclick = () => setSegmentFilter(seg);
        container.appendChild(btn);
      }});
    }}

    // ========================================================
    // UNIVERSAL SEARCHABLE COMBOBOX CONTROLLER
    // ========================================================
    const COMBOBOX_IDS = ['scatterCombobox', 'ciaCombobox', 'invCombobox', 'solvCombobox', 'gestCombobox', 'balCombobox'];

    function toggleCombobox(idPrefix) {{
      const dropdown = document.getElementById(`${{idPrefix}}Dropdown`);
      if (!dropdown) return;
      const isClosed = dropdown.classList.contains('hidden');
      
      // Close all other dropdowns
      COMBOBOX_IDS.forEach(id => {{
        const d = document.getElementById(`${{id}}Dropdown`);
        if (d) d.classList.add('hidden');
      }});

      if (isClosed) {{
        dropdown.classList.remove('hidden');
        const input = document.getElementById(`${{idPrefix}}Input`);
        if (input) {{
          input.value = '';
          setTimeout(() => input.focus(), 50);
        }}
        populateComboboxList(idPrefix, '');
      }}
    }}

    function closeAllComboboxes() {{
      COMBOBOX_IDS.forEach(id => {{
        const d = document.getElementById(`${{id}}Dropdown`);
        if (d) d.classList.add('hidden');
      }});
    }}

    function filterCombobox(idPrefix, query) {{
      populateComboboxList(idPrefix, query);
    }}

    function populateComboboxList(idPrefix, query) {{
      const listEl = document.getElementById(`${{idPrefix}}List`);
      if (!listEl) return;
      const data = window.DATA_SINENSUP;
      if (!data || !data.companies) return;

      const q = (query || '').toLowerCase().trim();
      
      // Match groups
      const matchedGroups = (data.groups || []).filter(g => {{
        if (!q) return true;
        return g.name.toLowerCase().includes(q) || g.short_name.toLowerCase().includes(q) || g.description.toLowerCase().includes(q);
      }});

      // Match companies
      let sourceList = data.companies;
      if (idPrefix === 'scatterCombobox' && state.selectedSegment !== 'Todos') {{
        sourceList = getFilteredCompanies();
      }}

      const filteredCias = sourceList.filter(c => {{
        if (!q) return true;
        return c.razon_social.toLowerCase().includes(q) || c.cod_cia.includes(q);
      }});

      if (matchedGroups.length === 0 && filteredCias.length === 0) {{
        listEl.innerHTML = '<div class="p-3 text-slate-500 text-center text-xs">No se encontraron coincidencias</div>';
        return;
      }}

      let html = '';

      if (matchedGroups.length > 0 && idPrefix !== 'scatterCombobox') {{
        html += `
          <div class="px-2 py-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 uppercase tracking-wider flex items-center justify-between">
            <span>🏛️ Grupos Aseguradores Consolidados (${{matchedGroups.length}})</span>
          </div>
        ` + matchedGroups.map(g => {{
          const isSelected = (state.balScope === 'group' && state.selectedGroupId === g.id);
          return `
            <div onclick="onComboboxSelect('${{idPrefix}}', 'group:${{g.id}}')" 
                 class="p-2 hover:bg-slate-800 cursor-pointer flex items-center justify-between gap-2 rounded transition-colors ${{isSelected ? 'bg-amber-500/20 font-bold text-amber-300 border-l-2 border-amber-400' : 'text-slate-200'}}">
              <div class="truncate flex items-center gap-1.5">
                <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">GRUPO</span>
                <span class="truncate font-semibold text-xs text-white">${{g.name}}</span>
                <span class="text-[10px] text-slate-400 font-mono">(${{g.entities_count}} cías)</span>
              </div>
              <div class="text-right text-[10px] font-mono text-amber-300 font-bold flex-shrink-0">
                ${{g.market_share.toFixed(1)}}% mkt
              </div>
            </div>
          `;
        }}).join('');
      }}

      if (filteredCias.length > 0) {{
        if (matchedGroups.length > 0 && idPrefix !== 'scatterCombobox') {{
          html += `
            <div class="px-2 py-1 text-[10px] font-bold text-slate-400 bg-slate-950 uppercase tracking-wider mt-1">
              <span>🏢 Aseguradoras Individuales (${{filteredCias.length}})</span>
            </div>
          `;
        }}
        html += filteredCias.map(c => {{
          const isSelected = (idPrefix === 'scatterCombobox' && state.highlightedCiaCode === c.cod_cia) ||
                             (idPrefix !== 'scatterCombobox' && state.selectedCompanyCode === c.cod_cia && state.balScope !== 'group');
          return `
            <div onclick="onComboboxSelect('${{idPrefix}}', '${{c.cod_cia}}')" 
                 class="p-2 hover:bg-slate-800 cursor-pointer flex items-center justify-between gap-2 rounded transition-colors ${{isSelected ? 'bg-slate-800/80 font-bold text-white' : 'text-slate-300'}}">
              <div class="truncate flex items-center gap-1.5">
                <span class="font-mono text-[10px] text-slate-400 font-bold">${{c.cod_cia}}</span>
                <span class="truncate font-semibold text-xs text-white">${{c.razon_social}}</span>
              </div>
              <div class="flex-shrink-0">
                ${{getTipoBadge(c.tipo_entidad)}}
              </div>
            </div>
          `;
        }}).join('');
      }}

      listEl.innerHTML = html;
    }}

    function onComboboxSelect(idPrefix, codeOrGid) {{
      closeAllComboboxes();
      if (idPrefix === 'scatterCombobox') {{
        highlightScatterCompany(codeOrGid);
      }} else if (codeOrGid.startsWith('group:')) {{
        const gid = codeOrGid.replace('group:', '');
        state.selectedGroupId = gid;
        if (state.currentTab === 'balances') {{
          setBalScope('group');
        }} else {{
          openGroupModal(gid);
        }}
      }} else {{
        if (state.balScope === 'group') {{
          state.balScope = 'cia';
        }}
        onCompanyDropdownChange(codeOrGid);
      }}
    }}

    function updateAllComboboxLabels() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.companies_by_code) return;

      const current = data.companies_by_code[state.selectedCompanyCode];
      const currentLabel = current ? `${{current.cod_cia}} - ${{current.razon_social}}` : 'Seleccionar aseguradora...';

      ['ciaComboboxLabel', 'invComboboxLabel', 'solvComboboxLabel', 'gestComboboxLabel'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.innerText = currentLabel;
      }});

      const balLabel = document.getElementById('balComboboxLabel');
      if (balLabel) {{
        if (state.balScope === 'group' && data.groups_by_id && data.groups_by_id[state.selectedGroupId]) {{
          balLabel.innerText = `🏛️ ${{data.groups_by_id[state.selectedGroupId].name}} (Consolidado)`;
        }} else {{
          balLabel.innerText = currentLabel;
        }}
      }}

      const scatterLabelEl = document.getElementById('scatterComboboxLabel');
      if (scatterLabelEl) {{
        if (state.highlightedCiaCode && data.companies_by_code[state.highlightedCiaCode]) {{
          const hl = data.companies_by_code[state.highlightedCiaCode];
          scatterLabelEl.innerText = `${{hl.cod_cia}} - ${{hl.razon_social}}`;
        }} else {{
          scatterLabelEl.innerText = '🔍 Resaltar aseguradora...';
        }}
      }}
    }}

    function highlightScatterCompany(code) {{
      state.highlightedCiaCode = code || null;
      updateAllComboboxLabels();
      
      const clearBtn = document.getElementById('clearHighlightBtn');
      if (clearBtn) {{
        if (code) clearBtn.classList.remove('hidden');
        else clearBtn.classList.add('hidden');
      }}

      if (state.currentTab === 'vision-mercado') {{
        renderScatterPlot();
      }}
    }}

    function setupSearchAutocomplete() {{
      const input = document.getElementById('globalCompanySearch');
      const dropdown = document.getElementById('searchResultsDropdown');
      const data = window.DATA_SINENSUP;
      if (!input || !dropdown || !data) return;

      input.addEventListener('input', (e) => {{
        const q = e.target.value.toLowerCase().trim();
        if (!q) {{
          dropdown.classList.add('hidden');
          return;
        }}

        const matches = data.companies.filter(c => 
          c.razon_social.toLowerCase().includes(q) || c.cod_cia.includes(q)
        ).slice(0, 10);

        if (matches.length === 0) {{
          dropdown.innerHTML = '<div class="p-3 text-slate-500 text-center">No se encontraron resultados</div>';
        }} else {{
          dropdown.innerHTML = matches.map(c => `
            <div onclick="selectCompany('${{c.cod_cia}}')" class="p-2.5 hover:bg-slate-800 cursor-pointer flex items-center justify-between border-b border-slate-800/60 last:border-0">
              <div>
                <span class="font-mono text-slate-400 font-bold mr-2">${{c.cod_cia}}</span>
                <span class="text-slate-200 font-semibold">${{c.razon_social}}</span>
              </div>
              <div>${{getTipoBadge(c.tipo_entidad)}}</div>
            </div>
          `).join('');
        }}
        dropdown.classList.remove('hidden');
      }});

      document.addEventListener('click', (e) => {{
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {{
          dropdown.classList.add('hidden');
        }}
        
        COMBOBOX_IDS.forEach(id => {{
          const container = document.getElementById(`${{id}}Container`);
          if (container && !container.contains(e.target)) {{
            const d = document.getElementById(`${{id}}Dropdown`);
            if (d) d.classList.add('hidden');
          }}
        }});
      }});
    }}

    function selectCompany(code) {{
      state.selectedCompanyCode = code;
      state.highlightedCiaCode = code;
      document.getElementById('globalCompanySearch').value = '';
      document.getElementById('searchResultsDropdown').classList.add('hidden');
      updateAllComboboxLabels();
      switchTab('ficha-compania');
    }}

    function onCompanyDropdownChange(code) {{
      state.selectedCompanyCode = code;
      state.highlightedCiaCode = code;
      updateAllComboboxLabels();

      // Auto switch scope to cia when selecting specific company
      if (state.currentTab === 'inversiones-finanzas') {{
        setInvScope('cia');
      }} else if (state.currentTab === 'solvencia-ratios') {{
        setSolvScope('cia');
      }} else if (state.currentTab === 'ratios-gestion') {{
        setGestScope('cia');
      }} else if (state.currentTab === 'balances') {{
        setBalScope('cia');
      }} else {{
        renderAll();
      }}
    }}

    function switchTab(tabId) {{
      state.currentTab = tabId;
      ['vision-mercado', 'ficha-compania', 'ramos-suscripcion', 'rankings-ramos', 'inversiones-finanzas', 'solvencia-ratios', 'ratios-gestion', 'balances'].forEach(id => {{
        const el = document.getElementById(`tab-${{id}}`);
        const btn = document.getElementById(`tabBtn-${{id}}`);
        if (!el || !btn) return;
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
      renderRamosRankingsTab();
      renderInvestmentsTab();
      renderSolvencyTab();
      renderManagementTab();
      renderBalancesTab();
    }}

    // ----------------------------------------------------
    // TAB 1 RENDER: MARKET OVERVIEW & GROUPS / COMPANIES RANKING
    function setRankingMode(mode) {{
      state.marketRankingMode = mode;
      const btnG = document.getElementById('rankingModeBtn-groups');
      const btnC = document.getElementById('rankingModeBtn-companies');
      const boxG = document.getElementById('groupsRankingContainer');
      const boxC = document.getElementById('companiesRankingContainer');

      if (mode === 'groups') {{
        if (btnG) btnG.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5';
        if (btnC) btnC.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5';
        if (boxG) boxG.classList.remove('hidden');
        if (boxC) boxC.classList.add('hidden');
      }} else {{
        if (btnG) btnG.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5';
        if (btnC) btnC.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5';
        if (boxG) boxG.classList.add('hidden');
        if (boxC) boxC.classList.remove('hidden');
      }}
      renderMarketOverview();
    }}

    function renderGroupsRankingTable() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.groups) return;

      const tbody = document.getElementById('groupsRankingTableBody');
      if (!tbody) return;

      tbody.innerHTML = data.groups.map((g, idx) => {{
        const isLS = g.id === 'la_segunda';
        const barWidth = Math.min(100, Math.max(4, g.market_share * 7));
        return `
          <tr class="hover:bg-slate-800/70 ${{isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/80 font-semibold' : ''}} cursor-pointer transition-colors" onclick="openGroupModal('${{g.id}}')">
            <td class="py-2.5 px-2 text-center text-slate-400 font-mono font-bold">${{idx + 1}}</td>
            <td class="py-2.5 px-2">
              <div class="font-bold text-white flex items-center gap-1.5">
                <span>${{g.name}}</span>
                ${{isLS ? '<span class="px-1.5 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
              </div>
              <div class="text-[10px] text-slate-400 truncate max-w-[230px]" title="${{g.description}}">${{g.description}}</div>
            </td>
            <td class="py-2.5 px-2 text-center">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 border border-slate-700 text-slate-300">${{g.entities_count}} Cías</span>
            </td>
            <td class="py-2.5 px-2 text-right font-bold font-mono text-white">${{formatARS(g.primas_emitidas)}}</td>
            <td class="py-2.5 px-2 text-right">
              <div class="font-bold font-mono text-amber-300">${{g.market_share.toFixed(2)}}%</div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1 overflow-hidden">
                <div class="bg-amber-400 h-full rounded-full" style="width: ${{barWidth}}%"></div>
              </div>
            </td>
            <td class="py-2.5 px-2 text-right text-slate-300 font-mono">${{formatARS(g.primas_devengadas)}}</td>
            <td class="py-2.5 px-2 text-right text-slate-300 font-mono">${{formatPercent(g.loss_ratio)}}</td>
            <td class="py-2.5 px-2 text-right font-mono font-bold ${{g.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(g.combined_ratio)}}</td>
            <td class="py-2.5 px-2 text-right font-mono ${{g.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(g.resultado_tecnico)}}</td>
            <td class="py-2.5 px-2 text-right font-mono ${{g.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(g.resultado_financiero)}}</td>
            <td class="py-2.5 px-2 text-right font-mono font-bold ${{g.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(g.resultado_neto)}}</td>
            <td class="py-2.5 px-2 text-right text-slate-300 font-mono">${{formatARS(g.activo)}}</td>
            <td class="py-2.5 px-2 text-right text-slate-300 font-mono">${{formatARS(g.patrimonio_neto)}}</td>
            <td class="py-2.5 px-2 text-center" onclick="event.stopPropagation()">
              <button onclick="openGroupModal('${{g.id}}')" class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-colors text-[10px] font-bold">
                Ver Cías
              </button>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function openGroupModal(gid) {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.groups_by_id) return;
      const g = data.groups_by_id[gid];
      if (!g) return;

      state.selectedGroupId = gid;

      document.getElementById('groupModalTitle').innerText = g.name;
      document.getElementById('groupModalSubtitle').innerText = `${{g.description}} • ${{g.entities_count}} entidades aseguradoras consolidadas`;

      document.getElementById('groupModalKpis').innerHTML = `
        <div class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <div class="text-[10px] font-semibold text-slate-400 uppercase">Primas Emitidas</div>
          <div class="text-base font-bold font-mono text-white mt-0.5">${{formatARS(g.primas_emitidas)}}</div>
          <div class="text-[10px] text-amber-400 font-bold">${{g.market_share.toFixed(2)}}% del Mercado Total</div>
        </div>
        <div class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <div class="text-[10px] font-semibold text-slate-400 uppercase">Ratio Combinado</div>
          <div class="text-base font-bold font-mono ${{g.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}} mt-0.5">${{formatPercent(g.combined_ratio)}}</div>
          <div class="text-[10px] text-slate-400">Siniestralidad: ${{formatPercent(g.loss_ratio)}}</div>
        </div>
        <div class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <div class="text-[10px] font-semibold text-slate-400 uppercase">Resultado Neto</div>
          <div class="text-base font-bold font-mono ${{g.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-0.5">${{formatARS(g.resultado_neto)}}</div>
          <div class="text-[10px] text-slate-400">Téc: ${{formatARS(g.resultado_tecnico)}}</div>
        </div>
        <div class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
          <div class="text-[10px] font-semibold text-slate-400 uppercase">Activo Consolidado</div>
          <div class="text-base font-bold font-mono text-brand-blue mt-0.5">${{formatARS(g.activo)}}</div>
          <div class="text-[10px] text-slate-400">PN: ${{formatARS(g.patrimonio_neto)}}</div>
        </div>
      `;

      document.getElementById('groupModalMembersList').innerHTML = g.members.map(m => `
        <div class="p-3.5 flex flex-wrap items-center justify-between gap-3 hover:bg-slate-900/60 transition-colors">
          <div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-xs font-bold text-slate-400">${{m.cod_cia}}</span>
              <span class="font-bold text-sm text-white">${{m.razon_social}}</span>
              ${{getTipoBadge(m.tipo_entidad)}}
            </div>
            <div class="text-xs text-slate-400 mt-1 flex flex-wrap items-center gap-3">
              <span>Primas: <b class="text-slate-200 font-mono">${{formatARS(m.primas_emitidas)}}</b> (${{m.share_of_group}}% del grupo)</span>
              <span>Siniestros: <b class="text-rose-300 font-mono">${{formatARS(m.siniestros)}}</b></span>
              <span>Comb. Ratio: <b class="${{m.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}} font-mono">${{formatPercent(m.combined_ratio)}}</b></span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="selectCompany('${{m.cod_cia}}'); closeGroupModal();" class="px-3 py-1 rounded-lg bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-xs font-bold">
              Ver Ficha Individual
            </button>
          </div>
        </div>
      `).join('');

      const balBtn = document.getElementById('groupModalBalanceBtn');
      if (balBtn) {{
        balBtn.onclick = () => {{
          closeGroupModal();
          state.selectedGroupId = gid;
          setBalScope('group');
          switchTab('balances');
        }};
      }}

      document.getElementById('groupDetailModal').classList.remove('hidden');
    }}

    function closeGroupModal() {{
      const m = document.getElementById('groupDetailModal');
      if (m) m.classList.add('hidden');
    }}

    function renderMarketOverview() {{
      const list = getFilteredCompanies();
      document.getElementById('filteredCiasCount').innerText = list.length;

      let totPrimasDev = 0, totPrimasEmit = 0, totActivo = 0, totSiniestros = 0, totGastos = 0, totNeto = 0;
      list.forEach(c => {{
        totPrimasDev += c.primas_devengadas || 0;
        totPrimasEmit += c.primas_emitidas || 0;
        totActivo += c.activo || 0;
        totSiniestros += (c.siniestros || 0) + (c.rescates || 0);
        totGastos += c.gtos_operativos || ((c.gtos_produccion || 0) + (c.gtos_explotacion || 0));
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

      // Render Groups ranking table
      renderGroupsRankingTable();

      // Top 15 Table SORTED BY PRIMAS EMITIDAS
      const sortedByEmitidas = [...list].sort((a, b) => b.primas_emitidas - a.primas_emitidas);
      const top15 = sortedByEmitidas.slice(0, 15);
      const top15Codes = new Set(top15.map(c => c.cod_cia));

      // La Segunda identifier
      const isLaSegunda = c => ['0117', '0317', '0436', '0618'].includes(c.cod_cia) || c.razon_social.toUpperCase().includes('SEGUNDA');

      const allDataCompanies = window.DATA_SINENSUP.companies;
      const allSorted = [...allDataCompanies].sort((a, b) => b.primas_emitidas - a.primas_emitidas);

      const extraLaSegundaInFilter = sortedByEmitidas.filter(c => isLaSegunda(c) && !top15Codes.has(c.cod_cia));
      const extraLaSegundaAll = allSorted.filter(c => isLaSegunda(c) && !top15Codes.has(c.cod_cia));
      const extraToShow = extraLaSegundaInFilter.length > 0 ? extraLaSegundaInFilter : (state.selectedSegment === 'Todos' ? extraLaSegundaAll : extraLaSegundaInFilter);

      let rowsHtml = top15.map((c, i) => {{
        const isLS = isLaSegunda(c);
        const isHL = state.highlightedCiaCode === c.cod_cia;
        return `
        <tr class="hover:bg-slate-800/60 ${{isHL ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : (isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/70' : '')}} cursor-pointer" onclick="highlightScatterCompany('${{c.cod_cia}}')">
          <td class="py-1.5 px-2 text-center text-slate-400 font-mono">${{i+1}}</td>
          <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[190px] whitespace-nowrap" title="${{c.razon_social}}">
            ${{c.razon_social}}
            ${{isLS ? '<span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
          </td>
          <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
          <td class="py-1.5 px-2 text-right font-bold text-white">${{formatARS(c.primas_emitidas)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.primas_devengadas)}}</td>
          <td class="py-1.5 px-2 text-right text-rose-300">${{formatARS(c.siniestros)}}</td>
          <td class="py-1.5 px-2 text-right">${{formatPercent(c.loss_ratio)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
          <td class="py-1.5 px-2 text-right ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_tecnico)}}</td>
          <td class="py-1.5 px-2 text-right ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_neto)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.activo)}}</td>
          <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
            <button onclick="selectCompany('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-[9px] font-bold">Ver</button>
          </td>
        </tr>
      `}}).join('');

      if (extraToShow.length > 0) {{
        rowsHtml += `
        <tr class="bg-slate-900/95 border-y-2 border-amber-500/40">
          <td colspan="13" class="py-1.5 px-2 text-[11px] font-bold text-amber-300">
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5"><i class="fa-solid fa-star text-amber-400 text-xs"></i> Grupo Asegurador La Segunda (Benchmark / Fuera de Top 15)</span>
              <span class="text-[9px] text-slate-400 font-normal">Fijadas permanentemente</span>
            </div>
          </td>
        </tr>
        ` + extraToShow.map(c => {{
          const overallRank = allSorted.findIndex(x => x.cod_cia === c.cod_cia) + 1;
          const isHL = state.highlightedCiaCode === c.cod_cia;
          return `
          <tr class="hover:bg-amber-500/15 ${{isHL ? 'bg-amber-500/25 border-l-4 border-l-amber-400 font-bold' : 'bg-amber-500/5 border-l-4 border-l-amber-400/80'}} cursor-pointer" onclick="highlightScatterCompany('${{c.cod_cia}}')">
            <td class="py-1.5 px-2 text-center text-amber-300 font-mono font-bold">#${{overallRank}}</td>
            <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[190px] whitespace-nowrap" title="${{c.razon_social}}">
              ${{c.razon_social}}
              <span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>
            </td>
            <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
            <td class="py-1.5 px-2 text-right font-bold text-white">${{formatARS(c.primas_emitidas)}}</td>
            <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.primas_devengadas)}}</td>
            <td class="py-1.5 px-2 text-right text-rose-300">${{formatARS(c.siniestros)}}</td>
            <td class="py-1.5 px-2 text-right">${{formatPercent(c.loss_ratio)}}</td>
            <td class="py-1.5 px-2 text-right font-bold ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
            <td class="py-1.5 px-2 text-right ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_tecnico)}}</td>
            <td class="py-1.5 px-2 text-right ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
            <td class="py-1.5 px-2 text-right font-bold ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_neto)}}</td>
            <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.activo)}}</td>
            <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
              <button onclick="selectCompany('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-[9px] font-bold">Ver</button>
            </td>
          </tr>
        `}}).join('');
      }}

      document.getElementById('topRankingTableBody').innerHTML = rowsHtml;

      renderMarketScatterPlot(list);
      renderMarketTable();
    }}

    function renderMarketScatterPlot(list) {{
      const valid = list.filter(c => c.primas_devengadas > 0);
      const hlCode = state.highlightedCiaCode;
      const hasHighlight = !!hlCode && valid.some(c => c.cod_cia === hlCode);

      const trace = {{
        x: valid.map(c => Math.max(-120, Math.min(150, c.margen_tecnico))),
        y: valid.map(c => Math.max(-40, Math.min(80, c.roi_inversiones))),
        text: valid.map(c => `<b>${{c.razon_social}}</b><br>Cód SSN: ${{c.cod_cia}} • Tipo: ${{c.tipo_entidad}}<br>Primas Emitidas: ${{formatARS(c.primas_emitidas)}}<br>Primas Devengadas: ${{formatARS(c.primas_devengadas)}}<br>Siniestros: ${{formatARS(c.siniestros)}}<br>M. Técnico: ${{c.margen_tecnico.toFixed(1)}}%<br>ROI Inv: ${{c.roi_inversiones.toFixed(1)}}%<br>Ratio Comb: ${{c.combined_ratio.toFixed(1)}}%`),
        customdata: valid.map(c => c.cod_cia),
        mode: 'markers',
        marker: {{
          size: valid.map(c => {{
            const baseSize = Math.max(9, Math.min(46, Math.sqrt(c.primas_emitidas / 8e7)));
            return (hasHighlight && c.cod_cia === hlCode) ? baseSize * 1.35 + 8 : baseSize;
          }}),
          color: valid.map(c => {{
            if (c.margen_tecnico >= 0 && c.roi_inversiones >= 0) return '#10B981';
            if (c.margen_tecnico < 0 && c.roi_inversiones >= 0) return '#F59E0B';
            if (c.margen_tecnico >= 0 && c.roi_inversiones < 0) return '#38BDF8';
            return '#E20039';
          }}),
          opacity: valid.map(c => {{
            if (!hasHighlight) return 0.88;
            return c.cod_cia === hlCode ? 1.0 : 0.22;
          }}),
          line: {{
            color: valid.map(c => {{
              if (hasHighlight && c.cod_cia === hlCode) return '#FBBF24';
              return '#FFFFFF';
            }}),
            width: valid.map(c => {{
              if (hasHighlight && c.cod_cia === hlCode) return 4.0;
              return hasHighlight ? 0.5 : 1.2;
            }})
          }}
        }},
        type: 'scatter',
        hoverinfo: 'text'
      }};

      const annotations = [
        {{ x: 75, y: 55, text: '<b>Cuadrante 1: Ganadoras Integrales</b><br>(Margen Técnico + / Rendimiento Financiero +)', showarrow: false, font: {{ color: '#10B981', size: 11 }} }},
        {{ x: -65, y: 55, text: '<b>Cuadrante 2: Dependencia Financiera</b><br>(Déficit Técnico / Rendimiento Financiero +)', showarrow: false, font: {{ color: '#F59E0B', size: 11 }} }},
        {{ x: 75, y: -25, text: '<b>Cuadrante 3: Técnicas Puras</b><br>(Margen Técnico + / Déficit Financiero -)', showarrow: false, font: {{ color: '#38BDF8', size: 11 }} }},
        {{ x: -65, y: -25, text: '<b>Cuadrante 4: En Riesgo Operativo</b><br>(Déficit Técnico y Financiero -)', showarrow: false, font: {{ color: '#E20039', size: 11 }} }}
      ];

      if (hasHighlight) {{
        const target = valid.find(c => c.cod_cia === hlCode);
        if (target) {{
          annotations.push({{
            x: Math.max(-120, Math.min(150, target.margen_tecnico)),
            y: Math.max(-40, Math.min(80, target.roi_inversiones)),
            text: `<b>📍 ${{target.razon_social}}</b><br>Primas Emit: ${{formatARS(target.primas_emitidas)}} | M. Téc: ${{target.margen_tecnico.toFixed(1)}}% | ROI: ${{target.roi_inversiones.toFixed(1)}}%`,
            showarrow: true,
            arrowhead: 2,
            arrowsize: 1.2,
            arrowwidth: 2.5,
            arrowcolor: '#FBBF24',
            ax: 0,
            ay: -55,
            bgcolor: 'rgba(15, 23, 42, 0.95)',
            bordercolor: '#FBBF24',
            borderwidth: 2,
            borderpad: 6,
            font: {{ color: '#FFFFFF', size: 11, family: 'Sora' }}
          }});
        }}
      }}

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 50, r: 30, t: 25, b: 55 }},
        xaxis: {{
          title: 'Margen Técnico (%) = Resultado Técnico / Primas Devengadas',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          zerolinecolor: '#475569',
          zerolinewidth: 2
        }},
        yaxis: {{
          title: 'Rendimiento Financiero (%) = Res. Financiero / Inversiones',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          zerolinecolor: '#475569',
          zerolinewidth: 2
        }},
        annotations: annotations
      }};

      const config = {{
        responsive: true,
        displayModeBar: false,
        scrollZoom: true
      }};

      Plotly.newPlot('marketScatterPlot', [trace], layout, config).then(() => {{
        const plotEl = document.getElementById('marketScatterPlot');
        plotEl.on('plotly_click', (data) => {{
          if (data && data.points && data.points.length > 0) {{
            const ciaCode = data.points[0].customdata;
            if (ciaCode) {{
              if (state.highlightedCiaCode === ciaCode) {{
                selectCompany(ciaCode);
              }} else {{
                highlightScatterCompany(ciaCode);
              }}
            }}
          }}
        }});
      }});
    }}

    let scatterDragMode = 'zoom';
    function toggleScatterPan() {{
      const plotEl = document.getElementById('marketScatterPlot');
      if (!plotEl) return;
      scatterDragMode = scatterDragMode === 'zoom' ? 'pan' : 'zoom';
      Plotly.relayout(plotEl, {{ dragmode: scatterDragMode }});
      const btn = document.getElementById('panToggleBtn');
      if (btn) {{
        if (scatterDragMode === 'pan') {{
          btn.className = 'px-2 py-1 bg-amber-500 text-slate-950 font-bold border border-amber-400 rounded-lg text-xs transition-colors shadow-md shadow-amber-500/20';
          btn.title = 'Modo Pan Activo (clic para volver a selección zoom)';
        }} else {{
          btn.className = 'px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-200 transition-colors';
          btn.title = 'Desplazar / Pan (arrastrar el gráfico)';
        }}
      }}
    }}

    function downloadScatterPlotPNG() {{
      const plotEl = document.getElementById('marketScatterPlot');
      if (plotEl) {{
        Plotly.downloadImage(plotEl, {{
          format: 'png',
          width: 1400,
          height: 800,
          filename: 'matriz_estrategica_mercado_asegurador_ssn'
        }});
      }}
    }}

    function zoomScatterPlot(factor) {{
      const plotEl = document.getElementById('marketScatterPlot');
      if (!plotEl || !plotEl.layout) return;
      const xRange = plotEl.layout.xaxis.range;
      const yRange = plotEl.layout.yaxis.range;
      if (!xRange || !yRange) return;
      const xMid = (xRange[0] + xRange[1]) / 2;
      const yMid = (yRange[0] + yRange[1]) / 2;
      const xSpan = (xRange[1] - xRange[0]) * factor / 2;
      const ySpan = (yRange[1] - yRange[0]) * factor / 2;
      Plotly.relayout(plotEl, {{
        'xaxis.range': [xMid - xSpan, xMid + xSpan],
        'yaxis.range': [yMid - ySpan, yMid + ySpan]
      }});
    }}

    function resetScatterPlotZoom() {{
      const plotEl = document.getElementById('marketScatterPlot');
      if (plotEl) {{
        Plotly.relayout(plotEl, {{
          'xaxis.autorange': true,
          'yaxis.autorange': true
        }});
      }}
    }}

    function renderMarketTable() {{
      const list = getFilteredCompanies();
      const q = (document.getElementById('marketTableFilter')?.value || '').toLowerCase().trim();
      const filtered = q ? list.filter(c => c.razon_social.toLowerCase().includes(q) || c.cod_cia.includes(q)) : list;
      
      const sorted = [...filtered].sort((a, b) => b.primas_emitidas - a.primas_emitidas);
      const tbody = document.getElementById('marketFullTableBody');
      tbody.innerHTML = sorted.map(c => {{
        const isHL = state.highlightedCiaCode === c.cod_cia;
        return `
        <tr class="hover:bg-slate-800/60 ${{isHL ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : ''}} cursor-pointer" onclick="highlightScatterCompany('${{c.cod_cia}}')">
          <td class="py-1.5 px-2 font-medium text-white truncate max-w-[190px] whitespace-nowrap" title="${{c.razon_social}}">${{c.razon_social}}</td>
          <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
          <td class="py-1.5 px-2 text-right font-bold text-white">${{formatARS(c.primas_emitidas)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300 font-bold">${{formatARS(c.primas_devengadas)}}</td>
          <td class="py-1.5 px-2 text-right text-rose-300 font-bold">${{formatARS(c.siniestros)}}</td>
          <td class="py-1.5 px-2 text-right">${{formatPercent(c.loss_ratio)}}</td>
          <td class="py-1.5 px-2 text-right ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
          <td class="py-1.5 px-2 text-right ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_tecnico)}}</td>
          <td class="py-1.5 px-2 text-right ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.resultado_neto >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_neto)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.activo)}}</td>
          <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
            <button onclick="selectCompany('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-[9px] font-semibold">Ver</button>
          </td>
        </tr>
      `}}).join('');
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

      document.getElementById('ciaKpiPrimasEmit').innerText = formatARS(c.primas_emitidas);
      document.getElementById('ciaKpiVarReservas').innerText = formatARS(c.var_reservas);
      document.getElementById('ciaKpiPrimasDev').innerText = formatARS(c.primas_devengadas);

      document.getElementById('ciaKpiCombined').innerText = formatPercent(c.combined_ratio);
      document.getElementById('ciaKpiCombined').className = `text-base font-bold font-mono mt-1 ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}`;
      
      document.getElementById('ciaKpiResTec').innerText = formatARS(c.resultado_tecnico);
      document.getElementById('ciaKpiResTec').className = `text-base font-bold font-mono mt-1 ${{c.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;

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
        totals: {{ marker: {{ color: '#38BDF8' }} }},
        hovertemplate: '<b>%{{x}}</b><br>Importe: <b>%{{text}}</b><extra></extra>'
      }};

      const maxWf = Math.max(...wf.map(s => Math.abs(s.amount)), 10);
      const tickVals = [];
      const tickTexts = [];
      for (let i = -3; i <= 3; i++) {{
        const v = (maxWf / 3) * i;
        tickVals.push(v);
        tickTexts.push(formatARS(v));
      }}

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 80, r: 30, t: 30, b: 80 }},
        xaxis: {{ color: '#94A3B8', tickangle: -25, tickfont: {{ size: 10 }} }},
        yaxis: {{
          title: 'Importe (ARS)',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          tickmode: 'array',
          tickvals: tickVals,
          ticktext: tickTexts
        }}
      }};

      Plotly.newPlot('ciaWaterfallPlot', [trace], layout, {{ responsive: true, displayModeBar: false }});
    }}

    function renderCompanyDonuts(c) {{
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
      const maxPrimas = Math.max(...topSub.map(s => s.primas), 10);
      const maxSin = Math.max(...topSub.map(s => s['siniestralidad_%'] || 0), 10);

      const tickCount = 5;
      const tickVals = [];
      const tickTexts = [];
      for (let i = 0; i <= tickCount; i++) {{
        const v = (maxPrimas / tickCount) * i;
        tickVals.push(v);
        tickTexts.push(formatARS(v));
      }}

      const tracePrimas = {{
        x: topSub.map(s => s.desc_subramo),
        y: topSub.map(s => s.primas),
        name: 'Primas Emitidas (ARS)',
        type: 'bar',
        marker: {{ color: '#38BDF8', opacity: 0.85, line: {{ color: '#0284C7', width: 1 }} }},
        customdata: topSub.map(s => ({{
          sub: s.desc_subramo,
          cod: s.cod_subramo || '-',
          primas_txt: formatARS(s.primas),
          sin_txt: formatARS(s.siniestros),
          loss_txt: (s['siniestralidad_%'] || 0).toFixed(1) + '%'
        }})),
        hovertemplate: '<b>%{{customdata.sub}}</b> (Cód: %{{customdata.cod}})<br>Primas Emitidas: <b>%{{customdata.primas_txt}}</b><br>Siniestros: <b>%{{customdata.sin_txt}}</b><br>Siniestralidad s/ Emisión: <b>%{{customdata.loss_txt}}</b><extra></extra>'
      }};

      const traceLoss = {{
        x: topSub.map(s => s.desc_subramo),
        y: topSub.map(s => s['siniestralidad_%'] || 0),
        name: 'Siniestralidad s/ Emisión (%)',
        type: 'scatter',
        mode: 'lines+markers+text',
        text: topSub.map(s => (s['siniestralidad_%'] || 0).toFixed(1) + '%'),
        textposition: 'top center',
        textfont: {{ color: '#FDA4AF', size: 11, family: 'JetBrains Mono', weight: 'bold' }},
        yaxis: 'y2',
        marker: {{ color: '#E20039', size: 9, line: {{ color: '#FFFFFF', width: 2 }} }},
        line: {{ color: '#E20039', width: 3 }},
        hovertemplate: '<b>%{{x}}</b><br>Siniestralidad s/ Emisión: <b>%{{y:.1f}}%</b><extra></extra>'
      }};

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 85, r: 65, t: 25, b: 120 }},
        xaxis: {{ tickangle: -30, color: '#94A3B8', tickfont: {{ size: 10 }} }},
        yaxis: {{
          title: 'Primas Emitidas (ARS)',
          color: '#94A3B8',
          gridcolor: '#1E293B',
          tickmode: 'array',
          tickvals: tickVals,
          ticktext: tickTexts,
          showgrid: true
        }},
        yaxis2: {{
          title: 'Siniestralidad s/ Emisión (%)',
          overlaying: 'y',
          side: 'right',
          color: '#E20039',
          ticksuffix: '%',
          showgrid: false,
          zeroline: true,
          zerolinecolor: '#334155',
          range: [0, Math.max(105, maxSin * 1.35)]
        }},
        legend: {{ orientation: 'h', y: 1.15, x: 0.5, xanchor: 'center', font: {{ color: '#E2E8F0', size: 11 }} }}
      }};

      Plotly.newPlot('subramosBarChart', [tracePrimas, traceLoss], layout, {{ responsive: true, displayModeBar: false }});

      // Subramos table
      const tbody = document.getElementById('subramosTableBody');
      tbody.innerHTML = topSub.map(s => `
        <tr class="hover:bg-slate-800/60">
          <td class="py-2 px-3 text-slate-400">${{s.cod_subramo || '-'}}</td>
          <td class="py-2 px-3 text-white font-medium">${{s.desc_subramo}}</td>
          <td class="py-2 px-3 text-right text-slate-200 font-bold">${{formatARS(s.primas)}}</td>
          <td class="py-2 px-3 text-right text-slate-300 font-bold">${{formatARS(s.siniestros)}}</td>
          <td class="py-2 px-3 text-right font-bold ${{s['siniestralidad_%'] > 60 ? 'text-rose-400' : 'text-emerald-400'}}">${{formatPercent(s['siniestralidad_%'])}}</td>
        </tr>
      `).join('');
    }}

    // ========================================================
    // TAB 4: RANKINGS DE PRODUCCIÓN POR RAMOS Y SUBRAMOS
    // ========================================================
    function initRamosRankingsTab() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.ramos_taxonomy) return;

      const tax = data.ramos_taxonomy;
      const allSecKeys = Object.keys(tax);

      // Ensure active sections is valid array
      if (!Array.isArray(state.ramosRankSections) || state.ramosRankSections.length === 0) {{
        state.ramosRankSections = ['personas'];
      }}

      // 1. Render Section Multi-Select Buttons
      const secContainer = document.getElementById('rrSectionButtons');
      if (secContainer) {{
        const isAllSec = allSecKeys.every(k => state.ramosRankSections.includes(k));
        let secHtml = `
          <button onclick="toggleRamosSection('all')" 
                  class="px-2 py-0.5 rounded-lg text-xs font-semibold transition-all ${{
                    isAllSec ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }}">
            🌟 Todas
          </button>
        `;

        secHtml += allSecKeys.map(secKey => {{
          const sec = tax[secKey];
          const isSelected = state.ramosRankSections.includes(secKey);
          return `
            <button onclick="toggleRamosSection('${{secKey}}')" 
                    class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${{
                      isSelected ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }}">
              <i class="fa-solid ${{sec.icon || 'fa-folder'}}"></i>
              <span>${{sec.name}}</span>
              <span class="text-[10px] opacity-70">${{isSelected ? '✓' : '+'}}</span>
            </button>
          `;
        }}).join('');
        secContainer.innerHTML = secHtml;
      }}

      // 2. Gather available groups for active sections
      let availableGroups = [];
      state.ramosRankSections.forEach(secKey => {{
        const sec = tax[secKey];
        if (sec && sec.ramos) {{
          Object.values(sec.ramos).forEach(g => {{
            if (!availableGroups.some(ag => ag.id === g.id)) {{
              availableGroups.push(g);
            }}
          }});
        }}
      }});

      // Ensure active groups is valid array
      if (!Array.isArray(state.ramosRankGroups) || state.ramosRankGroups.length === 0) {{
        state.ramosRankGroups = availableGroups.length > 0 ? [availableGroups[0].id] : [];
      }} else {{
        // Filter out groups no longer in active sections
        const validGroupIds = availableGroups.map(g => g.id);
        const filtered = state.ramosRankGroups.filter(gid => validGroupIds.includes(gid));
        state.ramosRankGroups = filtered.length > 0 ? filtered : (availableGroups.length > 0 ? [availableGroups[0].id] : []);
      }}

      // Render Group Multi-Select Buttons
      const grpContainer = document.getElementById('rrGroupButtons');
      if (grpContainer) {{
        const isAllGrp = availableGroups.length > 0 && availableGroups.every(g => state.ramosRankGroups.includes(g.id));
        let grpHtml = `
          <button onclick="toggleRamosGroup('all')" 
                  class="px-2 py-0.5 rounded-lg text-xs font-semibold transition-all ${{
                    isAllGrp ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }}">
            🌟 Todos (${{availableGroups.length}})
          </button>
        `;

        grpHtml += availableGroups.map(g => {{
          const isSelected = state.ramosRankGroups.includes(g.id);
          return `
            <button onclick="toggleRamosGroup('${{g.id}}')" 
                    class="px-2 py-0.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${{
                      isSelected ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }}">
              <span>${{g.name}}</span>
              <span class="text-[10px] opacity-70">${{isSelected ? '✓' : '+'}}</span>
            </button>
          `;
        }}).join('');
        grpContainer.innerHTML = grpHtml;
      }}

      // 3. Populate Subramo Select dropdown
      const subSelect = document.getElementById('rrSubramoSelect');
      if (subSelect) {{
        const catalog = {{}};
        (data.subramos_catalog || []).forEach(s => {{ catalog[s.cod] = s.desc; }});

        // Gather all subramos under currently selected groups
        let activeSubramos = [];
        availableGroups.filter(g => state.ramosRankGroups.includes(g.id)).forEach(g => {{
          (g.subramos || []).forEach(scod => {{
            if (!activeSubramos.includes(scod)) activeSubramos.push(scod);
          }});
        }});
        activeSubramos.sort();

        let opts = `<option value="all">🌟 CONSOLIDADO: TODOS LOS SUBRAMOS SELECCIONADOS (${{activeSubramos.length}})</option>`;
        activeSubramos.forEach(scod => {{
          const sdesc = catalog[scod] || scod;
          opts += `<option value="${{scod}}">${{scod}} - ${{sdesc}}</option>`;
        }});
        subSelect.innerHTML = opts;
        subSelect.value = state.ramosRankSubramo || 'all';
      }}
    }}

    function toggleRamosSection(sectionId) {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.ramos_taxonomy) return;
      const allSecKeys = Object.keys(data.ramos_taxonomy);

      if (sectionId === 'all') {{
        const isAll = allSecKeys.every(k => state.ramosRankSections.includes(k));
        state.ramosRankSections = isAll ? ['patrimoniales'] : [...allSecKeys];
      }} else {{
        if (state.ramosRankSections.includes(sectionId)) {{
          if (state.ramosRankSections.length > 1) {{
            state.ramosRankSections = state.ramosRankSections.filter(k => k !== sectionId);
          }}
        }} else {{
          state.ramosRankSections.push(sectionId);
        }}
      }}
      state.ramosRankSubramo = 'all';
      initRamosRankingsTab();
      renderRamosRankingsTab();
    }}

    function toggleRamosGroup(groupId) {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.ramos_taxonomy) return;

      // Gather available groups in active sections
      let availableGroupIds = [];
      state.ramosRankSections.forEach(secKey => {{
        const sec = data.ramos_taxonomy[secKey];
        if (sec && sec.ramos) {{
          Object.keys(sec.ramos).forEach(gid => {{
            if (!availableGroupIds.includes(gid)) availableGroupIds.push(gid);
          }});
        }}
      }});

      if (groupId === 'all') {{
        const isAll = availableGroupIds.every(gid => state.ramosRankGroups.includes(gid));
        state.ramosRankGroups = isAll ? (availableGroupIds.length > 0 ? [availableGroupIds[0]] : []) : [...availableGroupIds];
      }} else {{
        if (state.ramosRankGroups.includes(groupId)) {{
          if (state.ramosRankGroups.length > 1) {{
            state.ramosRankGroups = state.ramosRankGroups.filter(g => g !== groupId);
          }}
        }} else {{
          state.ramosRankGroups.push(groupId);
        }}
      }}
      state.ramosRankSubramo = 'all';
      initRamosRankingsTab();
      renderRamosRankingsTab();
    }}

    function setRamosSubramo(subramoCode) {{
      state.ramosRankSubramo = subramoCode;
      renderRamosRankingsTab();
    }}

    function setRamosRankMode(mode) {{
      state.ramosRankMode = mode;
      const btnG = document.getElementById('rrModeBtn-groups');
      const btnC = document.getElementById('rrModeBtn-companies');

      if (mode === 'groups') {{
        if (btnG) btnG.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5';
        if (btnC) btnC.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5';
      }} else {{
        if (btnG) btnG.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5';
        if (btnC) btnC.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5';
      }}
      renderRamosRankingsTab();
    }}

    function filterRamosRankingTable(query) {{
      state.ramosRankSearchQuery = query || '';
      renderRamosRankingTableOnly();
    }}

    function getTargetRamosSubramos() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.ramos_taxonomy) return [];
      const tax = data.ramos_taxonomy;

      if (state.ramosRankSubramo && state.ramosRankSubramo !== 'all') {{
        return [state.ramosRankSubramo];
      }}

      let allSubs = [];
      state.ramosRankSections.forEach(secKey => {{
        const sec = tax[secKey];
        if (sec && sec.ramos) {{
          Object.entries(sec.ramos).forEach(([gid, g]) => {{
            if (state.ramosRankGroups.includes(gid)) {{
              (g.subramos || []).forEach(scod => {{
                if (!allSubs.includes(scod)) allSubs.push(scod);
              }});
            }}
          }});
        }}
      }});
      return allSubs;
    }}

    function computeRamosRankingData() {{
      const data = window.DATA_SINENSUP;
      if (!data) return {{ total_emitidas: 0, total_siniestros: 0, loss_ratio: 0, resultado_tecnico: 0, entities_count: 0, ranking: [] }};

      const targetSubs = getTargetRamosSubramos();
      const ciasSub = data.cias_balances_subramos || {{}};
      const groupsSub = data.groups_balances_subramos || {{}};
      const ciasByCode = data.companies_by_code || {{}};
      const groupsById = data.groups_by_id || {{}};

      const ranking = [];

      if (state.ramosRankMode === 'companies') {{
        Object.entries(ciasSub).forEach(([cod_cia, sub_map]) => {{
          let totEmit = 0.0, totSin = 0.0, totIngTec = 0.0, totEgrTec = 0.0;
          targetSubs.forEach(s => {{
            if (sub_map[s]) {{
              const d = sub_map[s];
              totEmit += (d['5.01.01.00.00.00.00.00'] || 0.0);
              totSin += (d['4.01.01.00.00.00.00.00'] || 0.0) + (d['4.01.02.00.00.00.00.00'] || 0.0);
              totIngTec += (d['5.01.00.00.00.00.00.00'] || 0.0);
              totEgrTec += (d['4.01.00.00.00.00.00.00'] || 0.0);
            }}
          }});
          if (totEmit > 0) {{
            const c = ciasByCode[cod_cia] || {{}};
            const lossRatio = totEmit > 0 ? (totSin / totEmit * 100.0) : 0.0;
            const resTec = totIngTec - totEgrTec;
            ranking.push({{
              id: cod_cia,
              code: cod_cia,
              name: c.razon_social || cod_cia,
              tipo: c.tipo_entidad || '',
              emitidas: totEmit,
              siniestros: totSin,
              loss_ratio: lossRatio,
              resultado_tecnico: resTec
            }});
          }}
        }});
      }} else {{
        Object.entries(groupsSub).forEach(([gid, sub_map]) => {{
          let totEmit = 0.0, totSin = 0.0, totIngTec = 0.0, totEgrTec = 0.0;
          targetSubs.forEach(s => {{
            if (sub_map[s]) {{
              const d = sub_map[s];
              totEmit += (d['5.01.01.00.00.00.00.00'] || 0.0);
              totSin += (d['4.01.01.00.00.00.00.00'] || 0.0) + (d['4.01.02.00.00.00.00.00'] || 0.0);
              totIngTec += (d['5.01.00.00.00.00.00.00'] || 0.0);
              totEgrTec += (d['4.01.00.00.00.00.00.00'] || 0.0);
            }}
          }});
          if (totEmit > 0) {{
            const g = groupsById[gid] || {{}};
            const lossRatio = totEmit > 0 ? (totSin / totEmit * 100.0) : 0.0;
            const resTec = totIngTec - totEgrTec;
            ranking.push({{
              id: gid,
              code: gid,
              name: g.name || gid,
              tipo: `${{g.entities_count || 0}} Cías`,
              emitidas: totEmit,
              siniestros: totSin,
              loss_ratio: lossRatio,
              resultado_tecnico: resTec
            }});
          }}
        }});
      }}

      const totBranch = ranking.reduce((acc, r) => acc + r.emitidas, 0.0);
      const totSinBranch = ranking.reduce((acc, r) => acc + r.siniestros, 0.0);
      const lossBranch = totBranch > 0 ? (totSinBranch / totBranch * 100.0) : 0.0;
      const resTecBranch = ranking.reduce((acc, r) => acc + r.resultado_tecnico, 0.0);

      ranking.forEach(r => {{
        r.market_share = totBranch > 0 ? (r.emitidas / totBranch * 100.0) : 0.0;
      }});

      ranking.sort((a, b) => b.emitidas - a.emitidas);
      return {{
        total_emitidas: totBranch,
        total_siniestros: totSinBranch,
        loss_ratio: lossBranch,
        resultado_tecnico: resTecBranch,
        entities_count: ranking.length,
        ranking: ranking
      }};
    }}

    let currentRamosRankData = null;

    function renderRamosRankingsTab() {{
      initRamosRankingsTab();
      const data = window.DATA_SINENSUP;
      if (!data) return;

      const tax = data.ramos_taxonomy || {{}};
      const titleEl = document.getElementById('rrSelectedTitle');
      const badgeEl = document.getElementById('rrSelectedBadge');
      const subTitleEl = document.getElementById('rrSelectedSubtitle');

      if (titleEl) {{
        if (state.ramosRankSubramo && state.ramosRankSubramo !== 'all') {{
          const catalog = {{}};
          (data.subramos_catalog || []).forEach(s => {{ catalog[s.cod] = s.desc; }});
          titleEl.innerText = `${{state.ramosRankSubramo}} - ${{catalog[state.ramosRankSubramo] || 'Subramo'}}`;
          if (badgeEl) badgeEl.innerText = 'Subramo Específico SSN';
        }} else {{
          const secNames = state.ramosRankSections.map(k => tax[k] ? tax[k].name : k).join(' + ');
          const grpCount = state.ramosRankGroups.length;
          titleEl.innerText = `${{secNames}} (${{grpCount}} Ramos)`;
          if (badgeEl) badgeEl.innerText = `Ramos Consolidados (${{grpCount}})`;
        }}
      }}

      const res = computeRamosRankingData();
      currentRamosRankData = res;

      // Render KPIs
      const banner = document.getElementById('rrKpiBanner');
      if (banner) {{
        const totalMarketEmit = (data.macro_entidades && data.macro_entidades.total_mercado_emitidas) ? data.macro_entidades.total_mercado_emitidas : 29.9e12;
        const shareOfMarket = (res.total_emitidas / totalMarketEmit * 100.0);

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">PRIMAS EMITIDAS SELECCIÓN</div>
            <div class="text-lg font-bold font-mono text-white mt-1">${{formatARS(res.total_emitidas)}}</div>
            <div class="text-[10px] text-amber-400 font-bold mt-1">${{shareOfMarket.toFixed(1)}}% del Mercado Total</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">SINIESTROS / BENEFICIOS</div>
            <div class="text-lg font-bold font-mono text-rose-400 mt-1">${{formatARS(res.total_siniestros)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Siniestros + Rescates/Rentas</div>
          </div>
          <div class="glass-card p-4 rounded-xl ${{res.loss_ratio <= 65 ? 'border-l-emerald-500' : 'border-l-rose-500'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">SINIESTRALIDAD MEDIA</div>
            <div class="text-lg font-bold font-mono ${{res.loss_ratio <= 65 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatPercent(res.loss_ratio)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{res.loss_ratio <= 65 ? 'Siniestralidad Controlada' : 'Alta Siniestralidad'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl ${{res.resultado_tecnico >= 0 ? 'border-l-emerald-500' : 'border-l-rose-500'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO TÉCNICO TOTAL</div>
            <div class="text-lg font-bold font-mono ${{res.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatARS(res.resultado_tecnico)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{res.resultado_tecnico >= 0 ? 'Superávit Técnico' : 'Déficit Técnico'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-sky-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">ENTIDADES OPERATIVAS</div>
            <div class="text-lg font-bold font-mono text-sky-400 mt-1">${{res.entities_count}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{state.ramosRankMode === 'groups' ? 'Grupos Aseguradores' : 'Aseguradoras Directas'}}</div>
          </div>
        `;
      }}

      // Render Plot
      renderRamosMarketSharePlot(res.ranking);

      // Render Table
      renderRamosRankingTableOnly();
    }}

    function renderRamosMarketSharePlot(ranking) {{
      const plotEl = document.getElementById('rrMarketSharePlot');
      if (!plotEl) return;

      const top10 = ranking.slice(0, 10);
      if (top10.length === 0) {{
        plotEl.innerHTML = '<div class="h-full flex items-center justify-center text-slate-500 text-xs">No hay datos para graficar en esta selección</div>';
        return;
      }}

      const othersEmit = ranking.slice(10).reduce((acc, r) => acc + r.emitidas, 0.0);
      const labels = top10.map(r => r.name);
      const values = top10.map(r => r.emitidas);
      if (othersEmit > 0) {{
        labels.push('Resto del Mercado');
        values.push(othersEmit);
      }}

      const data = [{{
        type: 'pie',
        labels: labels,
        values: values,
        textinfo: 'label+percent',
        hoverinfo: 'label+value+percent',
        hole: 0.45,
        marker: {{
          colors: ['#F59E0B', '#3B82F6', '#10B981', '#EC4899', '#8B5CF6', '#06B6D4', '#E11D48', '#84CC16', '#F97316', '#6366F1', '#475569']
        }}
      }}];

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {{ color: '#94A3B8', size: 11 }},
        margin: {{ t: 10, b: 10, l: 10, r: 10 }},
        showlegend: true,
        legend: {{ orientation: 'h', x: 0, y: -0.1, font: {{ size: 10, color: '#cbd5e1' }} }}
      }};

      Plotly.newPlot('rrMarketSharePlot', data, layout, {{ responsive: true, displayModeBar: false }});
    }}

    function renderRamosRankingTableOnly() {{
      const tbody = document.getElementById('rrTableBody');
      if (!tbody || !currentRamosRankData) return;

      const q = (state.ramosRankSearchQuery || '').toLowerCase().trim();
      const filtered = currentRamosRankData.ranking.filter(r => {{
        if (!q) return true;
        return r.name.toLowerCase().includes(q) || r.code.toLowerCase().includes(q);
      }});

      if (filtered.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="9" class="text-center py-6 text-slate-500">No se encontraron entidades en este ramo</td></tr>';
        return;
      }}

      tbody.innerHTML = filtered.map((r, i) => {{
        const isLS = (r.code === '0317' || r.code === '0618' || r.code === '0117' || r.code === '0436' || r.code === 'la_segunda');
        const isSelected = (state.ramosRankMode === 'companies' && state.selectedCompanyCode === r.code) ||
                           (state.ramosRankMode === 'groups' && state.selectedGroupId === r.code);
        
        // Entity name cell: clean group name vs company [code] name
        let entityNameHtml = '';
        if (state.ramosRankMode === 'groups') {{
          entityNameHtml = `
            <div class="font-bold text-amber-300 flex items-center gap-1.5">
              <span class="truncate max-w-[280px]" title="${{r.name}}">${{r.name}}</span>
              ${{isLS ? '<span class="px-1.5 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
            </div>
          `;
        }} else {{
          entityNameHtml = `
            <div class="font-bold text-white flex items-center gap-1.5">
              <span class="font-mono text-xs text-slate-400 font-normal mr-1">[${{r.code}}]</span>
              <span class="truncate max-w-[240px]" title="${{r.name}}">${{r.name}}</span>
              ${{isLS ? '<span class="px-1.5 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
            </div>
          `;
        }}

        return `
          <tr class="hover:bg-slate-800/60 ${{isSelected ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : (isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/70 font-semibold' : '')}} cursor-pointer transition-colors">
            <td class="py-2 px-2 text-center text-slate-400 font-mono font-bold">${{i + 1}}</td>
            <td class="py-2 px-2">
              ${{entityNameHtml}}
            </td>
            <td class="py-2 px-2 text-center">
              ${{state.ramosRankMode === 'groups' ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">${{r.tipo}}</span>` : getTipoBadge(r.tipo)}}
            </td>
            <td class="py-2 px-2 text-right font-bold text-white font-mono">${{formatARS(r.emitidas)}}</td>
            <td class="py-2 px-2 text-right">
              <div class="font-bold font-mono text-amber-300">${{r.market_share.toFixed(2)}}%</div>
              <div class="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
                <div class="bg-amber-400 h-full rounded-full" style="width: ${{Math.min(100, r.market_share * 5)}}%"></div>
              </div>
            </td>
            <td class="py-2 px-2 text-right text-rose-300 font-mono">${{formatARS(r.siniestros)}}</td>
            <td class="py-2 px-2 text-right font-mono ${{r.loss_ratio <= 65 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(r.loss_ratio)}}</td>
            <td class="py-2 px-2 text-right font-mono font-bold ${{r.resultado_tecnico >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(r.resultado_tecnico)}}</td>
            <td class="py-2 px-2 text-center" onclick="event.stopPropagation()">
              ${{state.ramosRankMode === 'groups' ? `
                <button onclick="openGroupModal('${{r.code}}')" class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-colors text-[9px] font-bold">Ver Grupo</button>
              ` : `
                <button onclick="selectCompany('${{r.code}}')" class="px-2 py-0.5 rounded bg-brand-red/20 text-brand-red hover:bg-brand-red hover:text-white transition-colors text-[9px] font-bold">Ver Ficha</button>
              `}}
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function exportRamosRankCSV() {{
      if (!currentRamosRankData || !currentRamosRankData.ranking) return;

      const headers = ['rank', 'codigo', 'nombre', 'tipo', 'primas_emitidas', 'market_share', 'siniestros_beneficios', 'loss_ratio', 'resultado_tecnico'];
      let csv = headers.join(',') + '\\n';

      currentRamosRankData.ranking.forEach((r, idx) => {{
        const row = [
          idx + 1,
          `"${{r.code}}"`,
          `"${{r.name.replace(/"/g, '""')}}"`,
          `"${{r.tipo}}"`,
          r.emitidas || 0,
          (r.market_share || 0).toFixed(2),
          r.siniestros || 0,
          (r.loss_ratio || 0).toFixed(2),
          r.resultado_tecnico || 0
        ];
        csv += row.join(',') + '\\n';
      }});

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ranking_ramos_${{state.ramosRankSections.join('_')}}_${{state.ramosRankMode}}.csv`;
      a.click();
    }}

    // ----------------------------------------------------
    // TAB 5 RENDER: INVERSIONES Y FINANZAS
    // ----------------------------------------------------
    function setInvScope(scope) {{
      state.invScope = scope;
      
      const scopes = ['cia', 'market', 'Patrimoniales y Mixtas', 'Riesgos del Trabajo (ART)', 'Seguros de Personas', 'Seguros de Retiro'];
      scopes.forEach(sc => {{
        const btn = document.getElementById(`invScopeBtn-${{sc}}`);
        if (btn) {{
          if (state.invScope === sc) {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 font-bold transition-all shadow-md shadow-amber-500/20';
          }} else {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
          }}
        }}
      }});

      renderInvestmentsTab();
    }}

    function setInvTopMetric(metric) {{
      state.invTopMetric = metric;
      const metrics = ['activo', 'patrimonio_neto', 'resultado_financiero', 'inversiones'];
      metrics.forEach(m => {{
        const btn = document.getElementById(`invTopMetricBtn-${{m}}`);
        if (btn) {{
          if (state.invTopMetric === m) {{
            btn.className = 'px-3 py-1 rounded bg-amber-500 text-slate-950 font-bold';
          }} else {{
            btn.className = 'px-3 py-1 rounded text-slate-400 hover:text-white font-semibold';
          }}
        }}
      }});
      renderInvTopRankings();
    }}

    function renderInvestmentsTab() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      let title = '', badge = '', count = 1;
      let totInv = 0, resFin = 0, totActivo = 0, invs = [];

      if (state.invScope === 'cia') {{
        const c = data.companies_by_code[state.selectedCompanyCode];
        if (!c) return;
        title = c.razon_social;
        badge = c.tipo_entidad;
        count = 1;
        totInv = c.inversiones || 0;
        resFin = c.resultado_financiero || 0;
        totActivo = c.activo || 0;
        invs = c.investments || [];
      }} else if (state.invScope === 'market') {{
        title = 'Mercado Asegurador Consolidado';
        badge = 'Total Mercado';
        count = data.total_entidades || 185;
        data.companies.forEach(c => {{
          totInv += c.inversiones || 0;
          resFin += c.resultado_financiero || 0;
          totActivo += c.activo || 0;
        }});
        invs = data.market_investments || [];
      }} else {{
        const seg = state.invScope;
        title = `Segmento: ${{seg}}`;
        badge = seg;
        const segCias = data.companies.filter(c => c.tipo_entidad === seg);
        count = segCias.length;
        segCias.forEach(c => {{
          totInv += c.inversiones || 0;
          resFin += c.resultado_financiero || 0;
          totActivo += c.activo || 0;
        }});
        invs = (data.segment_investments && data.segment_investments[seg]) ? data.segment_investments[seg] : [];
      }}

      const roi = totInv > 0 ? (resFin / totInv * 100.0) : 0.0;
      const share = totActivo > 0 ? (totInv / totActivo * 100.0) : 0.0;

      // Update Tab 4 Header
      document.getElementById('invSelectedTitle').innerText = title;
      document.getElementById('invSelectedBadge').innerText = badge;
      document.getElementById('invEntitiesCount').innerText = count;

      // Update KPI Cards
      document.getElementById('invTotalVal').innerText = formatARS(totInv);
      document.getElementById('invResFinVal').innerText = formatARS(resFin);
      document.getElementById('invResFinVal').className = `text-base font-bold font-mono mt-1 ${{resFin >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;
      
      document.getElementById('invRoiVal').innerText = formatPercent(roi);
      document.getElementById('invRoiVal').className = `text-base font-bold font-mono mt-1 ${{roi >= 0 ? 'text-brand-blue' : 'text-rose-400'}}`;
      
      document.getElementById('invAssetShareVal').innerText = formatPercent(share);

      // Update Table
      const listBody = document.getElementById('investmentsListBody');
      if (!invs || invs.length === 0) {{
        listBody.innerHTML = '<tr><td colspan="3" class="p-3 text-slate-400 text-center">Sin desglose informado para esta selección</td></tr>';
      }} else {{
        listBody.innerHTML = invs.map(item => `
          <tr class="hover:bg-slate-800/50">
            <td class="py-1.5 px-2 text-slate-200 font-medium">${{item.desc_cuenta}}</td>
            <td class="py-1.5 px-2 text-right text-white font-bold">${{formatARS(item.importe)}}</td>
            <td class="py-1.5 px-2 text-right text-amber-300 font-bold">${{item.porcentaje}}%</td>
          </tr>
        `).join('');
      }}

      // Update Donut Chart
      document.getElementById('invDonutSubtitle').innerText = `${{title}} (${{formatARS(totInv)}})`;
      
      if (!invs || invs.length === 0) {{
        Plotly.newPlot('investmentsPieChart', [], {{
          paper_bgcolor: 'transparent',
          annotations: [{{ text: 'Sin datos de inversiones', showarrow: false, font: {{ color: '#94A3B8', size: 14 }} }}]
        }}, {{ responsive: true, displayModeBar: false }});
      }} else {{
        const colors = ['#38BDF8', '#10B981', '#F59E0B', '#C084FC', '#FB923C', '#F43F5E', '#A855F7', '#64748B', '#06B6D4'];
        Plotly.newPlot('investmentsPieChart', [{{
          labels: invs.map(i => i.desc_cuenta),
          values: invs.map(i => i.importe),
          hole: 0.45,
          type: 'pie',
          textinfo: 'label+percent',
          textposition: 'inside',
          marker: {{ colors: colors }},
          customdata: invs.map(i => formatARS(i.importe)),
          hovertemplate: '<b>%{{label}}</b><br>Importe: <b>%{{customdata}}</b><br>Participación: <b>%{{percent}}</b><extra></extra>'
        }}], {{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          margin: {{ l: 15, r: 15, t: 15, b: 15 }},
          showlegend: false,
          font: {{ color: '#E2E8F0', size: 11, family: 'Sora' }}
        }}, {{ responsive: true, displayModeBar: false }});
      }}

      renderInvTopRankings();
    }}

    function renderInvTopRankings() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.companies) return;

      const metric = state.invTopMetric || 'activo';
      const sorted = [...data.companies].sort((a, b) => (b[metric] || 0) - (a[metric] || 0));
      const top20 = sorted.slice(0, 20);
      const top20Codes = new Set(top20.map(c => c.cod_cia));

      const isLaSegunda = c => ['0117', '0317', '0436', '0618'].includes(c.cod_cia) || c.razon_social.toUpperCase().includes('SEGUNDA');
      const extraLaSegunda = sorted.filter(c => isLaSegunda(c) && !top20Codes.has(c.cod_cia));

      let rowsHtml = top20.map((c, i) => {{
        const isLS = isLaSegunda(c);
        const isHL = state.selectedCompanyCode === c.cod_cia;
        return `
        <tr class="hover:bg-slate-800/60 ${{isHL ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : (isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/70' : '')}} cursor-pointer" onclick="onCompanyDropdownChange('${{c.cod_cia}}')">
          <td class="py-1.5 px-2 text-center text-slate-400 font-mono">${{i+1}}</td>
          <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[190px] whitespace-nowrap" title="${{c.razon_social}}">
            ${{c.razon_social}}
            ${{isLS ? '<span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
          </td>
          <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
          <td class="py-1.5 px-2 text-right font-bold text-amber-300">${{formatARS(c.inversiones)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-200 font-bold">${{formatARS(c.activo)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.patrimonio_neto)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.roi_inversiones >= 0 ? 'text-brand-blue' : 'text-rose-400'}}">${{formatPercent(c.roi_inversiones)}}</td>
          <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
            <button onclick="onCompanyDropdownChange('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-colors text-[9px] font-bold">Ver</button>
          </td>
        </tr>
      `}}).join('');

      if (extraLaSegunda.length > 0) {{
        rowsHtml += `
        <tr class="bg-slate-900/95 border-y-2 border-amber-500/40">
          <td colspan="9" class="py-1.5 px-2 text-[11px] font-bold text-amber-300">
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5"><i class="fa-solid fa-star text-amber-400 text-xs"></i> Grupo Asegurador La Segunda (Benchmark / Fuera de Top 20)</span>
              <span class="text-[9px] text-slate-400 font-normal">Fijadas permanentemente</span>
            </div>
          </td>
        </tr>
        ` + extraLaSegunda.map(c => {{
          const rank = sorted.findIndex(x => x.cod_cia === c.cod_cia) + 1;
          const isHL = state.selectedCompanyCode === c.cod_cia;
          return `
          <tr class="hover:bg-amber-500/15 ${{isHL ? 'bg-amber-500/25 border-l-4 border-l-amber-400 font-bold' : 'bg-amber-500/5 border-l-4 border-l-amber-400/80'}} cursor-pointer" onclick="onCompanyDropdownChange('${{c.cod_cia}}')">
            <td class="py-1.5 px-2 text-center text-amber-300 font-mono font-bold">#${{rank}}</td>
            <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[190px] whitespace-nowrap" title="${{c.razon_social}}">
              ${{c.razon_social}}
              <span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>
            </td>
            <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
            <td class="py-1.5 px-2 text-right font-bold text-amber-300">${{formatARS(c.inversiones)}}</td>
            <td class="py-1.5 px-2 text-right text-slate-200 font-bold">${{formatARS(c.activo)}}</td>
            <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(c.patrimonio_neto)}}</td>
            <td class="py-1.5 px-2 text-right font-bold ${{c.resultado_financiero >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatARS(c.resultado_financiero)}}</td>
            <td class="py-1.5 px-2 text-right font-bold ${{c.roi_inversiones >= 0 ? 'text-brand-blue' : 'text-rose-400'}}">${{formatPercent(c.roi_inversiones)}}</td>
            <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
              <button onclick="onCompanyDropdownChange('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-colors text-[9px] font-bold">Ver</button>
            </td>
          </tr>
        `}}).join('');
      }}

      document.getElementById('invTopRankingTableBody').innerHTML = rowsHtml;
    }}

    // ----------------------------------------------------
    // TAB 5 RENDER: SOLVENCIA Y RATIOS SSN
    // ----------------------------------------------------
    function setSolvScope(scope) {{
      state.solvScope = scope;
      const scopes = ['cia', 'Todos', 'Patrimoniales y Mixtas', 'Riesgos del Trabajo (ART)', 'Seguros de Personas', 'Seguros de Retiro'];
      scopes.forEach(sc => {{
        const btn = document.getElementById(`solvScopeBtn-${{sc}}`);
        if (btn) {{
          if (state.solvScope === sc) {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 font-bold transition-all shadow-md shadow-emerald-500/20';
          }} else {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
          }}
        }}
      }});
      renderSolvencyTab();
    }}

    function setSolvSortMetric(metric) {{
      state.solvSortMetric = metric;
      const metrics = ['cobertura_reservas', 'combined_ratio', 'patrimonio_neto', 'apalancamiento'];
      metrics.forEach(m => {{
        const btn = document.getElementById(`solvSortBtn-${{m}}`);
        if (btn) {{
          if (state.solvSortMetric === m) {{
            btn.className = 'px-3 py-1 rounded bg-emerald-500 text-slate-950 font-bold';
          }} else {{
            btn.className = 'px-3 py-1 rounded text-slate-400 hover:text-white font-semibold';
          }}
        }}
      }});
      renderSolvencyTab();
    }}

    function renderSolvencyTab() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      let title = '', badge = '', subtitle = '', count = 1;
      let cob = 0, apal = 0, cobranza = 0, pn = 0;

      if (state.solvScope === 'cia') {{
        const c = data.companies_by_code[state.selectedCompanyCode];
        if (!c) return;
        title = c.razon_social;
        badge = c.tipo_entidad;
        subtitle = `Indicadores Individuales de Solvencia, Cobertura y Ratios SSN (Cód: ${{c.cod_cia}})`;
        count = 1;

        cob = c.cobertura_reservas || 0;
        apal = c.apalancamiento || 0;
        cobranza = c.calidad_cartera || 0;
        pn = c.patrimonio_neto || 0;

        document.getElementById('solvCoberturaSub').innerText = 'Exigencia s/ Compromisos Técnicos';
        document.getElementById('solvApalancamientoSub').innerText = 'Exposición s/ Capital Propio';
        document.getElementById('solvCobranzaSub').innerText = 'Índice de Cartera a Cobrar';
        document.getElementById('solvPnSub').innerText = 'Solvencia Patrimonial Individual';
      }} else if (state.solvScope === 'Todos') {{
        title = 'Mercado Asegurador Consolidado';
        badge = 'Total Mercado';
        subtitle = 'Indicadores Agregados de Solvencia y Cobertura Regulatoria del Mercado (185 Entidades)';
        count = data.total_entidades || 185;

        let totDisp = 0, totInv = 0, totInm = 0, totCompTec = 0, totPrimas = 0, totPremios = 0, totPN = 0;
        data.companies.forEach(c => {{
          totDisp += c.disponibilidades || 0;
          totInv += c.inversiones || 0;
          totInm += c.inmuebles || 0;
          totCompTec += c.compromisos_tecnicos || 0;
          totPrimas += (c.primas_devengadas > 0 ? c.primas_devengadas : (c.primas_emitidas || 0));
          totPremios += (c.premios_a_cobrar || 0);
          totPN += c.patrimonio_neto || 0;
        }});

        cob = totCompTec > 0 ? ((totInv + totInm + totDisp) / totCompTec) : 1.0;
        apal = totPN > 0 ? (totPrimas / totPN) : 0;
        cobranza = totPrimas > 0 ? ((totPremios / totPrimas) * 100.0) : 0;
        pn = totPN;

        document.getElementById('solvCoberturaSub').innerText = `Activos Elegibles: ${{formatARS(totInv + totInm + totDisp)}} / Comp. Téc: ${{formatARS(totCompTec)}}`;
        document.getElementById('solvApalancamientoSub').innerText = 'Primas / Patrimonio Neto Consolidado';
        document.getElementById('solvCobranzaSub').innerText = `Premios a Cobrar: ${{formatARS(totPremios)}} / Primas`;
        document.getElementById('solvPnSub').innerText = 'Patrimonio Neto Consolidado Mercado';
      }} else {{
        const seg = state.solvScope;
        title = `Segmento: ${{seg}}`;
        badge = seg;
        subtitle = `Indicadores Agregados de Solvencia y Ratios Consolidados de ${{seg}}`;
        
        const segCias = data.companies.filter(c => c.tipo_entidad === seg);
        count = segCias.length;

        let totDisp = 0, totInv = 0, totInm = 0, totCompTec = 0, totPrimas = 0, totPremios = 0, totPN = 0;
        segCias.forEach(c => {{
          totDisp += c.disponibilidades || 0;
          totInv += c.inversiones || 0;
          totInm += c.inmuebles || 0;
          totCompTec += c.compromisos_tecnicos || 0;
          totPrimas += (c.primas_devengadas > 0 ? c.primas_devengadas : (c.primas_emitidas || 0));
          totPremios += (c.premios_a_cobrar || 0);
          totPN += c.patrimonio_neto || 0;
        }});

        cob = totCompTec > 0 ? ((totInv + totInm + totDisp) / totCompTec) : 1.0;
        apal = totPN > 0 ? (totPrimas / totPN) : 0;
        cobranza = totPrimas > 0 ? ((totPremios / totPrimas) * 100.0) : 0;
        pn = totPN;

        document.getElementById('solvCoberturaSub').innerText = `Activos Elegibles: ${{formatARS(totInv + totInm + totDisp)}} / Comp. Téc: ${{formatARS(totCompTec)}}`;
        document.getElementById('solvApalancamientoSub').innerText = 'Primas / Patrimonio Neto del Segmento';
        document.getElementById('solvCobranzaSub').innerText = `Premios a Cobrar: ${{formatARS(totPremios)}} / Primas`;
        document.getElementById('solvPnSub').innerText = `Patrimonio Neto Total (${{count}} Aseguradoras)`;
      }}

      // Update Header
      document.getElementById('solvSelectedTitle').innerText = title;
      document.getElementById('solvSelectedBadge').innerText = badge;
      document.getElementById('solvEntitiesCount').innerText = count;
      const subEl = document.getElementById('solvSelectedSubtitle');
      if (subEl) subEl.innerText = subtitle;

      // Update KPI Cards
      document.getElementById('solvCoberturaVal').innerText = cob.toFixed(2) + 'x';
      document.getElementById('solvCoberturaStatus').innerText = cob >= 1.0 ? '● Superávit Regulatorio' : '● Déficit de Cobertura';
      document.getElementById('solvCoberturaStatus').className = `text-[10px] font-semibold mt-1 ${{cob >= 1.0 ? 'text-emerald-400' : 'text-rose-400'}}`;

      document.getElementById('solvApalancamientoVal').innerText = apal.toFixed(2) + 'x';
      document.getElementById('solvCobranzaVal').innerText = formatPercent(cobranza);
      document.getElementById('solvPnVal').innerText = formatARS(pn);

      // Solvency Table List
      let list = data.companies;
      if (state.solvScope !== 'Todos' && state.solvScope !== 'cia') {{
        list = data.companies.filter(x => x.tipo_entidad === state.solvScope);
      }}

      const metric = state.solvSortMetric || 'cobertura_reservas';
      let sortedSolv = [...list];
      if (metric === 'combined_ratio' || metric === 'apalancamiento') {{
        sortedSolv.sort((a, b) => (a[metric] || 0) - (b[metric] || 0));
      }} else {{
        sortedSolv.sort((a, b) => (b[metric] || 0) - (a[metric] || 0));
      }}

      const isLaSegunda = c => ['0117', '0317', '0436', '0618'].includes(c.cod_cia) || c.razon_social.toUpperCase().includes('SEGUNDA');

      let rowsHtml = sortedSolv.map((item, i) => {{
        const isLS = isLaSegunda(item);
        const isHL = (state.selectedCompanyCode === item.cod_cia);
        return `
        <tr class="hover:bg-slate-800/60 ${{isHL ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : (isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/70' : '')}} cursor-pointer" onclick="onCompanyDropdownChange('${{item.cod_cia}}')">
          <td class="py-1.5 px-2 text-center text-slate-400 font-mono">${{i+1}}</td>
          <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[190px] whitespace-nowrap" title="${{item.razon_social}}">
            ${{item.razon_social}}
            ${{isLS ? '<span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
          </td>
          <td class="py-1.5 px-2 text-center">${{getTipoBadge(item.tipo_entidad)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{item.cobertura_reservas >= 1.0 ? 'text-emerald-400' : 'text-rose-400'}}">${{item.cobertura_reservas.toFixed(2)}}x</td>
          <td class="py-1.5 px-2 text-right font-bold ${{item.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(item.combined_ratio)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{item.apalancamiento.toFixed(2)}}x</td>
          <td class="py-1.5 px-2 text-right text-amber-300">${{formatPercent(item.calidad_cartera)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-200 font-bold">${{formatARS(item.patrimonio_neto)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatARS(item.activo)}}</td>
          <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
            <button onclick="onCompanyDropdownChange('${{item.cod_cia}}')" class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500 hover:text-slate-950 transition-colors text-[9px] font-bold">Ver</button>
          </td>
        </tr>
      `}}).join('');

      const tbody = document.getElementById('solvencyRankingTableBody');
      tbody.innerHTML = rowsHtml;
    }}

    // ----------------------------------------------------
    // TAB 6 RENDER: RATIOS DE GESTIÓN & SCORECARD (NUEVO)
    // ----------------------------------------------------
    function setGestScope(scope) {{
      state.gestScope = scope;
      const scopes = ['cia', 'Todos', 'Patrimoniales y Mixtas', 'Riesgos del Trabajo (ART)', 'Seguros de Personas', 'Seguros de Retiro'];
      scopes.forEach(sc => {{
        const btn = document.getElementById(`gestScopeBtn-${{sc}}`);
        if (btn) {{
          if (state.gestScope === sc) {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-500 text-white font-bold transition-all shadow-md shadow-indigo-500/20';
          }} else {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
          }}
        }}
      }});
      renderManagementTab();
    }}

    function setGestFilterMode(mode) {{
      state.gestFilterMode = mode;
      const modes = ['all', 'loss_high', 'cob_low', 'integral_win', 'slow_collect'];
      modes.forEach(m => {{
        const btn = document.getElementById(`gestFiltBtn-${{m}}`);
        if (btn) {{
          if (state.gestFilterMode === m) {{
            btn.className = 'px-2.5 py-1 rounded bg-indigo-500 text-white font-bold';
          }} else {{
            btn.className = 'px-2.5 py-1 rounded text-slate-400 hover:text-white font-semibold';
          }}
        }}
      }});
      renderManagementTable();
    }}

    function renderManagementTab() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      let title = '', badge = '', subtitle = '', count = 1;
      let targetMetrics = null, benchmarkMetrics = null;

      const currentCompany = data.companies_by_code[state.selectedCompanyCode];
      const marketBench = data.market_benchmarks;
      const segBench = (currentCompany && data.segment_benchmarks) ? data.segment_benchmarks[currentCompany.tipo_entidad] : marketBench;

      if (state.gestScope === 'cia') {{
        if (!currentCompany) return;
        title = currentCompany.razon_social;
        badge = currentCompany.tipo_entidad;
        subtitle = `Scorecard Individual de Gestión (Cód: ${{currentCompany.cod_cia}}) • Comparado contra Promedio de ${{currentCompany.tipo_entidad}}`;
        count = 1;
        targetMetrics = currentCompany;
        benchmarkMetrics = segBench || marketBench;
      }} else if (state.gestScope === 'Todos') {{
        title = 'Mercado Asegurador Argentino Consolidado';
        badge = 'Total Mercado';
        subtitle = 'Scorecard Agregado de las 185 Aseguradoras • Promedios y Ratios Ponderados del Mercado';
        count = data.total_entidades || 185;
        targetMetrics = marketBench;
        benchmarkMetrics = marketBench;
      }} else {{
        const seg = state.gestScope;
        title = `Segmento Consolidado: ${{seg}}`;
        badge = seg;
        const segObj = data.segment_benchmarks ? data.segment_benchmarks[seg] : null;
        count = segObj ? segObj.entidades : 0;
        subtitle = `Scorecard Agregado del Segmento ${{seg}} (${{count}} Aseguradoras) • Comparado contra Mercado Total`;
        targetMetrics = segObj || marketBench;
        benchmarkMetrics = marketBench;
      }}

      // Header update
      document.getElementById('gestSelectedTitle').innerText = title;
      document.getElementById('gestSelectedBadge').innerText = badge;
      document.getElementById('gestEntitiesCount').innerText = count;
      document.getElementById('gestSelectedSubtitle').innerText = subtitle;

      // Populate Scorecard Cards
      const populateCard = (prefix, val, metric, benchVal, suffix = '%', isMulti = false) => {{
        const valEl = document.getElementById(`${{prefix}}Val`);
        const badgeEl = document.getElementById(`${{prefix}}Badge`);
        const benchEl = document.getElementById(`${{prefix}}Bench`);

        if (valEl) {{
          valEl.innerText = isMulti ? `${{val.toFixed(2)}}x` : formatPercent(val);
        }}
        if (badgeEl) {{
          badgeEl.innerHTML = getTrafficLightBadge(val, metric);
        }}
        if (benchEl && benchVal !== undefined && benchVal !== null) {{
          const diff = val - benchVal;
          const sign = diff >= 0 ? '+' : '';
          const benchLabel = state.gestScope === 'cia' ? `vs. Prom. ${{currentCompany.tipo_entidad}}` : 'vs. Mercado Total';
          benchEl.innerText = isMulti ? `${{sign}}${{diff.toFixed(2)}}x ${{benchLabel}} (${{benchVal.toFixed(2)}}x)` : `${{sign}}${{diff.toFixed(1)}}% ${{benchLabel}} (${{benchVal.toFixed(1)}}%)`;
        }}
      }};

      populateCard('gKpiCombined', targetMetrics.combined_ratio, 'combined_ratio', benchmarkMetrics.combined_ratio);
      populateCard('gKpiLoss', targetMetrics.loss_ratio, 'loss_ratio', benchmarkMetrics.loss_ratio);
      populateCard('gKpiComm', targetMetrics.comm_ratio, 'comm_ratio', benchmarkMetrics.comm_ratio);
      populateCard('gKpiExp', targetMetrics.exp_ratio, 'exp_ratio', benchmarkMetrics.exp_ratio);
      populateCard('gKpiRet', targetMetrics.retencion_ratio, 'retencion_ratio', benchmarkMetrics.retencion_ratio);

      populateCard('gKpiRoi', targetMetrics.roi_inversiones, 'roi_inversiones', benchmarkMetrics.roi_inversiones);
      populateCard('gKpiDens', targetMetrics.densidad_inversiones, 'densidad_inversiones', benchmarkMetrics.densidad_inversiones);

      populateCard('gKpiCob', targetMetrics.cobertura_reservas, 'cobertura_reservas', benchmarkMetrics.cobertura_reservas, 'x', true);
      populateCard('gKpiApal', targetMetrics.apalancamiento, 'apalancamiento', benchmarkMetrics.apalancamiento, 'x', true);
      populateCard('gKpiCobranza', targetMetrics.calidad_cartera, 'calidad_cartera', benchmarkMetrics.calidad_cartera);

      populateCard('gKpiRoe', targetMetrics.roe, 'roe', benchmarkMetrics.roe);
      populateCard('gKpiRoa', targetMetrics.roa, 'roa', benchmarkMetrics.roa);
      populateCard('gKpiMargenTec', targetMetrics.margen_tecnico, 'margen_neto', benchmarkMetrics.margen_tecnico);
      populateCard('gKpiMargenNeto', targetMetrics.margen_neto, 'margen_neto', benchmarkMetrics.margen_neto);

      renderManagementRadar(targetMetrics, benchmarkMetrics, title);
      renderManagementDiagnosis(targetMetrics, benchmarkMetrics, title);
      renderManagementTable();
    }}

    function renderManagementRadar(target, bench, title) {{
      const radarCategories = [
        'Control de<br>Siniestros',
        'Eficiencia<br>Administrativa',
        'Disciplina<br>Comercial',
        'Rendimiento de<br>Inversiones',
        'Solvencia<br>Regulatoria',
        'Cobranza de<br>Premios'
      ];

      // Normalize 0-100 score (higher is always better, 100 = outer edge, 0 = center)
      const normScore = m => {{
        return [
          Math.round(Math.max(0, Math.min(100, 100 - (m.loss_ratio || 0) * 0.9))),
          Math.round(Math.max(0, Math.min(100, 100 - (m.exp_ratio || 0) * 2.2))),
          Math.round(Math.max(0, Math.min(100, 100 - (m.comm_ratio || 0) * 2.0))),
          Math.round(Math.max(0, Math.min(100, 50 + (m.roi_inversiones || 0) * 2.5))),
          Math.round(Math.max(0, Math.min(100, Math.min(100, (m.cobertura_reservas || 1.0) * 45)))),
          Math.round(Math.max(0, Math.min(100, 100 - (m.calidad_cartera || 0) * 1.5)))
        ];
      }};

      const targetVals = normScore(target);
      const benchVals = normScore(bench);

      const targetLabel = state.gestScope === 'cia' ? (target.razon_social || title) : title;
      const benchLabel = state.gestScope === 'cia' ? `Promedio ${{target.tipo_entidad || 'Segmento'}}` : 'Promedio Mercado Total';

      const plainCategories = [
        'Control de Siniestros',
        'Eficiencia Administrativa',
        'Disciplina Comercial',
        'Rendimiento de Inversiones',
        'Solvencia Regulatoria SSN',
        'Cobranza de Premios'
      ];

      const targetRealValues = [
        `${{(target.loss_ratio || 0).toFixed(1)}}% (Loss Ratio)`,
        `${{(target.exp_ratio || 0).toFixed(1)}}% (Gastos Admin)`,
        `${{(target.comm_ratio || 0).toFixed(1)}}% (Comisiones)`,
        `${{(target.roi_inversiones || 0).toFixed(1)}}% (ROI Inv.)`,
        `${{(target.cobertura_reservas || 1.0).toFixed(2)}}x (Cobertura SSN)`,
        `${{(target.calidad_cartera || 0).toFixed(1)}}% (Premios a Cobrar)`
      ];

      const benchRealValues = [
        `${{(bench.loss_ratio || 0).toFixed(1)}}% (Loss Ratio)`,
        `${{(bench.exp_ratio || 0).toFixed(1)}}% (Gastos Admin)`,
        `${{(bench.comm_ratio || 0).toFixed(1)}}% (Comisiones)`,
        `${{(bench.roi_inversiones || 0).toFixed(1)}}% (ROI Inv.)`,
        `${{(bench.cobertura_reservas || 1.0).toFixed(2)}}x (Cobertura SSN)`,
        `${{(bench.calidad_cartera || 0).toFixed(1)}}% (Premios a Cobrar)`
      ];

      const targetCustom = plainCategories.map((cat, idx) => ({{
        cat: cat,
        score: targetVals[idx],
        real: targetRealValues[idx],
        entity: targetLabel
      }}));

      const benchCustom = plainCategories.map((cat, idx) => ({{
        cat: cat,
        score: benchVals[idx],
        real: benchRealValues[idx],
        entity: benchLabel
      }}));

      const data = [
        {{
          type: 'scatterpolar',
          r: [...benchVals, benchVals[0]],
          theta: [...radarCategories, radarCategories[0]],
          customdata: [...benchCustom, benchCustom[0]],
          fill: 'toself',
          fillcolor: 'rgba(56, 189, 248, 0.15)',
          name: benchLabel,
          line: {{ color: '#38BDF8', width: 2, dash: 'dot' }},
          marker: {{ size: 6, color: '#38BDF8' }},
          hovertemplate: '<b>%{{customdata.entity}}</b><br>🎯 Eje: <b>%{{customdata.cat}}</b><br>📊 Puntaje: <b>%{{customdata.score}} / 100</b><br>📋 Valor Real: <b>%{{customdata.real}}</b><extra></extra>',
          hoverlabel: {{ bgcolor: '#0F172A', bordercolor: '#38BDF8', font: {{ family: 'Sora', size: 12, color: '#FFFFFF' }} }}
        }},
        {{
          type: 'scatterpolar',
          r: [...targetVals, targetVals[0]],
          theta: [...radarCategories, radarCategories[0]],
          customdata: [...targetCustom, targetCustom[0]],
          fill: 'toself',
          fillcolor: 'rgba(226, 0, 57, 0.25)',
          name: targetLabel,
          line: {{ color: '#E20039', width: 3 }},
          marker: {{ size: 7, color: '#E20039' }},
          hovertemplate: '<b>%{{customdata.entity}}</b><br>🎯 Eje: <b>%{{customdata.cat}}</b><br>📊 Puntaje: <b>%{{customdata.score}} / 100</b><br>📋 Valor Real: <b>%{{customdata.real}}</b><extra></extra>',
          hoverlabel: {{ bgcolor: '#0F172A', bordercolor: '#E20039', font: {{ family: 'Sora', size: 12, color: '#FFFFFF' }} }}
        }}
      ];

      const layout = {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: {{ l: 95, r: 95, t: 40, b: 50 }},
        polar: {{
          domain: {{ x: [0.12, 0.88], y: [0.08, 0.92] }},
          bgcolor: 'rgba(15, 23, 42, 0.5)',
          radialaxis: {{
            visible: true,
            range: [0, 100],
            color: '#94A3B8',
            gridcolor: '#334155',
            showticklabels: true,
            tickfont: {{ size: 9, color: '#94A3B8', family: 'JetBrains Mono' }}
          }},
          angularaxis: {{
            color: '#F8FAFC',
            gridcolor: '#334155',
            tickfont: {{ size: 12, family: 'Sora', color: '#FFFFFF', weight: 'bold' }},
            rotation: 90,
            direction: 'clockwise'
          }}
        }},
        legend: {{
          orientation: 'h',
          y: -0.18,
          x: 0.5,
          xanchor: 'center',
          font: {{ color: '#F1F5F9', size: 12, family: 'Sora' }}
        }}
      }};

      Plotly.newPlot('managementRadarChart', data, layout, {{ responsive: true, displayModeBar: false }});

      // Populate Axes Breakdown Cards
      const breakdownEl = document.getElementById('radarAxesBreakdown');
      if (breakdownEl) {{
        const axesList = [
          {{ name: '1. Siniestros', val: `${{(target.loss_ratio || 0).toFixed(1)}}%`, benchVal: `${{(bench.loss_ratio || 0).toFixed(1)}}%`, score: targetVals[0], benchScore: benchVals[0], desc: 'Loss Ratio' }},
          {{ name: '2. Admin (Estructura)', val: `${{(target.exp_ratio || 0).toFixed(1)}}%`, benchVal: `${{(bench.exp_ratio || 0).toFixed(1)}}%`, score: targetVals[1], benchScore: benchVals[1], desc: 'Gtos Explotación' }},
          {{ name: '3. Comercial (Comis.)', val: `${{(target.comm_ratio || 0).toFixed(1)}}%`, benchVal: `${{(bench.comm_ratio || 0).toFixed(1)}}%`, score: targetVals[2], benchScore: benchVals[2], desc: 'Gtos Producción' }},
          {{ name: '4. Rend. Inversiones', val: `${{(target.roi_inversiones || 0).toFixed(1)}}%`, benchVal: `${{(bench.roi_inversiones || 0).toFixed(1)}}%`, score: targetVals[3], benchScore: benchVals[3], desc: 'ROI Inversiones' }},
          {{ name: '5. Solvencia SSN', val: `${{(target.cobertura_reservas || 1.0).toFixed(2)}}x`, benchVal: `${{(bench.cobertura_reservas || 1.0).toFixed(2)}}x`, score: targetVals[4], benchScore: benchVals[4], desc: 'Cobertura Art. 35' }},
          {{ name: '6. Cobranza Premios', val: `${{(target.calidad_cartera || 0).toFixed(1)}}%`, benchVal: `${{(bench.calidad_cartera || 0).toFixed(1)}}%`, score: targetVals[5], benchScore: benchVals[5], desc: 'Premios a Cobrar' }}
        ];

        breakdownEl.innerHTML = axesList.map(ax => {{
          const diff = ax.score - ax.benchScore;
          const sign = diff >= 0 ? '+' : '';
          const barColor = ax.score >= 70 ? 'bg-emerald-500' : (ax.score >= 45 ? 'bg-amber-500' : 'bg-rose-500');
          return `
            <div class="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800 flex flex-col justify-between">
              <div class="flex items-center justify-between text-[11px] font-sans font-bold text-white">
                <span>${{ax.name}}</span>
                <span class="font-mono ${{ax.score >= 70 ? 'text-emerald-400' : (ax.score >= 45 ? 'text-amber-400' : 'text-rose-400')}}">${{ax.score}}/100</span>
              </div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full my-1.5 overflow-hidden">
                <div class="${{barColor}} h-full rounded-full" style="width: ${{ax.score}}%"></div>
              </div>
              <div class="flex items-center justify-between text-[10px] text-slate-400">
                <span>Real: <b class="text-slate-200">${{ax.val}}</b></span>
                <span class="${{diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{sign}}${{diff}} pts</span>
              </div>
            </div>
          `;
        }}).join('');
      }}
    }}

    function renderManagementDiagnosis(target, bench, title) {{
      const diagEl = document.getElementById('execDiagnosticContent');
      if (!diagEl) return;

      const strengths = [];
      const warnings = [];

      // Suscripcion
      if (target.combined_ratio <= 100.0) {{
        strengths.push(`<b>Ganancia Técnica Neta:</b> Ratio Combinado del <b>${{target.combined_ratio.toFixed(1)}}%</b> (operación de suscripción superavitaria).`);
      }} else {{
        warnings.push(`<b>Déficit de Suscripción:</b> Ratio Combinado del <b>${{target.combined_ratio.toFixed(1)}}%</b> (costo y gastos superan la emisión devengada).`);
      }}

      // Siniestralidad
      if (target.loss_ratio <= 65.0) {{
        strengths.push(`<b>Excelente Control de Siniestros:</b> Loss Ratio del <b>${{target.loss_ratio.toFixed(1)}}%</b>.`);
      }} else if (target.loss_ratio > 75.0) {{
        warnings.push(`<b>Elevada Siniestralidad Devengada:</b> Loss Ratio del <b>${{target.loss_ratio.toFixed(1)}}%</b>.`);
      }}

      // Financiero
      if (target.roi_inversiones >= 0.0) {{
        strengths.push(`<b>Gestión Financiera Positiva:</b> Rendimiento ROI de inversiones del <b>${{target.roi_inversiones.toFixed(1)}}%</b>.`);
      }} else {{
        warnings.push(`<b>Rendimiento Financiero Negativo:</b> ROI de inversiones del <b>${{target.roi_inversiones.toFixed(1)}}%</b>.`);
      }}

      // Cobertura
      if (target.cobertura_reservas >= 1.15) {{
        strengths.push(`<b>Solvencia Regulatoria Holgada:</b> Cobertura de Compromisos Técnicos de <b>${{target.cobertura_reservas.toFixed(2)}}x</b>.`);
      }} else if (target.cobertura_reservas < 1.0) {{
        warnings.push(`<b>Alerta de Solvencia SSN:</b> Cobertura de <b>${{target.cobertura_reservas.toFixed(2)}}x</b> (por debajo de la exigencia legal de 1.00x).`);
      }}

      // Cobranza
      if (target.calidad_cartera <= 30.0) {{
        strengths.push(`<b>Cobranza Rápida:</b> Cartera a cobrar en <b>${{target.calidad_cartera.toFixed(1)}}%</b> de las primas.`);
      }} else if (target.calidad_cartera > 42.0) {{
        warnings.push(`<b>Atraso en Cobranzas:</b> Premios a cobrar representan el <b>${{target.calidad_cartera.toFixed(1)}}%</b> de las primas.`);
      }}

      let leftHtml = '';
      if (strengths.length > 0) {{
        leftHtml = `
          <div class="p-4 bg-emerald-500/10 border border-emerald-500/25 rounded-xl space-y-2">
            <div class="text-emerald-400 font-bold flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <i class="fa-solid fa-circle-check"></i> Fortalezas Principales (${{strengths.length}})
            </div>
            <ul class="list-disc list-inside space-y-1.5 text-slate-200 text-xs">
              ${{strengths.map(s => `<li>${{s}}</li>`).join('')}}
            </ul>
          </div>
        `;
      }} else {{
        leftHtml = `
          <div class="p-4 bg-slate-900/60 border border-slate-800 rounded-xl text-slate-400 text-xs flex items-center justify-center">
            Sin fortalezas destacadas en este período
          </div>
        `;
      }}

      let rightHtml = '';
      if (warnings.length > 0) {{
        rightHtml = `
          <div class="p-4 bg-amber-500/10 border border-amber-500/25 rounded-xl space-y-2">
            <div class="text-amber-400 font-bold flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <i class="fa-solid fa-triangle-exclamation"></i> Puntos de Atención & Desvíos (${{warnings.length}})
            </div>
            <ul class="list-disc list-inside space-y-1.5 text-slate-200 text-xs">
              ${{warnings.map(w => `<li>${{w}}</li>`).join('')}}
            </ul>
          </div>
        `;
      }} else {{
        rightHtml = `
          <div class="p-4 bg-emerald-500/10 border border-emerald-500/25 rounded-xl text-emerald-300 text-xs flex items-center justify-center font-semibold">
            ✓ No se detectan desvíos críticos ni alertas en este perfil
          </div>
        `;
      }}

      diagEl.innerHTML = leftHtml + rightHtml;
    }}

    function renderManagementTable() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      let list = data.companies;
      if (state.gestScope !== 'Todos' && state.gestScope !== 'cia') {{
        list = data.companies.filter(x => x.tipo_entidad === state.gestScope);
      }}

      const mode = state.gestFilterMode || 'all';
      let filtered = [...list];
      if (mode === 'loss_high') {{
        filtered = filtered.filter(c => (c.combined_ratio || 0) > 100.0);
      }} else if (mode === 'cob_low') {{
        filtered = filtered.filter(c => (c.cobertura_reservas || 0) < 1.0);
      }} else if (mode === 'integral_win') {{
        filtered = filtered.filter(c => (c.combined_ratio || 0) <= 100.0 && (c.roi_inversiones || 0) >= 0.0);
      }} else if (mode === 'slow_collect') {{
        filtered = filtered.filter(c => (c.calidad_cartera || 0) > 35.0);
      }}

      filtered.sort((a, b) => (a.combined_ratio || 0) - (b.combined_ratio || 0));

      const isLaSegunda = c => ['0117', '0317', '0436', '0618'].includes(c.cod_cia) || c.razon_social.toUpperCase().includes('SEGUNDA');

      const tbody = document.getElementById('managementTableBody');
      tbody.innerHTML = filtered.map((c, i) => {{
        const isLS = isLaSegunda(c);
        const isHL = (state.selectedCompanyCode === c.cod_cia);
        return `
        <tr class="hover:bg-slate-800/60 ${{isHL ? 'bg-amber-500/20 border-l-4 border-l-amber-400 font-bold' : (isLS ? 'bg-amber-500/10 border-l-4 border-l-amber-400/70' : '')}} cursor-pointer" onclick="onCompanyDropdownChange('${{c.cod_cia}}')">
          <td class="py-1.5 px-2 text-center text-slate-400 font-mono">${{i+1}}</td>
          <td class="py-1.5 px-2 font-semibold text-white truncate max-w-[180px] whitespace-nowrap" title="${{c.razon_social}}">
            ${{c.razon_social}}
            ${{isLS ? '<span class="ml-1 px-1 py-0.2 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">★ LS</span>' : ''}}
          </td>
          <td class="py-1.5 px-2 text-center">${{getTipoBadge(c.tipo_entidad)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.combined_ratio <= 100 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.combined_ratio)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatPercent(c.loss_ratio)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatPercent(c.comm_ratio)}}</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{formatPercent(c.exp_ratio)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.roi_inversiones >= 0 ? 'text-brand-blue' : 'text-rose-400'}}">${{formatPercent(c.roi_inversiones)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.cobertura_reservas >= 1.0 ? 'text-emerald-400' : 'text-rose-400'}}">${{(c.cobertura_reservas || 0).toFixed(2)}}x</td>
          <td class="py-1.5 px-2 text-right text-slate-300">${{(c.apalancamiento || 0).toFixed(2)}}x</td>
          <td class="py-1.5 px-2 text-right text-amber-300">${{formatPercent(c.calidad_cartera)}}</td>
          <td class="py-1.5 px-2 text-right font-bold ${{c.roe >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{formatPercent(c.roe)}}</td>
          <td class="py-1.5 px-2 text-center" onclick="event.stopPropagation()">
            <button onclick="onCompanyDropdownChange('${{c.cod_cia}}')" class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500 hover:text-white transition-colors text-[9px] font-bold">Ver</button>
          </td>
        </tr>
      `}}).join('');
    }}

    // Export to CSV
    function exportToCSV() {{
      const list = getFilteredCompanies();
      const headers = ['cod_cia', 'razon_social', 'tipo_entidad', 'primas_emitidas', 'primas_devengadas', 'var_reservas', 'siniestros', 'resultado_tecnico', 'resultado_financiero', 'resultado_neto', 'activo', 'inversiones', 'patrimonio_neto', 'loss_ratio', 'combined_ratio', 'cobertura_reservas', 'comm_ratio', 'exp_ratio', 'roi_inversiones', 'roe', 'roa', 'margen_neto'];
      
      let csv = headers.join(',') + '\\n';
      list.forEach(c => {{
        const row = [
          `"${{c.cod_cia}}"`,
          `"${{c.razon_social.replace(/"/g, '""')}}"`,
          `"${{c.tipo_entidad}}"`,
          c.primas_emitidas || 0,
          c.primas_devengadas || 0,
          c.var_reservas || 0,
          c.siniestros || 0,
          c.resultado_tecnico || 0,
          c.resultado_financiero || 0,
          c.resultado_neto || 0,
          c.activo || 0,
          c.inversiones || 0,
          c.patrimonio_neto || 0,
          c.loss_ratio || 0,
          c.combined_ratio || 0,
          c.cobertura_reservas || 0,
          c.comm_ratio || 0,
          c.exp_ratio || 0,
          c.roi_inversiones || 0,
          c.roe || 0,
          c.roa || 0,
          c.margen_neto || 0
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

    // ========================================================
    // TAB 7: BALANCES CONTABLES & HIERARCHICAL TREE ENGINE
    // ========================================================
    function setBalScope(scope) {{
      state.balScope = scope;
      
      // Update Scope Pills UI
      ['market', 'group', 'Patrimoniales y Mixtas', 'Riesgos del Trabajo (ART)', 'Seguros de Personas', 'Seguros de Retiro', 'cia'].forEach(s => {{
        const btn = document.getElementById(`balScopeBtn-${{s}}`);
        if (btn) {{
          if (state.balScope === s) {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 font-bold transition-all shadow-md shadow-emerald-500/20';
          }} else {{
            btn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
          }}
        }}
      }});

      updateAllComboboxLabels();
      renderBalancesTab();
    }}

    function setBalStatement(stmt) {{
      state.balStatement = stmt;
      
      // Update Statement Switch UI
      ['patrimonial', 'edr', 'tec', 'fin', 'ramo'].forEach(st => {{
        const btn = document.getElementById(`balStmtBtn-${{st}}`);
        if (btn) {{
          if (state.balStatement === st) {{
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20';
          }} else {{
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all';
          }}
        }}
      }});

      // Show/hide subramo select
      const subContainer = document.getElementById('balSubramoContainer');
      if (subContainer) {{
        if (stmt === 'ramo') subContainer.classList.remove('hidden');
        else subContainer.classList.add('hidden');
      }}

      renderBalancesTab();
    }}

    function setBalSubramo(subramoCode) {{
      state.balSubramo = subramoCode;
      renderBalancesTab();
    }}

    function filterBalTree(query) {{
      state.balSearchQuery = query || '';
      renderBalanceTree();
    }}

    function toggleBalNode(code) {{
      if (state.balExpandedNodes.has(code)) {{
        state.balExpandedNodes.delete(code);
      }} else {{
        state.balExpandedNodes.add(code);
      }}
      renderBalanceTree();
    }}

    function expandAllBalNodes() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.plan_de_cuentas) return;
      Object.keys(data.plan_de_cuentas).forEach(k => state.balExpandedNodes.add(k));
      renderBalanceTree();
    }}

    function collapseBalToLevel(maxLevel) {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.plan_de_cuentas) return;
      state.balExpandedNodes.clear();
      Object.entries(data.plan_de_cuentas).forEach(([k, v]) => {{
        if (v.nivel < maxLevel) {{
          state.balExpandedNodes.add(k);
        }}
      }});
      renderBalanceTree();
    }}

    function renderBalancesTab() {{
      const data = window.DATA_SINENSUP;
      if (!data) return;

      // Update Header Title & Subtitle based on active scope
      const titleEl = document.getElementById('balSelectedTitle');
      const badgeEl = document.getElementById('balSelectedBadge');
      const countEl = document.getElementById('balEntitiesCount');
      const subTitleEl = document.getElementById('balSelectedSubtitle');

      if (!titleEl || !badgeEl || !countEl) return;

      if (state.balScope === 'market') {{
        titleEl.innerText = 'Mercado Total Consolidado';
        badgeEl.innerText = '185 Cías';
        countEl.innerText = '185';
        if (subTitleEl) subTitleEl.innerText = 'Plan de Cuentas Oficial SSN • Apertura Jerárquica Multinivel por Cuentas e Importes';
      }} else if (state.balScope === 'group') {{
        const g = (data.groups_by_id && data.groups_by_id[state.selectedGroupId]) || (data.groups && data.groups[0]);
        titleEl.innerText = `${{g.name}} (Consolidado)`;
        badgeEl.innerText = `${{g.entities_count}} Cías del Grupo`;
        countEl.innerText = g.entities_count.toString();
        if (subTitleEl) subTitleEl.innerText = `Balance Consolidado del Grupo • ${{g.description}}`;
      }} else if (state.balScope === 'cia') {{
        const cia = data.companies_by_code[state.selectedCompanyCode];
        titleEl.innerText = cia ? cia.razon_social : 'Aseguradora';
        badgeEl.innerText = cia ? `${{cia.cod_cia}} • ${{cia.tipo_entidad}}` : 'Individual';
        countEl.innerText = '1';
        if (subTitleEl) subTitleEl.innerText = 'Plan de Cuentas Oficial SSN • Apertura Jerárquica Multinivel por Cuentas e Importes';
      }} else {{
        const count = data.companies.filter(c => c.tipo_entidad === state.balScope).length;
        titleEl.innerText = `${{state.balScope}} (Consolidado)`;
        badgeEl.innerText = `${{count}} Cías`;
        countEl.innerText = count.toString();
        if (subTitleEl) subTitleEl.innerText = 'Plan de Cuentas Oficial SSN • Apertura Jerárquica Multinivel por Cuentas e Importes';
      }}

      renderBalanceKpis();
      renderBalanceTree();
    }}

    function getActiveBalanceDict() {{
      const data = window.DATA_SINENSUP;
      if (!data) return {{}};

      if (state.balStatement === 'ramo') {{
        const sub = state.balSubramo;
        if (state.balScope === 'market') {{
          return (data.market_balances_subramos && data.market_balances_subramos[sub]) || {{}};
        }} else if (state.balScope === 'group') {{
          const gMap = (data.groups_balances_subramos && data.groups_balances_subramos[state.selectedGroupId]) || {{}};
          return gMap[sub] || {{}};
        }} else if (state.balScope in (data.segment_balances_subramos || {{}})) {{
          return data.segment_balances_subramos[state.balScope][sub] || {{}};
        }} else if (state.balScope === 'cia') {{
          const ciaMap = (data.cias_balances_subramos && data.cias_balances_subramos[state.selectedCompanyCode]) || {{}};
          return ciaMap[sub] || {{}};
        }}
      }} else {{
        if (state.balScope === 'market') {{
          return data.market_balances_general || {{}};
        }} else if (state.balScope === 'group') {{
          return (data.groups_balances_general && data.groups_balances_general[state.selectedGroupId]) || {{}};
        }} else if (state.balScope in (data.segment_balances_general || {{}})) {{
          return data.segment_balances_general[state.balScope] || {{}};
        }} else if (state.balScope === 'cia') {{
          return (data.cias_balances_general && data.cias_balances_general[state.selectedCompanyCode]) || {{}};
        }}
      }}
      return {{}};
    }}

    function renderBalanceKpis() {{
      const banner = document.getElementById('balKpiBanner');
      if (!banner) return;
      const dict = getActiveBalanceDict();

      if (state.balStatement === 'patrimonial') {{
        const activo = dict['1.00.00.00.00.00.00.00'] || 0;
        const pasivo = dict['2.00.00.00.00.00.00.00'] || 0;
        const pn = dict['3.00.00.00.00.00.00.00'] || 0;
        const cuadratura = activo - (pasivo + pn);

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-brand-blue">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">1. TOTAL ACTIVO</div>
            <div class="text-lg font-bold font-mono text-white mt-1">${{formatARS(activo)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Estructura Patrimonial</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">2. TOTAL PASIVO</div>
            <div class="text-lg font-bold font-mono text-rose-300 mt-1">${{formatARS(pasivo)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Deudas + Compromisos Téc.</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-purple-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">3. PATRIMONIO NETO</div>
            <div class="text-lg font-bold font-mono text-purple-300 mt-1">${{formatARS(pn)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Capital Propio + Reservas</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 ${{Math.abs(cuadratura) < 1000 ? 'border-l-emerald-500' : 'border-l-amber-500'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">CUADRATURA CONTABLE</div>
            <div class="text-lg font-bold font-mono ${{Math.abs(cuadratura) < 1000 ? 'text-emerald-400' : 'text-amber-400'}} mt-1">
              ${{Math.abs(cuadratura) < 1000 ? '✓ Cuadrado (Act = Pas + PN)' : formatARS(cuadratura)}}
            </div>
            <div class="text-[10px] text-slate-400 mt-1">Ecuación Patrimonial Fundamental</div>
          </div>
        `;
      }} else if (state.balStatement === 'tec') {{
        const ingTec = dict['5.01.00.00.00.00.00.00'] || 0;
        const egrTec = dict['4.01.00.00.00.00.00.00'] || 0;
        const resTec = ingTec - egrTec;

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">INGRESOS TÉCNICOS (5.01)</div>
            <div class="text-lg font-bold font-mono text-emerald-400 mt-1">${{formatARS(ingTec)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Primas Devengadas + Otros Ing. Téc.</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">EGRESOS TÉCNICOS (4.01)</div>
            <div class="text-lg font-bold font-mono text-rose-400 mt-1">${{formatARS(egrTec)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Siniestros + Gastos Prod./Explotación</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 ${{resTec >= 0 ? 'border-l-emerald-400' : 'border-l-rose-400'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO TÉCNICO (ET)</div>
            <div class="text-lg font-bold font-mono ${{resTec >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatARS(resTec)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{resTec >= 0 ? 'Superávit Técnico' : 'Déficit Técnico'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-400">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">ESTRUCTURA CONTABLE</div>
            <div class="text-base font-bold font-mono text-amber-300 mt-1">ESTRUCTURA TÉCNICA</div>
            <div class="text-[10px] text-slate-400 mt-1">Rubros 4.01 vs 5.01</div>
          </div>
        `;
      }} else if (state.balStatement === 'fin') {{
        const ingFin = dict['5.02.00.00.00.00.00.00'] || 0;
        const egrFin = dict['4.02.00.00.00.00.00.00'] || 0;
        const resFin = ingFin - egrFin;

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">INGRESOS FINANCIEROS (5.02)</div>
            <div class="text-lg font-bold font-mono text-emerald-400 mt-1">${{formatARS(ingFin)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Rentas + Tenencia + Realización</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">EGRESOS FINANCIEROS (4.02)</div>
            <div class="text-lg font-bold font-mono text-rose-400 mt-1">${{formatARS(egrFin)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Gastos Financieros + Desvalorizaciones</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 ${{resFin >= 0 ? 'border-l-emerald-400' : 'border-l-rose-400'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO FINANCIERO (EF)</div>
            <div class="text-lg font-bold font-mono ${{resFin >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatARS(resFin)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{resFin >= 0 ? 'Ganancia Financiera' : 'Pérdida Financiera'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-400">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">ESTRUCTURA CONTABLE</div>
            <div class="text-base font-bold font-mono text-amber-300 mt-1">ESTRUCTURA FINANCIERA</div>
            <div class="text-[10px] text-slate-400 mt-1">Rubros 4.02 vs 5.02</div>
          </div>
        `;
      }} else if (state.balStatement === 'ramo') {{
        const ingRamo = dict['5.01.00.00.00.00.00.00'] || dict['5.00.00.00.00.00.00.00'] || 0;
        const egrRamo = dict['4.01.00.00.00.00.00.00'] || dict['4.00.00.00.00.00.00.00'] || 0;
        const resRamo = ingRamo - egrRamo;

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">INGRESOS TÉCNICOS RAMO</div>
            <div class="text-lg font-bold font-mono text-emerald-400 mt-1">${{formatARS(ingRamo)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Devengamiento Subramo</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">EGRESOS TÉCNICOS RAMO</div>
            <div class="text-lg font-bold font-mono text-rose-400 mt-1">${{formatARS(egrRamo)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Siniestros + Gastos Subramo</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 ${{resRamo >= 0 ? 'border-l-emerald-400' : 'border-l-rose-400'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO TÉCNICO RAMO</div>
            <div class="text-lg font-bold font-mono ${{resRamo >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatARS(resRamo)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{resRamo >= 0 ? 'Superávit del Subramo' : 'Déficit del Subramo'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-400">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">SUBRAMO SELECCIONADO</div>
            <div class="text-sm font-bold font-mono text-amber-300 mt-1 truncate" title="${{state.balSubramo}}">${{state.balSubramo}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Apertura Técnica SSN</div>
          </div>
        `;
      }} else {{
        // EDR (Estado de Resultados Integral)
        const perdidas = dict['4.00.00.00.00.00.00.00'] || 0;
        const ganancias = dict['5.00.00.00.00.00.00.00'] || 0;
        const resNeto = ganancias - perdidas;

        banner.innerHTML = `
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">TOTAL INGRESOS / GANANCIAS</div>
            <div class="text-lg font-bold font-mono text-emerald-400 mt-1">${{formatARS(ganancias)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Capítulo 5.00 Integral</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">TOTAL EGRESOS / PÉRDIDAS</div>
            <div class="text-lg font-bold font-mono text-rose-400 mt-1">${{formatARS(perdidas)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">Capítulo 4.00 Integral</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 ${{resNeto >= 0 ? 'border-l-emerald-400' : 'border-l-rose-400'}}">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">RESULTADO NETO DEL PERÍODO</div>
            <div class="text-lg font-bold font-mono ${{resNeto >= 0 ? 'text-emerald-400' : 'text-rose-400'}} mt-1">${{formatARS(resNeto)}}</div>
            <div class="text-[10px] text-slate-400 mt-1">${{resNeto >= 0 ? 'Ganancia Neta' : 'Pérdida Neta'}}</div>
          </div>
          <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-400">
            <div class="text-[11px] font-semibold text-slate-400 uppercase">ESTADO CONTABLE</div>
            <div class="text-base font-bold font-mono text-amber-300 mt-1">ESTADO DE RESULTADOS</div>
            <div class="text-[10px] text-slate-400 mt-1">Plan Oficial SSN</div>
          </div>
        `;
      }}
    }}

    function renderBalanceTree() {{
      const tbody = document.getElementById('balanceTreeTableBody');
      if (!tbody) return;
      const data = window.DATA_SINENSUP;
      if (!data || !data.plan_de_cuentas) return;

      const dict = getActiveBalanceDict();
      const plan = data.plan_de_cuentas;

      // 1. Determine accounts in statement
      let rootPrefixes = [];
      if (state.balStatement === 'patrimonial') {{
        rootPrefixes = ['1.', '2.', '3.'];
      }} else if (state.balStatement === 'edr') {{
        rootPrefixes = ['4.', '5.'];
      }} else if (state.balStatement === 'tec') {{
        rootPrefixes = ['4.01.', '5.01.'];
      }} else if (state.balStatement === 'fin') {{
        rootPrefixes = ['4.02.', '5.02.'];
      }} else if (state.balStatement === 'ramo') {{
        rootPrefixes = ['4.', '5.'];
      }}

      // 2. Filter relevant accounts
      const allCodes = Object.keys(plan).sort();
      const stmtCodes = allCodes.filter(c => rootPrefixes.some(p => c.startsWith(p)));

      // 3. Build parent-child tree mapping
      const childrenMap = {{}};
      stmtCodes.forEach(code => {{
        const p = plan[code];
        const padre = p.padre_codigo || p.padre;
        if (padre && plan[padre]) {{
          if (!childrenMap[padre]) childrenMap[padre] = [];
          childrenMap[padre].push(code);
        }}
      }});

      // 4. Compute chapter totals for percentages
      const chapterTotals = {{
        '1': dict['1.00.00.00.00.00.00.00'] || 0,
        '2': dict['2.00.00.00.00.00.00.00'] || 0,
        '3': dict['3.00.00.00.00.00.00.00'] || 0,
        '4': dict['4.00.00.00.00.00.00.00'] || dict['4.01.00.00.00.00.00.00'] || dict['4.02.00.00.00.00.00.00'] || 0,
        '5': dict['5.00.00.00.00.00.00.00'] || dict['5.01.00.00.00.00.00.00'] || dict['5.02.00.00.00.00.00.00'] || 0
      }};

      // 5. Check if search query active
      const searchQ = (state.balSearchQuery || '').toLowerCase().trim();
      let matchedCodes = new Set();
      if (searchQ) {{
        stmtCodes.forEach(c => {{
          const desc = (plan[c].desc || '').toLowerCase();
          if (c.includes(searchQ) || desc.includes(searchQ)) {{
            matchedCodes.add(c);
            // Add all ancestors
            let curr = plan[c].padre_codigo || plan[c].padre;
            while (curr && plan[curr]) {{
              matchedCodes.add(curr);
              curr = plan[curr].padre_codigo || plan[curr].padre;
            }}
          }}
        }});
      }}

      // 6. Helper to check if an account is visible
      function isAccountVisible(code) {{
        if (searchQ) {{
          return matchedCodes.has(code);
        }}
        const p = plan[code];
        if (state.balStatement === 'patrimonial' || state.balStatement === 'edr' || state.balStatement === 'ramo') {{
          if (p.nivel === 1) return true;
        }} else if (state.balStatement === 'tec' || state.balStatement === 'fin') {{
          if (p.nivel === 2) return true;
        }}
        
        let curr = p.padre_codigo || p.padre;
        while (curr && plan[curr]) {{
          // In tec / fin, stop traversing once reaching above level 2 root
          if ((state.balStatement === 'tec' || state.balStatement === 'fin') && plan[curr].nivel < 2) break;
          if (!state.balExpandedNodes.has(curr)) return false;
          curr = plan[curr].padre_codigo || plan[curr].padre;
        }}
        return true;
      }}

      // 7. Render visible rows
      let rowsHtml = '';
      let visibleCount = 0;

      stmtCodes.forEach(code => {{
        if (!isAccountVisible(code)) return;

        const info = plan[code];
        const saldo = dict[code] !== undefined ? dict[code] : 0;
        
        // Skip accounts that have zero saldo and no children with saldo unless search is active
        const hasChildren = childrenMap[code] && childrenMap[code].length > 0;
        if (!searchQ && saldo === 0 && !hasChildren) return;

        visibleCount++;
        const isExp = state.balExpandedNodes.has(code) || searchQ !== '';
        const nivel = info.nivel;
        const indentPx = (nivel - 1) * 20;

        // Button toggle
        let toggleBtn = '';
        if (hasChildren) {{
          toggleBtn = `
            <button type="button" onclick="event.stopPropagation(); window.toggleBalNode('${{code}}')" 
                    class="w-7 h-7 flex items-center justify-center rounded-lg border font-mono font-black text-sm transition-all cursor-pointer shadow-md ${{isExp ? 'text-amber-300 bg-amber-500/25 border-amber-500/60 hover:bg-amber-500/40' : 'text-emerald-300 bg-emerald-500/25 border-emerald-500/60 hover:bg-emerald-500/40'}}"
                    title="${{isExp ? 'Colapsar subcuentas' : 'Abrir cuentas dependientes'}}">
              <span class="leading-none">${{isExp ? '−' : '+'}}</span>
            </button>
          `;
        }} else {{
          toggleBtn = `<span class="text-slate-600 text-xs block text-center font-mono">•</span>`;
        }}

        // Percentage
        const rootChap = code.charAt(0);
        const chapTot = chapterTotals[rootChap] || 0;
        let pctStr = '-';
        if (chapTot > 0 && saldo !== 0) {{
          const pct = Math.min(100.0, (Math.abs(saldo) / chapTot) * 100.0);
          pctStr = `${{pct.toFixed(2)}}%`;
        }}

        // Row styling according to level
        let rowStyle = '';
        let descStyle = '';
        let codeStyle = '';
        if (nivel === 1) {{
          rowStyle = 'bg-slate-900/95 font-bold border-t-2 border-slate-700';
          descStyle = 'text-white text-xs tracking-wide uppercase font-bold';
          codeStyle = 'text-amber-400 font-bold';
        }} else if (nivel === 2) {{
          rowStyle = 'bg-slate-900/50 font-semibold border-t border-slate-800';
          descStyle = 'text-slate-200 text-xs font-semibold';
          codeStyle = 'text-emerald-400 font-semibold';
        }} else if (nivel === 3) {{
          rowStyle = 'hover:bg-slate-800/40';
          descStyle = 'text-slate-300 text-[11px]';
          codeStyle = 'text-sky-400';
        }} else {{
          rowStyle = 'hover:bg-slate-800/30 text-slate-400';
          descStyle = 'text-slate-300 text-[11px]';
          codeStyle = 'text-slate-400';
        }}

        // Level badge
        const levelBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-mono bg-slate-800 border border-slate-700 text-slate-400">N${{nivel}}</span>`;

        rowsHtml += `
          <tr class="${{rowStyle}} transition-colors ${{hasChildren ? 'cursor-pointer' : ''}}" ${{hasChildren ? `onclick="window.toggleBalNode('${{code}}')"` : ''}}>
            <td class="py-2 px-3 text-center w-12" onclick="event.stopPropagation()">${{toggleBtn}}</td>
            <td class="py-2 px-3 ${{codeStyle}} font-mono whitespace-nowrap">${{code}}</td>
            <td class="py-2 px-3" style="padding-left: ${{indentPx + 12}}px;">
              <span class="${{descStyle}}">${{info.desc}}</span>
              ${{hasChildren ? `<span class="ml-2 text-[10px] text-slate-500 font-normal">(${{childrenMap[code].length}} subcuentas)</span>` : ''}}
            </td>
            <td class="py-2 px-3 text-right font-mono font-bold whitespace-nowrap ${{saldo < 0 ? 'text-rose-400' : (saldo > 0 ? 'text-slate-100' : 'text-slate-500')}}">
              ${{saldo === 0 ? '$0' : formatARS(saldo)}}
            </td>
            <td class="py-2 px-3 text-right font-mono text-[10px] text-slate-400">${{pctStr}}</td>
            <td class="py-2 px-3 text-center">${{levelBadge}}</td>
          </tr>
        `;
      }});

      if (visibleCount === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="py-8 text-center text-slate-500 text-xs">
              No se encontraron cuentas contables con los filtros seleccionados
            </td>
          </tr>
        `;
      }} else {{
        tbody.innerHTML = rowsHtml;
      }}
    }}

    function exportBalanceCSV() {{
      const data = window.DATA_SINENSUP;
      if (!data || !data.plan_de_cuentas) return;

      const dict = getActiveBalanceDict();
      const plan = data.plan_de_cuentas;

      let csv = 'codigo_cuenta,descripcion,nivel,saldo_ars,alcance,estado\\n';
      const scopeLabel = state.balScope === 'market' ? 'Mercado Total' : (state.balScope === 'cia' ? state.selectedCompanyCode : state.balScope);

      Object.entries(plan).forEach(([code, info]) => {{
        const saldo = dict[code] || 0;
        csv += `"${{code}}","${{info.desc.replace(/"/g, '""')}}",${{info.nivel}},${{saldo}},"${{scopeLabel}}","${{state.balStatement}}"\\n`;
      }});

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `balance_ssn_${{state.balStatement}}_${{scopeLabel.toLowerCase().replace(/ /g, '_')}}.csv`;
      a.click();
    }}

    // Export all tree, group and ramos ranking functions to window scope
    window.setRankingMode = setRankingMode;
    window.openGroupModal = openGroupModal;
    window.closeGroupModal = closeGroupModal;
    window.renderGroupsRankingTable = renderGroupsRankingTable;
    window.initRamosRankingsTab = initRamosRankingsTab;
    window.toggleRamosSection = toggleRamosSection;
    window.toggleRamosGroup = toggleRamosGroup;
    window.setRamosSection = toggleRamosSection;
    window.setRamosGroup = toggleRamosGroup;
    window.setRamosSubramo = setRamosSubramo;
    window.setRamosRankMode = setRamosRankMode;
    window.filterRamosRankingTable = filterRamosRankingTable;
    window.renderRamosRankingsTab = renderRamosRankingsTab;
    window.exportRamosRankCSV = exportRamosRankCSV;
    window.setBalScope = setBalScope;
    window.setBalStatement = setBalStatement;
    window.setBalSubramo = setBalSubramo;
    window.filterBalTree = filterBalTree;
    window.toggleBalNode = toggleBalNode;
    window.expandAllBalNodes = expandAllBalNodes;
    window.collapseBalToLevel = collapseBalToLevel;
    window.renderBalancesTab = renderBalancesTab;
    window.renderBalanceTree = renderBalanceTree;
    window.exportBalanceCSV = exportBalanceCSV;
  </script>
</body>
</html>
"""

    out_file = r"g:\Mi unidad\IA\Sinensup\index.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"index.html updated successfully ({os.path.getsize(out_file):,} bytes)")

if __name__ == '__main__':
    generate_html()
