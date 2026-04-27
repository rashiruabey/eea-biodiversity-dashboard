"""
Europe's Biodiversity in Crisis
EEA Article 17 — Conservation Status of Habitats and Species (2013-2018)
University of Westminster — 5DATA004C Data Science Project Lifecycle
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_utils import (
    load_species_raw, load_habitats_raw, load_pressures_raw, load_bio_regions,
    filter_species, filter_habitats, filter_pressures,
    status_dist, pressure_bar_color,
    STATUS_ORDER, STATUS_COLORS, STATUS_LABELS,
    TREND_LABELS, COUNTRY_NAMES, PRESSURE_CAT_COLORS,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Europe's Biodiversity in Crisis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hero ── */
.hero-eyebrow {
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: #3498db; margin-bottom: 0.4rem;
    animation: fadeDown 0.6s ease both;
}
.hero-title {
    font-size: 2.8rem; font-weight: 700; color: #ffffff; line-height: 1.2;
    animation: fadeDown 0.75s ease both;
}
.hero-sub {
    font-size: 1.0rem; color: #8892a4; margin-top: 0.6rem; line-height: 1.65;
    animation: fadeDown 0.9s ease both;
}

/* ── Act dividers ── */
.act-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3498db; margin-top: 2.8rem;
    animation: fadeLeft 0.5s ease both;
}
.act-title {
    font-size: 1.55rem; font-weight: 600; color: #ffffff;
    padding-left: 0.85rem; border-left: 4px solid #3498db;
    margin-bottom: 0.25rem;
    animation: fadeLeft 0.6s ease both;
}
.act-sub {
    font-size: 0.9rem; color: #8892a4; padding-left: 1rem; margin-bottom: 1.1rem;
}

/* ── KPI cards ── */
.kpi-card {
    background: #1a1f2e; border: 1px solid #252d40;
    border-radius: 14px; padding: 1.25rem 1.5rem; text-align: center;
    animation: fadeUp 0.7s ease both;
}
.kpi-val   { font-size: 2.2rem; font-weight: 700; color: #ffffff; }
.kpi-lbl   { font-size: 0.76rem; color: #8892a4; text-transform: uppercase;
              letter-spacing: 0.07em; margin-top: 0.3rem; }
.kpi-delta { font-size: 0.83rem; font-weight: 500; margin-top: 0.2rem; }
.bad  { color: #e74c3c; }
.good { color: #27ae60; }
.neu  { color: #8892a4; }

/* ── Insight box ── */
.insight {
    background: #1a1f2e; border: 1px solid #252d40;
    border-radius: 8px; padding: 0.85rem 1.1rem;
    font-size: 0.875rem; color: #b0b8c8; line-height: 1.6; margin-top: 0.5rem;
}
.insight strong { color: #ffffff; }

/* ── Divider ── */
.hdivider { border: none; border-top: 1px solid #252d40; margin: 2.2rem 0; }

/* ── Hide entire top-right toolbar (Share, GitHub, edit, ⋮ menu) ── */
[data-testid="stToolbar"] { display: none !important; }
#MainMenu                  { display: none !important; }
/* ── Hide "Made with Streamlit" footer ── */
footer, [data-testid="stFooter"] { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #131720; border-right: 1px solid #252d40;
}
section[data-testid="stSidebar"] .stMarkdown p { color: #8892a4; }

/* ── Keyframes ── */
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeLeft {
    from { opacity: 0; transform: translateX(-14px); }
    to   { opacity: 1; transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)


# ── CACHED LOADERS ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_species():    return load_species_raw()

@st.cache_data(show_spinner=False)
def get_habitats():  return load_habitats_raw()

@st.cache_data(show_spinner=False)
def get_pressures(): return load_pressures_raw()

@st.cache_data(show_spinner=False)
def get_bio():       return load_bio_regions()


# ── CHART THEME ───────────────────────────────────────────────────────────────
_BG   = "#1a1f2e"
_GRID = "#252d40"
_FONT = "#b0b8c8"

def theme(fig, height=420, legend=True, title_text=""):
    cfg = dict(
        paper_bgcolor=_BG, plot_bgcolor=_BG,
        font=dict(color=_FONT, family="Inter", size=12),
        height=height,
        margin=dict(l=8, r=8, t=44 if title_text else 12, b=8),
        transition_duration=450,
    )
    if title_text:
        cfg["title"] = dict(text=title_text, font=dict(size=13, color="#ffffff"), x=0.01)
    if legend:
        cfg["legend"] = dict(bgcolor=_BG, bordercolor=_GRID, borderwidth=1,
                             font=dict(size=11))
    else:
        cfg["showlegend"] = False
    fig.update_layout(**cfg)
    fig.update_xaxes(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=_GRID)
    fig.update_yaxes(gridcolor=_GRID, zerolinecolor=_GRID, linecolor=_GRID)
    return fig


def kpi(val, lbl, delta="", delta_cls="neu"):
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-val">{val}</div>'
        f'<div class="kpi-lbl">{lbl}</div>'
        f'<div class="kpi-delta {delta_cls}">{delta}</div>'
        f"</div>"
    )


def act(label, title, sub=""):
    st.markdown(f'<div class="act-label">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="act-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="act-sub">{sub}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="hdivider">', unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Loading dataset — please wait..."):
    sp_raw  = get_species()
    hab_raw = get_habitats()
    pt_raw  = get_pressures()
    bio_map = get_bio()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Dashboard Filters")
    st.markdown("Selections apply across all charts.")
    st.markdown("---")

    all_countries = sorted(sp_raw["country"].unique())
    sel_countries = st.multiselect(
        "Country",
        options=all_countries,
        format_func=lambda c: f"{COUNTRY_NAMES.get(c, c)} ({c})",
        placeholder="All 28 EU countries",
    )

    all_groups = sorted(sp_raw["group"].dropna().unique())
    sel_groups = st.multiselect(
        "Species Group",
        options=all_groups,
        placeholder="All taxonomic groups",
    )

    all_regions = sorted(sp_raw["region"].unique())
    sel_regions = st.multiselect(
        "Biogeographic Region",
        options=all_regions,
        format_func=lambda r: bio_map.get(r, r),
        placeholder="All 14 regions",
    )

    sel_statuses = st.multiselect(
        "Assessment Status",
        options=STATUS_ORDER,
        format_func=lambda s: STATUS_LABELS.get(s, s),
        placeholder="All statuses",
    )

    st.markdown("---")
    st.markdown("**Pressures & Threats Panel**")

    feat_type = st.radio(
        "Feature type", ["Both", "Species", "Habitats"], horizontal=True
    )
    ptype = st.radio(
        "Pressure or threat", ["Both", "Pressures", "Threats"], horizontal=True
    )
    ranking_sel = st.multiselect(
        "Ranking",
        options=["H", "M", "L"],
        default=["H"],
        format_func=lambda r: {"H": "High", "M": "Medium", "L": "Low"}[r],
    )

    st.markdown("---")
    st.caption(
        "Source: European Environment Agency  \n"
        "EEA Article 17 — Habitats Directive 92/43/EEC  \n"
        "Reporting period: 2013–2018"
    )


# ── APPLY GLOBAL FILTERS ──────────────────────────────────────────────────────
sp  = filter_species(sp_raw,  sel_countries, sel_groups,  sel_regions, sel_statuses)
hab = filter_habitats(hab_raw, sel_countries, sel_regions, sel_statuses)
pt  = filter_pressures(pt_raw, sel_countries, sel_regions, feat_type, ranking_sel, ptype)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-eyebrow">European Environment Agency — Article 17 Conservation Assessment</div>
<div class="hero-title">Europe's Biodiversity in Crisis</div>
<div class="hero-sub">
An interactive analysis of conservation status across 28 EU Member States — covering
1,383 species and 233 habitat types across 14 biogeographic regions.
Data from the 2013–2018 Habitats Directive reporting period.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPI row
n_sp       = len(sp)
n_hab      = len(hab)
n_unfav_sp = len(sp[sp["conclusion_assessment"].isin(["U1", "U2"])])
n_unfav_h  = len(hab[hab["conclusion_assessment"].isin(["U1", "U2"])])
pct_sp     = f"{100 * n_unfav_sp / n_sp:.0f}%" if n_sp else "—"
pct_h      = f"{100 * n_unfav_h  / n_hab:.0f}%" if n_hab else "—"
n_countries = sp["country"].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi(f"{n_sp:,}",  "Species Assessments",
                    f"{len(sp[sp['conclusion_assessment']=='U2']):,} in Bad status", "bad"),
                unsafe_allow_html=True)
with c2:
    st.markdown(kpi(pct_sp, "Species Unfavourable",
                    "U1 (Inadequate) + U2 (Bad)", "bad"),
                unsafe_allow_html=True)
with c3:
    st.markdown(kpi(f"{n_hab:,}", "Habitat Assessments",
                    f"{pct_h} unfavourable", "bad"),
                unsafe_allow_html=True)
with c4:
    st.markdown(kpi(str(n_countries), "Countries Reporting",
                    "All EU Member States", "good"),
                unsafe_allow_html=True)

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT I — OVERALL STATUS DISTRIBUTION
# ─────────────────────────────────────────────────────────────────────────────
act("Act I", "The State of Nature",
    "How are Europe's species and habitats assessed overall? "
    "Each assessment represents one species or habitat type in one country and biogeographic region.")

if n_sp == 0 or n_hab == 0:
    st.warning("No data matches the current filters. Adjust the sidebar selections.")
else:
    col_l, col_r = st.columns(2)

    def donut(df, title, total):
        sd = status_dist(df)
        fig = go.Figure(go.Pie(
            labels=sd["label"],
            values=sd["count"],
            marker_colors=sd["color"],
            hole=0.58,
            textinfo="percent",
            textfont=dict(size=12, color="#ffffff"),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            pull=[0.02, 0.02, 0.04, 0.02],
            sort=False,
            direction="clockwise",
        ))
        fig.add_annotation(
            text=f"<b>{total:,}</b><br><span style='font-size:10px;color:#8892a4'>assessments</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=17, color="#ffffff"),
        )
        return theme(fig, height=370, title_text=title)

    with col_l:
        st.plotly_chart(donut(sp, "Species Status Distribution", n_sp),
                        width='stretch')
    with col_r:
        st.plotly_chart(donut(hab, "Habitats Status Distribution", n_hab),
                        width='stretch')

    sp_fv_pct  = 100 * len(sp[sp["conclusion_assessment"] == "FV"])  / n_sp
    hab_fv_pct = 100 * len(hab[hab["conclusion_assessment"] == "FV"]) / n_hab
    insight(
        f"<strong>Key finding:</strong> Only <strong>{sp_fv_pct:.0f}%</strong> of species assessments "
        f"and <strong>{hab_fv_pct:.0f}%</strong> of habitat assessments reach Favourable status. "
        f"Habitats are in worse condition than species — a pattern consistent across most EU countries. "
        f"The U2 (Unfavourable — Bad) category represents species and habitats in active decline "
        f"with no realistic short-term recovery prospect."
    )

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT II — COUNTRY RANKING
# ─────────────────────────────────────────────────────────────────────────────
act("Act II", "Where Is It Worst?",
    "Countries ranked by the proportion of species assessments with unfavourable status (U1 + U2). "
    "Hover over each bar segment for exact figures.")

if n_sp > 0:
    grp = (
        sp.groupby(["country", "country_name", "conclusion_assessment"])
        .size().reset_index(name="count")
    )
    totals = grp.groupby("country")["count"].sum().reset_index(name="total")
    grp    = grp.merge(totals, on="country")
    grp["pct"] = 100 * grp["count"] / grp["total"]

    unfav_pct = (
        grp[grp["conclusion_assessment"].isin(["U1", "U2"])]
        .groupby("country_name")["pct"].sum()
        .sort_values(ascending=True)
    )
    order = unfav_pct.index.tolist()

    cpiv = (
        grp.pivot_table(index="country_name", columns="conclusion_assessment",
                        values="pct", fill_value=0)
        .reindex(columns=STATUS_ORDER, fill_value=0)
        .reset_index()
    )
    cpiv = cpiv.set_index("country_name").reindex(order).reset_index()

    fig2 = go.Figure()
    for s in STATUS_ORDER:
        if s in cpiv.columns:
            fig2.add_trace(go.Bar(
                name=STATUS_LABELS[s],
                x=cpiv[s],
                y=cpiv["country_name"],
                orientation="h",
                marker_color=STATUS_COLORS[s],
                text=[f"{v:.0f}%" if v > 4 else "" for v in cpiv[s]],
                textposition="inside",
                textfont=dict(size=9, color="#ffffff"),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    + STATUS_LABELS[s]
                    + ": %{x:.1f}%<extra></extra>"
                ),
            ))
    fig2.update_layout(
        barmode="stack",
        xaxis=dict(range=[0, 100], ticksuffix="%", title="% of National Assessments"),
        yaxis_title="",
    )
    theme(fig2, height=700, title_text="Species Assessment Status by Country (% of national total)")
    st.plotly_chart(fig2, width='stretch')

    worst_name = unfav_pct.index[-1]
    best_name  = unfav_pct.index[0]
    worst_val  = unfav_pct.iloc[-1]
    best_val   = unfav_pct.iloc[0]
    insight(
        f"<strong>Range:</strong> {worst_name} has the highest proportion of unfavourable species "
        f"assessments ({worst_val:.0f}%), while {best_name} has the lowest ({best_val:.0f}%). "
        f"Countries with large, ecologically diverse territories tend to report more assessments but "
        f"also accumulate more unfavourable results — reflecting both genuine biodiversity stress and "
        f"reporting thoroughness."
    )

    # ── Europe choropleth map ──────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.82rem;color:#8892a4;margin:1.2rem 0 0.3rem;">'
        '▸ Geographic view — hover over any country for full details</p>',
        unsafe_allow_html=True,
    )

    _ISO2_TO_ISO3 = {
        "AT":"AUT","BE":"BEL","BG":"BGR","CY":"CYP","CZ":"CZE",
        "DE":"DEU","DK":"DNK","EE":"EST","ES":"ESP","FI":"FIN",
        "FR":"FRA","GR":"GRC","HR":"HRV","HU":"HUN","IE":"IRL",
        "IT":"ITA","LT":"LTU","LU":"LUX","LV":"LVA","MT":"MLT",
        "NL":"NLD","PL":"POL","PT":"PRT","RO":"ROU","SE":"SWE",
        "SI":"SVN","SK":"SVK","UK":"GBR",
    }

    _totals  = sp.groupby("country").size().rename("total")
    _unfav   = sp[sp["conclusion_assessment"].isin(["U1","U2"])].groupby("country").size().rename("unfav")
    _bad     = sp[sp["conclusion_assessment"] == "U2"].groupby("country").size().rename("bad")
    map_df   = pd.concat([_totals, _unfav, _bad], axis=1).fillna(0).reset_index()
    map_df.columns = ["country", "total", "unfav", "bad"]
    map_df["pct_unfav"]    = (100 * map_df["unfav"] / map_df["total"]).round(1)
    map_df["country_name"] = map_df["country"].map(COUNTRY_NAMES).fillna(map_df["country"])
    map_df["iso3"]         = map_df["country"].map(_ISO2_TO_ISO3)

    fig_map = px.choropleth(
        map_df,
        locations="iso3",
        locationmode="ISO-3",
        color="pct_unfav",
        scope="europe",
        color_continuous_scale=["#27ae60", "#f39c12", "#c0392b"],
        range_color=[0, 100],
        hover_name="country_name",
        hover_data={
            "pct_unfav": ":.1f",
            "total": ":,",
            "unfav": ":,",
            "bad": ":,",
            "iso3": False,
            "country": False,
        },
        labels={
            "pct_unfav": "% Unfavourable",
            "total": "Total assessments",
            "unfav": "Unfavourable (U1+U2)",
            "bad": "Bad status (U2)",
        },
    )
    fig_map.update_geos(
        bgcolor="#1a1f2e",
        lakecolor="#1a1f2e",
        landcolor="#252d40",
        oceancolor="#131720",
        showocean=True,
        showlakes=True,
        showcoastlines=True,
        coastlinecolor="#3d4460",
        showframe=False,
        showcountries=True,
        countrycolor="#3d4460",
        resolution=50,
    )
    fig_map.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="%<br>Unfav", font=dict(color="#b0b8c8")),
            ticksuffix="%",
            len=0.65,
            thickness=14,
            bgcolor="#1a1f2e",
            bordercolor="#252d40",
            borderwidth=1,
            tickfont=dict(color="#b0b8c8"),
        ),
    )
    theme(fig_map, height=540, legend=False,
          title_text="% Unfavourable Species Assessments — EU Member States")
    st.plotly_chart(fig_map, width='stretch')

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT III — SPECIES GROUPS
# ─────────────────────────────────────────────────────────────────────────────
act("Act III", "Which Groups Are Suffering?",
    "Assessment breakdown across nine taxonomic groups covered by the Habitats Directive.")

if n_sp > 0:
    sort_by = st.radio("Sort by", ["Total assessments", "% Unfavourable"],
                       horizontal=True, key="grp_sort")

    grp_cnt = (
        sp.groupby(["group", "conclusion_assessment"])
        .size().reset_index(name="count")
    )
    grp_tot = grp_cnt.groupby("group")["count"].sum().reset_index(name="total")
    grp_unf = (
        grp_cnt[grp_cnt["conclusion_assessment"].isin(["U1", "U2"])]
        .groupby("group")["count"].sum().reset_index(name="unfav")
    )
    grp_meta = grp_tot.merge(grp_unf, on="group", how="left").fillna(0)
    grp_meta["pct_unfav"] = 100 * grp_meta["unfav"] / grp_meta["total"]

    order3 = (
        grp_meta.sort_values("total", ascending=False)["group"].tolist()
        if sort_by == "Total assessments"
        else grp_meta.sort_values("pct_unfav", ascending=False)["group"].tolist()
    )

    gpiv = (
        grp_cnt.pivot_table(index="group", columns="conclusion_assessment",
                            values="count", fill_value=0)
        .reindex(columns=STATUS_ORDER, fill_value=0)
        .reset_index()
    )
    gpiv = gpiv.set_index("group").reindex(order3).reset_index()

    col3a, col3b = st.columns([3, 2])

    with col3a:
        fig3a = go.Figure()
        for s in STATUS_ORDER:
            if s in gpiv.columns:
                fig3a.add_trace(go.Bar(
                    name=STATUS_LABELS[s],
                    x=gpiv["group"],
                    y=gpiv[s],
                    marker_color=STATUS_COLORS[s],
                    hovertemplate="<b>%{x}</b><br>" + STATUS_LABELS[s] + ": %{y}<extra></extra>",
                ))
        fig3a.update_layout(
            barmode="stack",
            xaxis=dict(title="", tickangle=-30),
            yaxis_title="Number of Assessments",
        )
        theme(fig3a, height=400, title_text="Assessments by Taxonomic Group")
        st.plotly_chart(fig3a, width='stretch')

    with col3b:
        meta_sorted = grp_meta.set_index("group").reindex(order3).reset_index()
        bar_colors3 = [
            "#e74c3c" if v >= 60 else "#f39c12" if v >= 40 else "#27ae60"
            for v in meta_sorted["pct_unfav"]
        ]
        fig3b = go.Figure(go.Bar(
            y=meta_sorted["group"],
            x=meta_sorted["pct_unfav"],
            orientation="h",
            marker_color=bar_colors3,
            text=[f"{v:.0f}%" for v in meta_sorted["pct_unfav"]],
            textposition="outside",
            textfont=dict(color="#ffffff", size=11),
            hovertemplate="<b>%{y}</b><br>% Unfavourable: %{x:.1f}%<extra></extra>",
        ))
        fig3b.update_layout(
            xaxis=dict(range=[0, 108], ticksuffix="%", title="% Unfavourable"),
            yaxis_title="",
        )
        theme(fig3b, height=400, legend=False,
              title_text="% Unfavourable per Group")
        st.plotly_chart(fig3b, width='stretch')

    worst_grp = grp_meta.sort_values("pct_unfav", ascending=False).iloc[0]
    insight(
        f"<strong>{worst_grp['group']}</strong> have the highest proportion of unfavourable "
        f"assessments at <strong>{worst_grp['pct_unfav']:.0f}%</strong>. "
        f"Mammals follow a pattern of widespread but fragmented populations, "
        f"making them sensitive to habitat fragmentation and hydrological changes. "
        f"Vascular plants represent the largest volume of assessments, reflecting the "
        f"diversity of plant species listed under the Habitats Directive."
    )

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT IV — TREND COMPARISON (2007-2012 vs 2013-2018)
# ─────────────────────────────────────────────────────────────────────────────
act("Act IV", "Are Things Getting Better or Worse?",
    "Direct comparison of conservation status between the previous (2007–2012) "
    "and current (2013–2018) reporting periods. Annotations show the absolute change.")

comp_tab = st.radio("Dataset", ["Species", "Habitats"], horizontal=True, key="comp_tab")
comp_df  = sp if comp_tab == "Species" else hab
n_comp   = len(comp_df)

if n_comp > 0:
    prev_c = comp_df["conclusion_assessment_prev"].value_counts().reindex(STATUS_ORDER, fill_value=0)
    curr_c = comp_df["conclusion_assessment"].value_counts().reindex(STATUS_ORDER, fill_value=0)

    labels4 = [STATUS_LABELS[s] for s in STATUS_ORDER]

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        name="2007–2012 (Previous period)",
        x=labels4,
        y=prev_c.values,
        marker_color=["#1a6b3a", "#8a5a00", "#7a1a0a", "#3d4450"],
        opacity=0.65,
        hovertemplate="<b>%{x}</b><br>2007–2012: %{y:,}<extra></extra>",
    ))
    fig4.add_trace(go.Bar(
        name="2013–2018 (Current period)",
        x=labels4,
        y=curr_c.values,
        marker_color=[STATUS_COLORS[s] for s in STATUS_ORDER],
        hovertemplate="<b>%{x}</b><br>2013–2018: %{y:,}<extra></extra>",
    ))

    for i, s in enumerate(STATUS_ORDER):
        delta = int(curr_c[s]) - int(prev_c[s])
        sign  = "+" if delta >= 0 else ""
        is_bad = (s in ["U1", "U2"] and delta > 0) or (s == "FV" and delta < 0)
        color  = "#e74c3c" if is_bad else "#27ae60"
        fig4.add_annotation(
            x=STATUS_LABELS[s],
            y=max(int(curr_c[s]), int(prev_c[s])) + max(30, n_comp * 0.015),
            text=f"<b>{sign}{delta:,}</b>",
            showarrow=False,
            font=dict(size=12, color=color),
        )

    fig4.update_layout(
        barmode="group",
        xaxis_title="",
        yaxis_title="Number of Assessments",
    )
    theme(fig4, height=420,
          title_text=f"{comp_tab} Status: 2007–2012 vs 2013–2018")
    st.plotly_chart(fig4, width='stretch')

    # Current-period trend direction
    trend_c = (
        comp_df["conclusion_assessment_trend"]
        .map(TREND_LABELS)
        .value_counts()
        .reset_index()
    )
    trend_c.columns = ["trend", "count"]
    trend_colors4 = {
        "Improving": "#27ae60", "Stable": "#3498db",
        "Declining": "#e74c3c", "Unknown": "#7f8c8d", "Uncertain": "#f39c12",
    }
    fig4b = go.Figure(go.Bar(
        x=trend_c["trend"],
        y=trend_c["count"],
        marker_color=[trend_colors4.get(t, "#95a5a6") for t in trend_c["trend"]],
        text=trend_c["count"],
        textposition="outside",
        textfont=dict(color="#ffffff"),
        hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>",
    ))
    fig4b.update_layout(
        xaxis=dict(categoryorder="total descending", title=""),
        yaxis_title="Assessments",
    )
    theme(fig4b, height=330, legend=False,
          title_text="Current Period Trend Direction")
    st.plotly_chart(fig4b, width='stretch')

    delta_u2 = int(curr_c["U2"]) - int(prev_c["U2"])
    delta_fv = int(curr_c["FV"]) - int(prev_c["FV"])
    insight(
        f"<strong>The picture is mixed but concerning:</strong> "
        f"The number of assessments in the worst category (U2 — Unfavourable Bad) has increased by "
        f"<strong>{'+' if delta_u2 >= 0 else ''}{delta_u2:,}</strong> since the previous period. "
        f"Favourable assessments changed by "
        f"<strong>{'+' if delta_fv >= 0 else ''}{delta_fv:,}</strong>. "
        f"Many species that were previously Unknown (XX) have now been assessed, "
        f"which partially explains shifts between categories."
    )

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT V — BIOGEOGRAPHIC REGIONS
# ─────────────────────────────────────────────────────────────────────────────
act("Act V", "A Regional Portrait",
    "Europe's 14 biogeographic regions span from the Arctic Boreal north to the "
    "Mediterranean south. Conservation pressures differ sharply across this gradient.")

reg_tab = st.radio("Show", ["Species", "Habitats"], horizontal=True, key="reg_tab")
reg_df  = sp if reg_tab == "Species" else hab
n_reg   = len(reg_df)

if n_reg > 0:
    reg_df = reg_df.copy()
    reg_df["region_name"] = reg_df["region"].map(bio_map)

    rg = (
        reg_df.groupby(["region_name", "conclusion_assessment"])
        .size().reset_index(name="count")
    )
    reg_totals = rg.groupby("region_name")["count"].sum()
    reg_order  = reg_totals.sort_values(ascending=False).index.tolist()

    rpiv = (
        rg.pivot_table(index="region_name", columns="conclusion_assessment",
                       values="count", fill_value=0)
        .reindex(columns=STATUS_ORDER, fill_value=0)
        .reset_index()
    )
    rpiv = rpiv.set_index("region_name").reindex(reg_order).reset_index()

    fig5 = go.Figure()
    for s in STATUS_ORDER:
        if s in rpiv.columns:
            fig5.add_trace(go.Bar(
                name=STATUS_LABELS[s],
                x=rpiv["region_name"],
                y=rpiv[s],
                marker_color=STATUS_COLORS[s],
                hovertemplate="<b>%{x}</b><br>" + STATUS_LABELS[s] + ": %{y:,}<extra></extra>",
            ))
    fig5.update_layout(
        barmode="stack",
        xaxis=dict(title="", tickangle=-35),
        yaxis_title="Number of Assessments",
    )
    theme(fig5, height=420,
          title_text=f"{reg_tab} Assessments by Biogeographic Region")
    st.plotly_chart(fig5, width='stretch')

    # % unfavourable by region
    reg_unfav = (
        rg[rg["conclusion_assessment"].isin(["U1", "U2"])]
        .groupby("region_name")["count"].sum()
        / reg_totals * 100
    ).sort_values(ascending=True)

    fig5b = go.Figure(go.Bar(
        y=reg_unfav.index,
        x=reg_unfav.values,
        orientation="h",
        marker_color=[
            "#e74c3c" if v >= 65 else "#f39c12" if v >= 45 else "#27ae60"
            for v in reg_unfav.values
        ],
        text=[f"{v:.0f}%" for v in reg_unfav.values],
        textposition="outside",
        textfont=dict(color="#ffffff"),
        hovertemplate="<b>%{y}</b><br>% Unfavourable: %{x:.1f}%<extra></extra>",
    ))
    fig5b.update_layout(
        xaxis=dict(range=[0, 108], ticksuffix="%", title="% Unfavourable (U1 + U2)"),
        yaxis_title="",
    )
    theme(fig5b, height=380, legend=False,
          title_text="% Unfavourable by Biogeographic Region")
    st.plotly_chart(fig5b, width='stretch')

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT VI — PRESSURES & THREATS
# ─────────────────────────────────────────────────────────────────────────────
act("Act VI", "What Is Driving the Crisis?",
    "The most frequently reported pressures and threats ranked by number of reports. "
    "Colors indicate the broad category of the pressure (Agriculture, Forestry, Infrastructure, etc.).")

n_top = st.slider("Number of pressures/threats to display", 5, 30, 15, key="n_top")

n_pt = len(pt)
if n_pt == 0:
    st.warning("No pressure/threat records match the current filters.")
else:
    pt_agg = (
        pt.groupby(["pressurecode", "label"])
        .size().reset_index(name="count")
        .sort_values("count", ascending=True)
        .tail(n_top)
    )
    pt_agg["label_trunc"] = pt_agg["label"].str.slice(0, 60).str.strip()
    pt_agg["label_trunc"] = pt_agg["label_trunc"] + pt_agg["label"].apply(
        lambda x: "…" if len(str(x)) > 60 else ""
    )
    bar_clrs = [pressure_bar_color(c) for c in pt_agg["pressurecode"]]

    fig6 = go.Figure(go.Bar(
        y=pt_agg["label_trunc"],
        x=pt_agg["count"],
        orientation="h",
        marker_color=bar_clrs,
        text=pt_agg["count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color="#ffffff", size=10),
        customdata=pt_agg[["label", "pressurecode"]].values,
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "%{customdata[0]}<br>"
            "Reports: %{x:,}<extra></extra>"
        ),
    ))
    fig6.update_layout(
        xaxis=dict(
            title="Number of Reports",
            range=[0, pt_agg["count"].max() * 1.22],
        ),
        yaxis=dict(automargin=True, title=""),
    )
    theme(fig6, height=max(360, n_top * 30), legend=False,
          title_text=f"Top {n_top} Reported Pressures / Threats")
    st.plotly_chart(fig6, width='stretch')

    top_p = pt_agg.iloc[-1]
    insight(
        f"<strong>Category legend:</strong> "
        f'<span style="color:#e67e22">■ Agriculture</span> &nbsp; '
        f'<span style="color:#27ae60">■ Forestry</span> &nbsp; '
        f'<span style="color:#2980b9">■ Infrastructure / Transport</span> &nbsp; '
        f'<span style="color:#e74c3c">■ Invasive species</span> &nbsp; '
        f'<span style="color:#3498db">■ Hydrological / Climate change</span> &nbsp; '
        f'<span style="color:#16a085">■ Human intrusion</span><br><br>'
        f"<strong>Most reported:</strong> <em>{top_p['label']}</em> "
        f"({top_p['count']:,} reports). Grassland abandonment and natural succession "
        f"dominate because the Habitats Directive protects many semi-natural habitats "
        f"that depend on traditional land management to remain in good condition."
    )

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT VII — POPULATION vs RANGE TREND (bubble chart)
# ─────────────────────────────────────────────────────────────────────────────
act("Act VII", "Population vs Range Trends",
    "Each bubble shows how many species assessments share the same combination of "
    "population trend and range trend. Bubble size = number of assessments. "
    "Color = conservation status.")

if n_sp > 0:
    valid_trends = set(TREND_LABELS.keys())
    sc = sp[sp["population_trend"].isin(valid_trends) &
            sp["range_trend"].isin(valid_trends)].copy()
    sc["pop_lbl"]   = sc["population_trend"].map(TREND_LABELS)
    sc["range_lbl"] = sc["range_trend"].map(TREND_LABELS)

    grp7 = st.multiselect(
        "Filter by species group (optional)",
        options=sorted(sc["group"].dropna().unique()),
        placeholder="All groups",
        key="sc_grp",
    )
    if grp7:
        sc = sc[sc["group"].isin(grp7)]

    sc_agg = (
        sc.groupby(["range_lbl", "pop_lbl", "conclusion_assessment"])
        .size().reset_index(name="count")
    )
    sc_agg["status_label"] = sc_agg["conclusion_assessment"].map(STATUS_LABELS)

    trend_order7 = ["Declining", "Unknown", "Uncertain", "Stable", "Improving"]

    fig7 = px.scatter(
        sc_agg,
        x="range_lbl",
        y="pop_lbl",
        size="count",
        color="conclusion_assessment",
        color_discrete_map=STATUS_COLORS,
        size_max=55,
        opacity=0.82,
        labels={
            "range_lbl": "Range Trend",
            "pop_lbl": "Population Trend",
            "conclusion_assessment": "Status",
            "count": "Assessments",
        },
        hover_data={
            "count": True,
            "status_label": True,
            "conclusion_assessment": False,
        },
        category_orders={
            "range_lbl": trend_order7,
            "pop_lbl":   trend_order7,
            "conclusion_assessment": STATUS_ORDER,
        },
        title="Population Trend vs Range Trend — Bubble Size = Assessments",
    )
    fig7.update_traces(marker=dict(line=dict(width=0.5, color="#0e1117")))
    fig7.add_annotation(
        x="Declining", y="Declining",
        text="Critical zone", showarrow=False,
        font=dict(size=10, color="#e74c3c"), opacity=0.6,
        yshift=40,
    )
    fig7.add_annotation(
        x="Improving", y="Improving",
        text="Recovery zone", showarrow=False,
        font=dict(size=10, color="#27ae60"), opacity=0.6,
        yshift=40,
    )
    fig7.update_layout(title_font_color="#ffffff")
    theme(fig7, height=480)
    st.plotly_chart(fig7, width='stretch')

    insight(
        "<strong>Reading the chart:</strong> Bubbles toward the bottom-left "
        "(Declining / Declining) represent species where both population size and "
        "geographic range are contracting simultaneously — the most precarious situation. "
        "The largest red (U2) bubbles reveal where the biodiversity crisis is most acute. "
        "Bubbles on the diagonal from bottom-left to top-right follow the expected "
        "covariance: range and population usually trend together."
    )

divider()


# ─────────────────────────────────────────────────────────────────────────────
# ACT VIII — DATA EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
act("Act VIII", "Explore the Data",
    "Full filtered dataset. All sidebar filters apply. Download as CSV for offline analysis.")

tbl_mode = st.radio("Dataset to explore", ["Species", "Habitats"],
                    horizontal=True, key="tbl_mode")

if tbl_mode == "Species" and n_sp > 0:
    tbl = sp[[
        "country_name", "region", "speciesname", "group",
        "conclusion_assessment", "conclusion_assessment_trend",
        "conclusion_assessment_prev", "population_trend", "range_trend",
    ]].copy()
    tbl.columns = [
        "Country", "Region", "Species", "Group",
        "Status (2013–2018)", "Trend (Current)",
        "Status (2007–2012)", "Population Trend", "Range Trend",
    ]
elif tbl_mode == "Habitats" and n_hab > 0:
    tbl = hab[[
        "country_name", "region", "habitatcode",
        "conclusion_assessment", "conclusion_assessment_trend",
        "conclusion_assessment_prev", "coverage_trend",
    ]].copy()
    tbl.columns = [
        "Country", "Region", "Habitat Code",
        "Status (2013–2018)", "Trend (Current)",
        "Status (2007–2012)", "Coverage Trend",
    ]
else:
    tbl = pd.DataFrame()

if not tbl.empty:
    tbl["Region"] = tbl["Region"].map(bio_map).fillna(tbl["Region"])
    for col in ["Status (2013–2018)", "Status (2007–2012)"]:
        if col in tbl.columns:
            tbl[col] = tbl[col].map(STATUS_LABELS).fillna(tbl[col])
    for col in ["Trend (Current)", "Population Trend", "Range Trend", "Coverage Trend"]:
        if col in tbl.columns:
            tbl[col] = tbl[col].map(TREND_LABELS).fillna(tbl[col])

    display_tbl = tbl.reset_index(drop=True)
    st.markdown(
        """
        <style>
        .data-tbl { width:100%; border-collapse:collapse; font-size:0.82rem;
                    font-family:'Inter',sans-serif; }
        .data-tbl th { background:#252d40; color:#b0b8c8; padding:8px 10px;
                       text-align:left; border-bottom:2px solid #3498db;
                       text-transform:uppercase; letter-spacing:0.04em; font-size:0.72rem; }
        .data-tbl td { padding:7px 10px; border-bottom:1px solid #252d40; color:#d0d8e8; }
        .data-tbl tr:hover td { background:#1f2638; }
        .tbl-wrap { max-height:420px; overflow-y:auto; border:1px solid #252d40;
                    border-radius:8px; background:#1a1f2e; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    html_tbl = display_tbl.to_html(index=False, classes="data-tbl", border=0)
    st.markdown(f'<div class="tbl-wrap">{html_tbl}</div>', unsafe_allow_html=True)
    st.caption(f"Showing {len(display_tbl):,} rows")

    st.download_button(
        label="Download filtered data as CSV",
        data=tbl.to_csv(index=False).encode("utf-8"),
        file_name="eea_art17_filtered.csv",
        mime="text/csv",
    )
else:
    st.info("No records to display for the current filter selection.")

divider()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center;color:#3d4450;font-size:0.8rem;'>"
    "Data: European Environment Agency — Article 17, Habitats Directive 92/43/EEC, "
    "2013–2018 reporting period. "
    "Dashboard developed for University of Westminster 5DATA004C, April 2026."
    "</p>",
    unsafe_allow_html=True,
)
