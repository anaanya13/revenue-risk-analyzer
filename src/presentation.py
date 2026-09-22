"""Midnight & Teal styling; presentation only, with no uploaded HTML."""

import streamlit as st


def apply_theme():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp { background: radial-gradient(ellipse at 90% 0%, #164c59 0%, transparent 42%),
    radial-gradient(ellipse at 5% 30%, #19334f 0%, transparent 48%), #0b1729;
    font-family: 'DM Sans', sans-serif; }
[data-testid="stHeader"] { background: #0b1729e8; color: #edf7fa; }
[data-testid="stHeader"] button { color: #edf7fa; }
.block-container { padding-top: 4.5rem; padding-bottom: 3rem; max-width: 1500px; }
.rr-hero { color: #edf7fa; padding: 0 0 1.8rem; }
.rr-eyebrow { color: #6de2cf; font: 700 .75rem 'DM Sans', sans-serif;
    letter-spacing: .2em; text-transform: uppercase; margin-bottom: .9rem; }
.rr-hero h1 { font: 800 clamp(2rem, 4vw, 3.3rem)/1.1 'Manrope', sans-serif;
    color: #f6fbff; letter-spacing: -.045em; margin: 0 0 1rem; padding: 0; }
.rr-hero h1 span { color: #6de2cf; }
.rr-hero p { color: #c0d3df; font-size: 1.02rem; max-width: 680px; line-height: 1.7; margin: 0; }
.rr-meta { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.1rem; }
.rr-meta span { border: 1px solid #456477; border-radius: 30px; padding: .3rem .75rem;
    color: #d4e8ee; font-size: .73rem; letter-spacing: .025em; }
[data-baseweb="tab-list"] { gap: .35rem; background: #172c40; padding: .5rem;
    border-radius: 16px 16px 0 0; overflow-x: auto; }
[data-baseweb="tab"] { color: #d9e8ef; padding: .65rem 1.2rem; height: auto;
    border-radius: 9px; font-weight: 600; white-space: nowrap; }
[data-baseweb="tab"] p { font-size: .94rem; }
[data-baseweb="tab"][aria-selected="true"] { background: #e3faf3; color: #075e55; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
[data-baseweb="tab-panel"] { background: #f4f7fa; color: #172c42; padding: 1.8rem;
    border-radius: 0 0 16px 16px; box-shadow: 0 18px 45px #030d1933; }
h2, h3, h4 { font-family: 'Manrope', sans-serif; letter-spacing: -.025em; color: #172c42; }
[data-testid="stMetric"] { background: #fff; border: 1px solid #dae5ec; border-top: 3px solid #20a894;
    border-radius: 12px; padding: 1rem 1.1rem; box-shadow: 0 4px 12px #142f4507; min-height: 108px; }
[data-testid="stMetricLabel"] { color: #486276; font-weight: 500; }
[data-testid="stMetricValue"] { font-family: 'Manrope', sans-serif; font-weight: 800;
    font-size: clamp(1.35rem, 2.1vw, 2rem); color: #123d4a; letter-spacing: -.04em; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #526b7c !important; }
[data-testid="stExpander"] { background: #fff; border-radius: 10px; border-color: #dbe6ed; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-color: #dbe6ed; }
[class*="st-key-action_"] { background: #fff; border-radius: 12px; }
[data-testid="stPlotlyChart"] { background: white; padding: .55rem; border-radius: 12px; border: 1px solid #dbe6ed; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #dbe6ed; }
.stButton button, .stDownloadButton button { border-radius: 9px; font-weight: 600; min-height: 2.65rem; }
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background: #087e70; color: white; border-color: #087e70; }
[data-testid="stSidebar"] { background: #eaf1f5; border-right: 1px solid #cbdce5; }
[data-testid="stSidebar"] h3 { color: #124856; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background: #d9eee9; color: #155b51; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #fff; border-color: #ccdce5; }
.rr-badge { display: inline-block; font-size: .7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; border-radius: 30px; padding: .3rem .65rem; margin-bottom: .15rem; }
.rr-priority { background: #fce8e6; color: #9b3026; }
.rr-details { background: #e5edf9; color: #304f80; }
.rr-watch { background: #fff0d2; color: #82551a; }
.rr-info { background: #dff4ed; color: #175c49; }
@media (max-width: 700px) {
    .block-container { padding: 4rem 1rem 2rem; }
    [data-baseweb="tab-panel"] { padding: 1rem; }
    [data-baseweb="tab"] { padding: .6rem .7rem; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    .rr-hero { padding-bottom: 1.2rem; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>""", unsafe_allow_html=True)


def render_hero():
    st.markdown("""<section class="rr-hero">
<div class="rr-eyebrow">Pipeline intelligence · Revenue Risk Analyzer</div>
<h1>A clearer view of<br><span>your pipeline.</span></h1>
<p>Find the opportunities that need attention. Understand the exposure.<br>Turn your sales data into a focused plan of action.</p>
<div class="rr-meta"><span>Explainable risk rules</span><span>Traceable recommendations</span><span>Independent SQL verification</span></div>
</section>""", unsafe_allow_html=True)


def priority_badge(priority):
    # Only static labels enter HTML; source-file text remains native Streamlit text.
    styles = {"Review first": "priority", "Complete details": "details", "Watch": "watch", "Information": "info"}
    label = priority if priority in styles else "Information"
    st.markdown('<span class="rr-badge rr-{}">{}</span>'.format(styles[label], label), unsafe_allow_html=True)


def style_chart(chart):
    chart.update_layout(template="plotly_white", paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                        font={"family": "DM Sans, sans-serif", "color": "#365369", "size": 12},
                        margin={"l": 18, "r": 18, "t": 24, "b": 30}, height=350,
                        hoverlabel={"bgcolor": "#102e43", "font_color": "#ffffff"})
    chart.update_xaxes(gridcolor="#e9eff3", zerolinecolor="#dce6ed")
    chart.update_yaxes(gridcolor="#e9eff3", zerolinecolor="#dce6ed")
    chart.update_traces(marker_line_width=0, selector={"type": "bar"})
    return chart
