import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  THEME / GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #161922;
    --card:     #1e2330;
    --border:   #2a3048;
    --accent:   #5b8cff;
    --accent2:  #ff6b6b;
    --accent3:  #43e97b;
    --text:     #e8ecf4;
    --muted:    #7a84a0;
    --radius:   14px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* Cards */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .07em;
    margin-top: .35rem;
}
.kpi-delta {
    font-size: 0.82rem;
    margin-top: .4rem;
}
.delta-pos { color: var(--accent3); }
.delta-neg { color: var(--accent2); }

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    margin: 1.8rem 0 .8rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.section-title span.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
}

/* Page title */
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5b8cff 0%, #a855f7 60%, #ff6b6b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
}
.dash-subtitle {
    color: var(--muted);
    font-size: .9rem;
    margin-top: .2rem;
    margin-bottom: 1.6rem;
}

/* Tab nav override */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--surface);
    border-radius: var(--radius);
    padding: .3rem;
    gap: .3rem;
    border: 1px solid var(--border);
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: .84rem !important;
    color: var(--muted) !important;
    border-radius: 10px !important;
    padding: .5rem 1.2rem !important;
    border: none !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: var(--radius); }
iframe { border-radius: var(--radius) !important; }

/* Plotly charts background */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Multiselect tags */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #2a3559 !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PALETTE = ["#5b8cff","#a855f7","#ff6b6b","#43e97b","#ffd166","#06d6a0","#ef476f","#118ab2"]
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#e8ecf4", size=12),
    xaxis=dict(gridcolor="#1e2330", showgrid=True, zeroline=False,
               tickfont=dict(color="#7a84a0", size=11)),
    yaxis=dict(gridcolor="#1e2330", showgrid=True, zeroline=False,
               tickfont=dict(color="#7a84a0", size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8ecf4", size=11)),
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=PALETTE,
)

def apply_theme(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
SALES_COLS = [
    "Num.CMD","Date.CMD","Client","Adresse","Forme Juridique Client",
    "Wilaya","Code Produit","Produit","Catégorie Produit","Type vente",
    "Qté","Montant HT","Taxe","Montant TTC"
]
PURCHASES_COLS = [
    "Num.CMD","Date.CMD","Fournisseur","Type achat",
    "Code Produit","Produit","Catégorie Produit",
    "QTY","Montant HT","Taxe","Montant TTC"
]

SALES_DATA = """Num.CMD,Date.CMD,Client,Adresse,Forme Juridique Client,Wilaya,Code Produit,Produit,Catégorie Produit,Type vente,Qté,Montant HT,Taxe,Montant TTC
SLSD/0001,2024-12-28,SARL ABC,"Cité 20 Aout, Alger",SARL,Alger,LAP.0120,Laptop HP Probook G4,Laptop,Directe,4,500000,95000,595000
SLSD/0001,2024-12-28,SARL ABC,"Cité 20 Aout, Alger",SARL,Alger,PRI.0020,Printer Canon 6030,Imprimante,Directe,1,49000,9310,58310
SLSD/0001,2024-12-28,SARL ABC,"Cité 20 Aout, Alger",SARL,Alger,INK.0034,Toner Canon 6030,Consommable,Directe,1,1800,342,2142
SLSR/0002,2025-02-22,EURL XYZ,"Coopérative Rym, Blida",EURL,Blida,LAP.0011,Laptop Lenovo 110,Laptop,Revendeur,1,89000,16910,105910
SLSR/0002,2025-02-22,EURL XYZ,"Coopérative Rym, Blida",EURL,Blida,PRI.0020,Printer Canon 6030,Imprimante,Revendeur,2,98000,18620,116620
SLSR/0002,2025-02-22,EURL XYZ,"Coopérative Rym, Blida",EURL,Blida,INK.0004,Toner Canon 6030,Consommable,Revendeur,2,3600,684,4284
SLSR/0002,2025-02-22,EURL XYZ,"Coopérative Rym, Blida",EURL,Blida,SCA.0002,Scanner Epson 1600,Scanner,Revendeur,1,21000,3990,24990
SLSD/0003,2025-03-15,SARL AGRODZ,"Cité 310 logt Kouba, Alger",SARL,Alger,PRI.0011,Printer EPSON 3010,Imprimante,Directe,2,64000,12160,76160
SLSD/0003,2025-03-15,SARL AGRODZ,"Cité 310 logt Kouba, Alger",SARL,Alger,LAP.0120,Laptop HP Probook G4,Laptop,Directe,1,125000,23750,148750
SLSG/0004,2025-03-28,SNC Wiffak,"Boulvard Nord, Sétif",SNC,Sétif,INK.0001,INK Canon 3210,Consommable,Gros,10,18000,3420,21420
SLSD/0005,2025-03-28,EURL XYZ,"Coopérative Rym, Oran",EURL,Oran,LAP.0011,Laptop Lenovo 110,Laptop,Directe,3,267000,50730,317730
SLSD/0005,2025-03-28,EURL XYZ,"Coopérative Rym, Oran",EURL,Oran,PRI.0011,Printer EPSON 3010,Imprimante,Directe,1,32000,6080,38080
SLSD/0005,2025-03-28,EURL XYZ,"Coopérative Rym, Oran",EURL,Oran,INK.0005,INK Epson 110,Consommable,Directe,10,8000,1520,9520
SLSG/0006,2025-05-02,SARL ABC,"Cité 20 Aout, Alger",SARL,Alger,LAP.0120,Laptop HP Probook G4,Laptop,Gros,2,250000,47500,297500
SLSD/0007,2025-05-04,EURL HAMIDI,"Promotion Bahia, Oran",EURL,Oran,PRI.0020,Printer Canon 6030,Imprimante,Directe,2,98000,18620,116620
"""

PURCHASES_DATA = """Num.CMD,Date.CMD,Fournisseur,Type achat,Code Produit,Produit,Catégorie Produit,QTY,Montant HT,Taxe,Montant TTC
POL/0001,2024-11-05,SARL IMPORT COMPUTER,Local,LAP.0120,Laptop HP Probook G4,Laptop,10,1000000,190000,1190000
POL/0001,2024-11-05,SARL IMPORT COMPUTER,Local,PRI.0020,Printer Canon 6030,Imprimante,10,390000,74100,464100
POL/0001,2024-11-05,SARL IMPORT COMPUTER,Local,INK.0034,Toner Canon 6030,Consommable,20,900,171,1071
POI/0002,2024-12-16,EURL ABM,Import,LAP.0011,Laptop Lenovo 110,Laptop,500,33500000,6365000,39865000
POI/0002,2024-12-16,EURL ABM,Import,PRI.0011,Printer EPSON 3010,Imprimante,500,11500000,2185000,13685000
POI/0002,2024-12-16,EURL ABM,Import,INK.0001,INK Canon 3210,Consommable,1000,600000,114000,714000
POI/0002,2024-12-16,EURL ABM,Import,SCA.0002,Scanner Epson 1600,Scanner,200,3000000,570000,3570000
POL/0003,2025-02-11,SARL IMPORT COMPUTER,Local,LAP.0120,Laptop HP Probook G4,Laptop,5,525000,99750,624750
POL/0003,2025-02-11,SARL IMPORT COMPUTER,Local,PRI.0020,Printer Canon 6030,Imprimante,3,123000,23370,146370
POI/0004,2025-02-25,SNC Wiffak,Import,INK.0005,INK Epson 110,Consommable,1000,600000,114000,714000
"""

@st.cache_data
def load_data():
    sales = pd.read_csv(io.StringIO(SALES_DATA))
    purchases = pd.read_csv(io.StringIO(PURCHASES_DATA))
    for df in [sales, purchases]:
        df['Date.CMD'] = pd.to_datetime(df['Date.CMD'])
        df['Mois'] = df['Date.CMD'].dt.month
        df['Mois_Nom'] = df['Date.CMD'].dt.strftime('%b')
        df['Année'] = df['Date.CMD'].dt.year
    return sales, purchases

sales, purchases = load_data()

MONTH_ORDER = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
               7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}



# ─────────────────────────────────────────────
#  FILE UPLOAD (optional override)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Syne;font-size:1.1rem;font-weight:700;color:#e8ecf4;margin-bottom:.5rem">📂 Charger vos données</div>', unsafe_allow_html=True)
    f1 = st.file_uploader("Tableau Ventes (CSV/Excel)", type=["csv","xlsx"], key="f1")
    f2 = st.file_uploader("Tableau Achats (CSV/Excel)", type=["csv","xlsx"], key="f2")
    # ── helpers for uploaded files ──────────────────────────────────────
    def _parse_num(s):
        """Handle French-style numbers: '1 000 000,00' → float."""
        return (s.astype(str)
                 .str.replace(r'\s', '', regex=True)
                 .str.replace(',', '.', regex=False)
                 .pipe(pd.to_numeric, errors='coerce'))

    def _enrich_dates(df):
        df['Date.CMD'] = pd.to_datetime(df['Date.CMD'], dayfirst=True, errors='coerce')
        df['Mois']     = df['Date.CMD'].dt.month.fillna(0).astype(int)
        df['Mois_Nom'] = df['Date.CMD'].dt.strftime('%b').fillna('?')
        df['Année']    = df['Date.CMD'].dt.year.fillna(0).astype(int)
        # Drop rows where date couldn't be parsed
        df = df[df['Mois'] > 0].reset_index(drop=True)
        return df

    _TYPE_VENTE = {'SLSD':'Directe','SLSR':'Revendeur','SLSG':'Gros'}
    _CAT_MAP    = {'LAP':'Laptop','PRI':'Imprimante','INK':'Consommable','SCA':'Scanner'}
    _WILAYAS    = ['Alger','Blida','Oran','Sétif','Annaba','Constantine',
                   'Tlemcen','Béjaïa','Batna','Tizi Ouzou']

    def _enrich_sales(df):
        for c in ['Montant HT','Taxe','Montant TTC','Qté']:
            if c in df.columns: df[c] = _parse_num(df[c])
        if 'Type vente' not in df.columns:
            df['Type vente'] = df['Num.CMD'].str[:4].map(_TYPE_VENTE).fillna('Directe')
        if 'Catégorie Produit' not in df.columns:
            df['Catégorie Produit'] = df['Code Produit'].str[:3].map(_CAT_MAP).fillna('Autre')
        if 'Wilaya' not in df.columns:
            def _wil(addr):
                if pd.isna(addr): return 'Inconnue'
                for w in _WILAYAS:
                    if w.lower() in str(addr).lower(): return w
                return str(addr).split(',')[-1].strip() if ',' in str(addr) else 'Inconnue'
            df['Wilaya'] = df['Adresse'].apply(_wil)
        if 'Forme Juridique Client' not in df.columns:
            def _fj(c):
                for fj in ['SARL','EURL','SNC','SPA','EI']:
                    if str(c).startswith(fj): return fj
                return 'Autre'
            df['Forme Juridique Client'] = df['Client'].apply(_fj)
        return _enrich_dates(df)

    def _enrich_purchases(df):
        for c in ['Montant HT','Taxe','Montant TTC','QTY']:
            if c in df.columns: df[c] = _parse_num(df[c])
        if 'Catégorie Produit' not in df.columns:
            df['Catégorie Produit'] = df['Code Produit'].str[:3].map(_CAT_MAP).fillna('Autre')
        if 'Type achat' not in df.columns:
            df['Type achat'] = df['Num.CMD'].str[2].map({'L':'Local','I':'Import'}).fillna('Local')
        return _enrich_dates(df)

    if f1:
        if f1.name.endswith('.csv'):
            sales = pd.read_csv(f1, sep=',', quotechar='"', engine='python',
                                encoding='utf-8-sig', on_bad_lines='skip')
        else:
            sales = pd.read_excel(f1)
        sales = _enrich_sales(sales)
    if f2:
        if f2.name.endswith('.csv'):
            purchases = pd.read_csv(f2, sep=',', quotechar='"', engine='python',
                                    encoding='utf-8-sig', on_bad_lines='skip')
        else:
            purchases = pd.read_excel(f2)
        purchases = _enrich_purchases(purchases)
    st.markdown("---")


# ─────────────────────────────────────────────
#  PAGE TITLE
# ─────────────────────────────────────────────
st.markdown('<div class="dash-title">Business Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Tableau de bord analytique · Ventes · Achats · Marges</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 Ventes", "🛒 Achats", "📈 Marges"])


# ══════════════════════════════════════════════
#  TAB 1 — VENTES
# ══════════════════════════════════════════════
with tab1:

    # ── Sidebar filters (sales)
    with st.sidebar:
        st.markdown('<div style="font-family:Syne;font-size:1rem;font-weight:700;color:#e8ecf4;margin:.6rem 0 .3rem">Filtres — Ventes</div>', unsafe_allow_html=True)
        f_produit   = st.multiselect("Produit",             sorted(sales['Produit'].unique()),           key="s_prod")
        f_cat       = st.multiselect("Catégorie Produit",   sorted(sales['Catégorie Produit'].unique()), key="s_cat")
        f_client    = st.multiselect("Client",              sorted(sales['Client'].unique()),            key="s_cli")
        f_fjurid    = st.multiselect("Forme Juridique",     sorted(sales['Forme Juridique Client'].unique()), key="s_fj")
        f_tvente    = st.multiselect("Type vente",          sorted(sales['Type vente'].unique()),        key="s_tv")
        f_wilaya    = st.multiselect("Wilaya",              sorted(sales['Wilaya'].unique()),            key="s_wil")
        f_mois      = st.multiselect("Mois",                sorted(int(x) for x in sales['Mois'].dropna().unique()),   key="s_mois",
                                     format_func=lambda x: MONTH_ORDER.get(x, x))
        f_annee     = st.multiselect("Année",               sorted(int(x) for x in sales['Année'].dropna().unique()),             key="s_yr")
        indicator   = st.selectbox("Indicateur", ["Montant TTC","Qté"], key="s_ind")

    def apply_filters(df):
        mask = pd.Series(True, index=df.index)
        if f_produit: mask &= df['Produit'].isin(f_produit)
        if f_cat:     mask &= df['Catégorie Produit'].isin(f_cat)
        if f_client:  mask &= df['Client'].isin(f_client)
        if f_fjurid:  mask &= df['Forme Juridique Client'].isin(f_fjurid)
        if f_tvente:  mask &= df['Type vente'].isin(f_tvente)
        if f_wilaya:  mask &= df['Wilaya'].isin(f_wilaya)
        if f_mois:    mask &= df['Mois'].isin(f_mois)
        if f_annee:   mask &= df['Année'].isin(f_annee)
        return df[mask]

    fs = apply_filters(sales)

    # ── KPIs
    total_ca  = fs['Montant TTC'].sum()
    total_qty = fs['Qté'].sum()
    n_clients = fs['Client'].nunique()
    n_orders  = fs['Num.CMD'].nunique()

    k1, k2, k3, k4 = st.columns(4)
    def kpi_card(col, label, value, fmt="{:,.0f}", suffix="", color="var(--accent)"):
        col.markdown(f"""<div class="card">
            <div class="kpi-value" style="color:{color}">{fmt.format(value)}{suffix}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    kpi_card(k1, "Chiffre d'affaires (TTC)", total_ca, "{:,.0f}", " DZD", "#5b8cff")
    kpi_card(k2, "Quantités vendues", total_qty, "{:,.0f}", " unités", "#43e97b")
    kpi_card(k3, "Clients actifs", n_clients, "{:,.0f}", "", "#a855f7")
    kpi_card(k4, "Commandes", n_orders, "{:,.0f}", "", "#ffd166")

    # ── Q1: Produits vendus après 01/02/2025
    st.markdown('<div class="section-title"><span class="dot"></span>Produits vendus après le 01 Février 2025</div>', unsafe_allow_html=True)
    after_feb = sales[sales['Date.CMD'] > "2025-02-01"]['Produit'].unique()
    chips = " ".join([f'<span style="background:#2a3559;color:#a0b4ff;padding:.3rem .75rem;border-radius:20px;font-size:.8rem;margin:.2rem;display:inline-block">{p}</span>' for p in after_feb])
    st.markdown(chips, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Q2: Classement produits par CA
    st.markdown('<div class="section-title"><span class="dot"></span>Classement des produits par Chiffre d\'affaires</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])
    with col_a:
        ranking = fs.groupby(['Produit','Type vente','Année'])[indicator].sum().reset_index()
        fig = px.bar(ranking, x='Produit', y=indicator, color='Type vente',
                     barmode='group', text_auto='.3s',
                     title=f"{indicator} par Produit, Type vente & Année",
                     color_discrete_sequence=PALETTE)
        apply_theme(fig)
        fig.update_traces(textposition='outside', textfont_size=10)
        st.plotly_chart(fig, width='stretch')
    with col_b:
        prod_rank = fs.groupby('Produit')[indicator].sum().sort_values(ascending=True)
        fig2 = px.bar(prod_rank, orientation='h', text_auto='.3s',
                      title="Ranking global", color=prod_rank.values,
                      color_continuous_scale=["#1e2330","#5b8cff"])
        apply_theme(fig2)
        fig2.update_layout(coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig2, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Q3: Classement clients
    st.markdown('<div class="section-title"><span class="dot"></span>Classement des clients par Wilaya & Forme Juridique</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        client_rank = fs.groupby(['Client','Wilaya'])[indicator].sum().reset_index()
        fig3 = px.bar(client_rank, x='Client', y=indicator, color='Wilaya',
                      barmode='group', text_auto='.3s',
                      title="Clients par Wilaya",
                      color_discrete_sequence=PALETTE)
        apply_theme(fig3)
        st.plotly_chart(fig3, width='stretch')
    with c2:
        fj_rank = fs.groupby(['Client','Forme Juridique Client'])[indicator].sum().reset_index()
        fig4 = px.bar(fj_rank, x='Client', y=indicator, color='Forme Juridique Client',
                      barmode='group', text_auto='.3s',
                      title="Clients par Forme Juridique",
                      color_discrete_sequence=PALETTE)
        apply_theme(fig4)
        st.plotly_chart(fig4, width='stretch')

    # Treemap
    fig_tree = px.treemap(fs, path=['Wilaya','Forme Juridique Client','Client'],
                          values=indicator, title="Distribution Wilaya → Client",
                          color_discrete_sequence=PALETTE)
    apply_theme(fig_tree)
    st.plotly_chart(fig_tree, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Q4: Ventes quantitatives par catégorie / type / mois / année
    st.markdown('<div class="section-title"><span class="dot"></span>Ventes quantitatives — Catégorie · Type · Mois · Année</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        qty_cat = fs.groupby(['Catégorie Produit','Type vente'])['Qté'].sum().reset_index()
        fig5 = px.bar(qty_cat, x='Catégorie Produit', y='Qté', color='Type vente',
                      barmode='stack', text_auto='.2s',
                      title="Qté par Catégorie & Type vente",
                      color_discrete_sequence=PALETTE)
        apply_theme(fig5)
        st.plotly_chart(fig5, width='stretch')
    with c4:
        qty_time = fs.groupby(['Mois','Année','Catégorie Produit'])['Qté'].sum().reset_index()
        qty_time['Période'] = qty_time['Mois'].map(MONTH_ORDER) + " " + qty_time['Année'].astype(str)
        fig6 = px.line(qty_time, x='Période', y='Qté', color='Catégorie Produit',
                       markers=True, title="Évolution Qté dans le temps",
                       color_discrete_sequence=PALETTE)
        apply_theme(fig6)
        st.plotly_chart(fig6, width='stretch')

    fig7 = px.sunburst(fs, path=['Année','Mois_Nom','Catégorie Produit','Produit'],
                       values='Qté', title="Répartition Qté (Année → Catégorie → Produit)",
                       color_discrete_sequence=PALETTE)
    apply_theme(fig7)
    st.plotly_chart(fig7, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Q5: Catégorie top CA
    st.markdown('<div class="section-title"><span class="dot"></span>Top Catégorie — Chiffre d\'affaires</div>', unsafe_allow_html=True)
    cat_rank = fs.groupby('Catégorie Produit')['Montant TTC'].sum().sort_values(ascending=False)
    top_cat  = cat_rank.index[0] if len(cat_rank) else "—"
    top_val  = cat_rank.iloc[0] if len(cat_rank) else 0

    c5, c6 = st.columns([1, 3])
    with c5:
        st.markdown(f"""<div class="card" style="border-color:#5b8cff55">
            <div style="font-size:.75rem;color:#7a84a0;text-transform:uppercase;letter-spacing:.07em">🏆 Meilleure catégorie</div>
            <div style="font-family:Syne;font-size:1.5rem;font-weight:800;color:#5b8cff;margin:.4rem 0">{top_cat}</div>
            <div style="font-size:1.1rem;color:#e8ecf4;font-weight:600">{top_val:,.0f} DZD</div>
        </div>""", unsafe_allow_html=True)
    with c6:
        fig8 = px.pie(cat_rank.reset_index(), names='Catégorie Produit', values='Montant TTC',
                      hole=.55, title="Part du CA par Catégorie",
                      color_discrete_sequence=PALETTE)
        apply_theme(fig8)
        fig8.update_traces(textinfo='percent+label')
        st.plotly_chart(fig8, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Raw data (collapsible)
    with st.expander("🗃️  Données filtrées (Ventes)"):
        st.dataframe(fs.style.format({'Montant HT':'{:,.0f}','Montant TTC':'{:,.0f}','Taxe':'{:,.0f}'}),
                     width='stretch')


# ══════════════════════════════════════════════
#  TAB 2 — ACHATS
# ══════════════════════════════════════════════
with tab2:

    with st.sidebar:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Syne;font-size:1rem;font-weight:700;color:#e8ecf4;margin:.6rem 0 .3rem">Filtres — Achats</div>', unsafe_allow_html=True)
        p_produit  = st.multiselect("Produit",           sorted(purchases['Produit'].unique()),           key="p_prod")
        p_cat      = st.multiselect("Catégorie Produit", sorted(purchases['Catégorie Produit'].unique()), key="p_cat")
        p_fourn    = st.multiselect("Fournisseur",       sorted(purchases['Fournisseur'].unique()),       key="p_f")
        p_type     = st.multiselect("Type achat",        sorted(purchases['Type achat'].unique()),        key="p_t")
        p_mois     = st.multiselect("Mois",              sorted(int(x) for x in purchases['Mois'].dropna().unique()), key="p_m",
                                    format_func=lambda x: MONTH_ORDER.get(x, x))
        p_annee    = st.multiselect("Année",             sorted(int(x) for x in purchases['Année'].dropna().unique()),             key="p_yr")
        p_ind      = st.selectbox("Indicateur", ["Montant TTC","QTY"], key="p_ind")

    def apply_p_filters(df):
        mask = pd.Series(True, index=df.index)
        if p_produit: mask &= df['Produit'].isin(p_produit)
        if p_cat:     mask &= df['Catégorie Produit'].isin(p_cat)
        if p_fourn:   mask &= df['Fournisseur'].isin(p_fourn)
        if p_type:    mask &= df['Type achat'].isin(p_type)
        if p_mois:    mask &= df['Mois'].isin(p_mois)
        if p_annee:   mask &= df['Année'].isin(p_annee)
        return df[mask]

    fp = apply_p_filters(purchases)

    # KPIs
    total_cost  = fp['Montant TTC'].sum()
    total_pqty  = fp['QTY'].sum()
    n_fourn     = fp['Fournisseur'].nunique()
    n_porders   = fp['Num.CMD'].nunique()

    pk1, pk2, pk3, pk4 = st.columns(4)
    kpi_card(pk1, "Coût d'achat total (TTC)", total_cost, "{:,.0f}", " DZD", "#ff6b6b")
    kpi_card(pk2, "Quantités achetées", total_pqty, "{:,.0f}", " unités", "#43e97b")
    kpi_card(pk3, "Fournisseurs", n_fourn, "{:,.0f}", "", "#a855f7")
    kpi_card(pk4, "Commandes d'achat", n_porders, "{:,.0f}", "", "#ffd166")

    # Q1 Achats — produits achetés en 2024
    st.markdown('<div class="section-title"><span class="dot" style="background:#ff6b6b"></span>Produits achetés en 2024</div>', unsafe_allow_html=True)
    prods_2024 = purchases[purchases['Année'] == 2024]['Produit'].unique()
    chips2 = " ".join([f'<span style="background:#3a1e1e;color:#ff9f9f;padding:.3rem .75rem;border-radius:20px;font-size:.8rem;margin:.2rem;display:inline-block">{p}</span>' for p in prods_2024])
    st.markdown(chips2, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Q2: achats quantitatifs par type / mois / année
    st.markdown('<div class="section-title"><span class="dot" style="background:#ff6b6b"></span>Achats quantitatifs — Type · Mois · Année</div>', unsafe_allow_html=True)
    c1p, c2p = st.columns(2)
    with c1p:
        qty_type = fp.groupby(['Produit','Type achat'])['QTY'].sum().reset_index()
        fig_p1 = px.bar(qty_type, x='Produit', y='QTY', color='Type achat',
                        barmode='group', text_auto='.2s',
                        title="Qté par Produit & Type achat",
                        color_discrete_sequence=PALETTE)
        apply_theme(fig_p1)
        st.plotly_chart(fig_p1, width='stretch')
    with c2p:
        qty_time_p = fp.groupby(['Mois','Année','Catégorie Produit'])['QTY'].sum().reset_index()
        qty_time_p['Période'] = qty_time_p['Mois'].map(MONTH_ORDER) + " " + qty_time_p['Année'].astype(str)
        fig_p2 = px.area(qty_time_p, x='Période', y='QTY', color='Catégorie Produit',
                         title="Évolution Qté achats",
                         color_discrete_sequence=PALETTE)
        apply_theme(fig_p2)
        st.plotly_chart(fig_p2, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # Q3: fournisseur top par catégorie
    st.markdown('<div class="section-title"><span class="dot" style="background:#ff6b6b"></span>Fournisseur dominant par Catégorie</div>', unsafe_allow_html=True)
    fourn_cat = fp.groupby(['Fournisseur','Catégorie Produit'])[p_ind].sum().reset_index()
    fig_p3 = px.bar(fourn_cat, x='Catégorie Produit', y=p_ind, color='Fournisseur',
                    barmode='group', text_auto='.3s',
                    title=f"{p_ind} par Catégorie & Fournisseur",
                    color_discrete_sequence=PALETTE)
    apply_theme(fig_p3)
    st.plotly_chart(fig_p3, width='stretch')

    fig_p4 = px.sunburst(fp, path=['Fournisseur','Catégorie Produit','Produit'],
                         values=p_ind, title="Répartition Fournisseur → Catégorie → Produit",
                         color_discrete_sequence=PALETTE)
    apply_theme(fig_p4)
    st.plotly_chart(fig_p4, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # Q4: catégorie la plus coûteuse
    st.markdown('<div class="section-title"><span class="dot" style="background:#ff6b6b"></span>Catégorie la plus coûteuse</div>', unsafe_allow_html=True)
    cat_cost = fp.groupby('Catégorie Produit')['Montant TTC'].sum().sort_values(ascending=False)
    top_cat_p = cat_cost.index[0] if len(cat_cost) else "—"
    top_val_p = cat_cost.iloc[0] if len(cat_cost) else 0

    cp1, cp2 = st.columns([1, 3])
    with cp1:
        st.markdown(f"""<div class="card" style="border-color:#ff6b6b55">
            <div style="font-size:.75rem;color:#7a84a0;text-transform:uppercase;letter-spacing:.07em">💸 Catégorie la + coûteuse</div>
            <div style="font-family:Syne;font-size:1.5rem;font-weight:800;color:#ff6b6b;margin:.4rem 0">{top_cat_p}</div>
            <div style="font-size:1.1rem;color:#e8ecf4;font-weight:600">{top_val_p:,.0f} DZD</div>
        </div>""", unsafe_allow_html=True)
    with cp2:
        fig_p5 = px.pie(cat_cost.reset_index(), names='Catégorie Produit', values='Montant TTC',
                        hole=.55, title="Part du coût par Catégorie",
                        color_discrete_sequence=PALETTE)
        apply_theme(fig_p5)
        fig_p5.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_p5, width='stretch')

    with st.expander("🗃️  Données filtrées (Achats)"):
        st.dataframe(fp.style.format({'Montant HT':'{:,.0f}','Montant TTC':'{:,.0f}','Taxe':'{:,.0f}'}),
                     width='stretch')


# ══════════════════════════════════════════════
#  TAB 3 — MARGES
# ══════════════════════════════════════════════
with tab3:

    with st.sidebar:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Syne;font-size:1rem;font-weight:700;color:#e8ecf4;margin:.6rem 0 .3rem">Filtres — Marges</div>', unsafe_allow_html=True)
        m_produit = st.multiselect("Produit",           sorted(sales['Produit'].unique()),           key="m_prod")
        m_cat     = st.multiselect("Catégorie Produit", sorted(sales['Catégorie Produit'].unique()), key="m_cat")
        m_wilaya  = st.multiselect("Wilaya",            sorted(sales['Wilaya'].unique()),            key="m_wil")
        m_mois    = st.multiselect("Mois",              sorted(int(x) for x in sales['Mois'].dropna().unique()),   key="m_m",
                                   format_func=lambda x: MONTH_ORDER.get(x, x))
        m_annee   = st.multiselect("Année",             sorted(int(x) for x in sales['Année'].dropna().unique()),             key="m_yr")

    # Build merged margin table
    s_agg = sales.groupby(['Produit','Catégorie Produit','Wilaya','Mois','Année'])['Montant TTC'].sum().reset_index()
    p_agg = purchases.groupby(['Produit','Catégorie Produit','Mois','Année'])['Montant TTC'].sum().reset_index()
    p_agg_unit = purchases.groupby(['Produit'])['Montant TTC'].sum().reset_index()
    p_qty_unit = purchases.groupby(['Produit'])['QTY'].sum().reset_index()
    p_unit_cost = pd.merge(p_agg_unit, p_qty_unit, on='Produit')
    p_unit_cost['Prix unitaire achat'] = p_unit_cost['Montant TTC'] / p_unit_cost['QTY']

    s_qty = sales.groupby(['Produit','Catégorie Produit','Wilaya','Mois','Année'])[['Montant TTC','Qté']].sum().reset_index()
    s_qty['Mois_Nom'] = s_qty['Mois'].map(MONTH_ORDER)
    merged = pd.merge(s_qty, p_unit_cost[['Produit','Prix unitaire achat']], on='Produit', how='left')
    merged['Coût achat estimé'] = merged['Qté'] * merged['Prix unitaire achat']
    merged['Marge'] = merged['Montant TTC'] - merged['Coût achat estimé']
    merged['Marge %'] = (merged['Marge'] / merged['Montant TTC'] * 100).round(1)

    # Apply margin filters
    def apply_m_filters(df):
        mask = pd.Series(True, index=df.index)
        if m_produit: mask &= df['Produit'].isin(m_produit)
        if m_cat:     mask &= df['Catégorie Produit'].isin(m_cat)
        if m_wilaya:  mask &= df['Wilaya'].isin(m_wilaya)
        if m_mois:    mask &= df['Mois'].isin(m_mois)
        if m_annee:   mask &= df['Année'].isin(m_annee)
        return df[mask]

    fm = apply_m_filters(merged)

    # KPIs
    total_rev  = fm['Montant TTC'].sum()
    total_cost = fm['Coût achat estimé'].sum()
    total_marge = fm['Marge'].sum()
    avg_marge_pct = (total_marge / total_rev * 100) if total_rev else 0

    mk1, mk2, mk3, mk4 = st.columns(4)
    kpi_card(mk1, "Chiffre d'affaires", total_rev, "{:,.0f}", " DZD", "#5b8cff")
    kpi_card(mk2, "Coût d'achat estimé", total_cost, "{:,.0f}", " DZD", "#ff6b6b")
    kpi_card(mk3, "Marge brute", total_marge, "{:,.0f}", " DZD", "#43e97b")
    kpi_card(mk4, "Taux de marge", avg_marge_pct, "{:.1f}", " %", "#ffd166")

    st.markdown('<hr>', unsafe_allow_html=True)

    # Marge par produit
    st.markdown('<div class="section-title"><span class="dot" style="background:#43e97b"></span>Marge par Produit & Catégorie</div>', unsafe_allow_html=True)
    c1m, c2m = st.columns(2)
    with c1m:
        marge_prod = fm.groupby(['Produit','Catégorie Produit'])['Marge'].sum().reset_index()
        fig_m1 = px.bar(marge_prod, x='Produit', y='Marge', color='Catégorie Produit',
                        text_auto='.3s', title="Marge brute par Produit",
                        color_discrete_sequence=PALETTE)
        apply_theme(fig_m1)
        fig_m1.update_traces(textposition='outside')
        st.plotly_chart(fig_m1, width='stretch')
    with c2m:
        _mp = fm.groupby('Produit')[['Marge','Montant TTC']].sum()
        _mp['Marge %'] = (_mp['Marge'] / _mp['Montant TTC'] * 100).where(_mp['Montant TTC'] != 0, 0).round(1)
        marge_pct = _mp.reset_index()[['Produit','Marge %']].sort_values('Marge %', ascending=True)
        fig_m2 = px.bar(marge_pct, x='Marge %', y='Produit', orientation='h',
                        text_auto='.1f', title="Taux de marge % par Produit",
                        color='Marge %', color_continuous_scale=["#ff6b6b","#ffd166","#43e97b"])
        apply_theme(fig_m2)
        fig_m2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_m2, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # Marge par Wilaya
    st.markdown('<div class="section-title"><span class="dot" style="background:#43e97b"></span>Marge par Wilaya</div>', unsafe_allow_html=True)
    marge_wil = fm.groupby('Wilaya')['Marge'].sum().reset_index()
    fig_m3 = px.bar(marge_wil, x='Wilaya', y='Marge', text_auto='.3s',
                    title="Marge par Wilaya",
                    color='Marge', color_continuous_scale=["#1e2330","#43e97b"])
    apply_theme(fig_m3)
    fig_m3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_m3, width='stretch')

    st.markdown('<hr>', unsafe_allow_html=True)

    # Évolution temporelle de la marge
    st.markdown('<div class="section-title"><span class="dot" style="background:#43e97b"></span>Évolution de la marge dans le temps</div>', unsafe_allow_html=True)
    marge_time = fm.groupby(['Mois','Année'])[['Montant TTC','Coût achat estimé','Marge']].sum().reset_index()
    marge_time['Période'] = marge_time['Mois'].map(MONTH_ORDER) + " " + marge_time['Année'].astype(str)

    fig_m4 = go.Figure()
    fig_m4.add_trace(go.Bar(name="CA", x=marge_time['Période'], y=marge_time['Montant TTC'],
                            marker_color="#5b8cff", opacity=.7))
    fig_m4.add_trace(go.Bar(name="Coût achat", x=marge_time['Période'], y=marge_time['Coût achat estimé'],
                            marker_color="#ff6b6b", opacity=.7))
    fig_m4.add_trace(go.Scatter(name="Marge", x=marge_time['Période'], y=marge_time['Marge'],
                                mode='lines+markers', marker_color="#43e97b",
                                line=dict(width=3)))
    fig_m4.update_layout(barmode='group', title="CA vs Coût achat vs Marge", **CHART_LAYOUT)
    st.plotly_chart(fig_m4, width='stretch')

    # Treemap marge
    fig_m5 = px.treemap(fm[fm['Marge'] > 0], path=['Catégorie Produit','Produit','Wilaya'],
                        values='Marge', title="Répartition de la Marge",
                        color='Marge %', color_continuous_scale=["#ffd166","#43e97b"])
    apply_theme(fig_m5)
    st.plotly_chart(fig_m5, width='stretch')

    with st.expander("🗃️  Données Marges"):
        st.dataframe(fm[['Produit','Catégorie Produit','Wilaya','Mois_Nom','Année',
                          'Montant TTC','Coût achat estimé','Marge','Marge %']]
                     .style.format({'Montant TTC':'{:,.0f}','Coût achat estimé':'{:,.0f}',
                                    'Marge':'{:,.0f}','Marge %':'{:.1f}'}),
                     width='stretch')