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
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-crosshairs text-brand-red"></i> Matriz Estratégica: Margen Técnico vs. Rendimiento Financiero
            </h3>
            <p class="text-xs text-slate-400">Selecciona o haz clic en cualquier burbuja para resaltarla con su ficha y métricas</p>
          </div>

          <!-- Highlight Company Selector & Zoom Controls -->
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex items-center gap-1.5 bg-slate-900/90 px-2.5 py-1 rounded-lg border border-slate-700">
              <span class="text-xs text-slate-300 font-semibold flex items-center gap-1">
                <i class="fa-solid fa-bullseye text-brand-red"></i> Resaltar:
              </span>
              <select id="scatterCompanySelect" onchange="highlightScatterCompany(this.value)"
                      class="bg-slate-900 text-xs text-amber-300 font-semibold focus:outline-none max-w-[210px] truncate border-0">
                <option value="">-- Seleccionar aseguradora --</option>
              </select>
              <button id="clearHighlightBtn" onclick="highlightScatterCompany('')" class="hidden text-xs text-slate-400 hover:text-white px-1" title="Quitar selección">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

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
      <div class="glass-card p-5 rounded-xl w-full">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-trophy text-amber-400"></i> Ranking Top Aseguradoras del Segmento (por Primas Emitidas)
            </h3>
            <p class="text-xs text-slate-400">Principales aseguradoras ordenadas por volumen de Primas Emitidas (con inclusión fija de Grupo Asegurador La Segunda)</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] font-mono px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-lg font-bold">Top 15 + Grupo La Segunda</span>
          </div>
        </div>
        <div class="w-full overflow-hidden">
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

      <!-- Company Mini KPI Cards (6 Cards with Primas Emitidas & Variación de Reservas) -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
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
      <div class="glass-card p-5 rounded-xl border-l-4 border-l-amber-500 flex flex-wrap items-center justify-between gap-4">
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
            <select id="invCompanyDropdownSelect" onchange="onCompanyDropdownChange(this.value)"
                    class="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-amber-500 max-w-[240px] truncate"></select>
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
      <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
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
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
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
          <div id="investmentsPieChart" class="w-full h-72"></div>
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
                <th class="py-2.5 px-3 text-center">Tipo</th>
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
      selectedCompanyCode: '0436',
      highlightedCiaCode: null,
      ramosScope: 'cia',
      invScope: 'cia',
      invTopMetric: 'activo'
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
      buildCompanyDropdowns();
      buildScatterCompanySelect();
      setupSearchAutocomplete();
      renderAll();
    }}

    function setSegmentFilter(seg) {{
      state.selectedSegment = seg;
      buildSegmentPills();
      buildScatterCompanySelect();
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

    function buildCompanyDropdowns() {{
      const data = window.DATA_SINENSUP;
      const selects = [
        document.getElementById('companyDropdownSelect'),
        document.getElementById('invCompanyDropdownSelect')
      ];

      const sorted = [...data.companies].sort((a, b) => a.razon_social.localeCompare(b.razon_social));
      
      selects.forEach(select => {{
        if (!select) return;
        select.innerHTML = '';
        sorted.forEach(c => {{
          const opt = document.createElement('option');
          opt.value = c.cod_cia;
          opt.innerText = `${{c.cod_cia}} - ${{c.razon_social}}`;
          if (c.cod_cia === state.selectedCompanyCode) opt.selected = true;
          select.appendChild(opt);
        }});
      }});
    }}

    function buildScatterCompanySelect() {{
      const select = document.getElementById('scatterCompanySelect');
      if (!select) return;
      select.innerHTML = '<option value="">-- Seleccionar aseguradora --</option>';

      const list = getFilteredCompanies();
      const sorted = [...list].sort((a, b) => a.razon_social.localeCompare(b.razon_social));
      sorted.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c.cod_cia;
        opt.innerText = `${{c.cod_cia}} - ${{c.razon_social}}`;
        if (c.cod_cia === state.highlightedCiaCode) opt.selected = true;
        select.appendChild(opt);
      }});
    }}

    function highlightScatterCompany(code) {{
      state.highlightedCiaCode = code || null;
      const select = document.getElementById('scatterCompanySelect');
      if (select) select.value = code || '';
      
      const clearBtn = document.getElementById('clearHighlightBtn');
      if (clearBtn) {{
        if (code) clearBtn.classList.remove('hidden');
        else clearBtn.classList.add('hidden');
      }}

      renderMarketScatterPlot(getFilteredCompanies());
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
      state.highlightedCiaCode = code;
      document.getElementById('globalCompanySearch').value = '';
      document.getElementById('searchResultsDropdown').classList.add('hidden');
      
      const cSel1 = document.getElementById('companyDropdownSelect');
      if (cSel1) cSel1.value = code;
      const cSel2 = document.getElementById('invCompanyDropdownSelect');
      if (cSel2) cSel2.value = code;

      switchTab('ficha-compania');
    }}

    function onCompanyDropdownChange(code) {{
      state.selectedCompanyCode = code;
      state.highlightedCiaCode = code;
      
      const cSel1 = document.getElementById('companyDropdownSelect');
      if (cSel1) cSel1.value = code;
      const cSel2 = document.getElementById('invCompanyDropdownSelect');
      if (cSel2) cSel2.value = code;

      // If in investments tab, switch scope back to company
      if (state.currentTab === 'inversiones-finanzas') {{
        setInvScope('cia');
      }} else {{
        renderAll();
      }}
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
    // TAB 3 RENDER: RAMOS (ESCALA HISPANA Y VISIBILIDAD MEJORADA)
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

      // Custom Y-axis ticks in exact standard format (B, MM, M, K)
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

    // ----------------------------------------------------
    // TAB 4 RENDER: INVERSIONES Y FINANZAS (COMPAÑÍA, SEGMENTOS Y TOP 20)
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
        // Segment scope
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
          <td class="py-2 px-3 text-center">${{getTipoBadge(item.tipo_entidad)}}</td>
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
      const headers = ['cod_cia', 'razon_social', 'tipo_entidad', 'primas_emitidas', 'primas_devengadas', 'var_reservas', 'siniestros', 'resultado_tecnico', 'resultado_financiero', 'resultado_neto', 'activo', 'inversiones', 'patrimonio_neto', 'loss_ratio', 'combined_ratio', 'cobertura_reservas'];
      
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

    print(f"index.html updated successfully ({os.path.getsize(out_file):,} bytes)")

if __name__ == '__main__':
    generate_html()
