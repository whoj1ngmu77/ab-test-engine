import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
import plotly.graph_objects as go

st.set_page_config(page_title="AB Test Engine", layout="wide", page_icon="⚡")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #030d0a; color: #e2f0eb; }
.stApp { background: linear-gradient(135deg, #030d0a 0%, #071a10 30%, #0a1628 60%, #060f1a 100%); }
.stApp > header { display: none; }
div[data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 1.5rem 2.5rem 1.5rem 2.5rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #030d0a !important; border-right: 1px solid #0d2a1a; }
section[data-testid="stSidebar"] .block-container { padding: 0.5rem 1rem !important; }

.metric-card { background: linear-gradient(135deg, #071510 0%, #0a1e14 100%); border: 1px solid #0d2a1a; border-radius: 16px; padding: 1.2rem 1.4rem; position: relative; overflow: hidden; }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00c97a, #00a8e0, #7c5cbf); border-radius: 16px 16px 0 0; }
.metric-label { font-size: 11px; font-weight: 500; color: #3a6050; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.metric-value { font-size: 24px; font-weight: 700; color: #e2f0eb; line-height: 1; margin-bottom: 4px; }
.metric-sub { font-size: 11px; color: #3a6050; }

.card { background: linear-gradient(135deg, #071510 0%, #0a1e14 100%); border: 1px solid #0d2a1a; border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }
.card-title { font-size: 13px; font-weight: 600; color: #00c97a; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
.card-title span { font-size: 11px; color: #3a6050; text-transform: none; letter-spacing: 0; font-weight: 400; }

.verdict-ship { background: linear-gradient(135deg, rgba(0,201,122,0.12), rgba(0,168,224,0.08)); border: 1px solid rgba(0,201,122,0.3); border-radius: 16px; padding: 1.8rem; text-align: center; }
.verdict-hold { background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(124,92,191,0.08)); border: 1px solid rgba(255,107,107,0.3); border-radius: 16px; padding: 1.8rem; text-align: center; }
.verdict-inconclusive { background: linear-gradient(135deg, rgba(247,183,49,0.10), rgba(0,168,224,0.06)); border: 1px solid rgba(247,183,49,0.3); border-radius: 16px; padding: 1.8rem; text-align: center; }

div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { display: flex; flex-direction: column; gap: 4px; }
div[data-testid="stRadio"] > div > label { display: flex !important; align-items: center; padding: 10px 12px !important; border-radius: 10px !important; font-size: 13px !important; color: #3a6050 !important; cursor: pointer !important; border: none !important; background: transparent !important; }
div[data-testid="stRadio"] > div > label:hover { background: rgba(0,201,122,0.08) !important; color: #a0c8b0 !important; }
div[data-testid="stRadio"] > div > label[aria-checked="true"] { background: rgba(0,201,122,0.12) !important; color: #00c97a !important; font-weight: 600 !important; }
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }

.stButton button { background: linear-gradient(135deg, #00c97a, #00a8e0) !important; border: none !important; border-radius: 10px !important; color: #030d0a !important; font-weight: 700 !important; font-size: 13px !important; }
div[data-testid="stSelectbox"] > div { background: #071510 !important; border: 1px solid #0d2a1a !important; border-radius: 10px !important; color: #e2f0eb !important; }
div[data-testid="stFileUploader"] { background: #071510; border: 1px dashed #0d2a1a; border-radius: 16px; }
.stSlider > div > div { background: linear-gradient(90deg, #00c97a, #00a8e0) !important; }
</style>
""", unsafe_allow_html=True)

CHART_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#3a6050', family='Inter', size=11),
    margin=dict(t=20, b=20, l=0, r=0),
)

with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0;">
      <div style="font-size:18px;font-weight:700;background:linear-gradient(90deg,#00c97a,#00a8e0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.5px;margin-bottom:2px;">⚡ AB Test Engine</div>
      <div style="font-size:11px;color:#1a3a28;">Statistical Experiment Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Nav", ["▦  Analyzer", "○  About"], label_visibility="collapsed")

    st.markdown("""
    <div style="background:rgba(0,201,122,0.06);border:1px solid rgba(0,201,122,0.15);border-radius:12px;padding:1rem;margin-top:1.5rem;">
      <div style="font-size:11px;font-weight:600;color:#00c97a;margin-bottom:8px;">HOW IT WORKS</div>
      <div style="font-size:11px;color:#3a6050;line-height:1.8;">
        1. Upload your CSV<br>
        2. Map your columns<br>
        3. Get instant stats<br>
        4. Read the verdict
      </div>
    </div>
    <div style="background:rgba(0,168,224,0.06);border:1px solid rgba(0,168,224,0.15);border-radius:12px;padding:1rem;margin-top:1rem;">
      <div style="font-size:11px;font-weight:600;color:#00a8e0;margin-bottom:8px;">STATS USED</div>
      <div style="font-size:11px;color:#3a6050;line-height:1.8;">
        Two-proportion Z-test<br>
        95% Confidence Interval<br>
        Cohen's h Effect Size<br>
        α = 0.05
      </div>
    </div>
    """, unsafe_allow_html=True)

def run_analysis(df, group_col, conversion_col, control_label, treatment_label):
    control = df[df[group_col] == control_label][conversion_col]
    treatment = df[df[group_col] == treatment_label][conversion_col]
    n_c, n_t = len(control), len(treatment)
    conv_c, conv_t = control.mean(), treatment.mean()
    diff = conv_t - conv_c
    rel_diff = diff / conv_c if conv_c > 0 else 0
    conversions = np.array([treatment.sum(), control.sum()])
    nobs = np.array([n_t, n_c])
    z_stat, p_value = proportions_ztest(conversions, nobs)
    se = np.sqrt((conv_c*(1-conv_c)/n_c) + (conv_t*(1-conv_t)/n_t))
    ci_lower = diff - 1.96 * se
    ci_upper = diff + 1.96 * se
    cohen_h = 2*np.arcsin(np.sqrt(conv_t)) - 2*np.arcsin(np.sqrt(conv_c))
    return {
        'n_control': n_c, 'n_treatment': n_t,
        'conv_control': conv_c, 'conv_treatment': conv_t,
        'diff': diff, 'rel_diff': rel_diff,
        'z_stat': z_stat, 'p_value': p_value,
        'ci_lower': ci_lower, 'ci_upper': ci_upper,
        'cohen_h': cohen_h, 'significant': p_value < 0.05
    }

if "Analyzer" in page:
    st.markdown("""
    <div style="font-size:28px;font-weight:700;color:#e2f0eb;letter-spacing:-0.5px;margin-bottom:4px;padding-top:0.5rem;">
      A/B Test <span style="background:linear-gradient(90deg,#00c97a,#00a8e0,#7c5cbf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Analyzer</span>
    </div>
    <div style="font-size:14px;color:#3a6050;margin-bottom:1.5rem;">Upload any experiment CSV and get instant statistical analysis.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Upload Dataset <span>CSV files only</span></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload your A/B test CSV", type=['csv'], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded:
        df = pd.read_csv(uploaded)
        st.markdown(f"""
        <div style="background:rgba(0,201,122,0.08);border:1px solid rgba(0,201,122,0.2);border-radius:12px;padding:12px 16px;margin-bottom:1rem;font-size:13px;color:#00c97a;">
          ✓ Loaded {len(df):,} rows × {len(df.columns)} columns
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">Configure Test <span>map your columns</span></div>', unsafe_allow_html=True)
        cols = df.columns.tolist()
        c1, c2 = st.columns(2)
        with c1:
            group_col = st.selectbox("Group column (A/B)", cols)
            unique_groups = df[group_col].unique().tolist()
            control_label = st.selectbox("Control group label", unique_groups)
        with c2:
            conversion_col = st.selectbox("Conversion column (0/1)", cols)
            treatment_options = [g for g in unique_groups if g != control_label]
            treatment_label = st.selectbox("Treatment group label", treatment_options)
        alpha = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Run Analysis ↗"):
            r = run_analysis(df, group_col, conversion_col, control_label, treatment_label)
            significant = r['p_value'] < alpha

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Control Conversion</div><div class="metric-value">{r['conv_control']*100:.2f}%</div><div class="metric-sub">n = {r['n_control']:,}</div></div>""", unsafe_allow_html=True)
            with c2:
                color = '#00c97a' if r['diff'] > 0 else '#ff6b6b'
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Treatment Conversion</div><div class="metric-value" style="color:{color};">{r['conv_treatment']*100:.2f}%</div><div class="metric-sub">n = {r['n_treatment']:,}</div></div>""", unsafe_allow_html=True)
            with c3:
                arrow = '▲' if r['diff'] > 0 else '▼'
                color = '#00c97a' if r['diff'] > 0 else '#ff6b6b'
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Relative Uplift</div><div class="metric-value" style="color:{color};">{arrow} {abs(r['rel_diff'])*100:.2f}%</div><div class="metric-sub">{r['diff']*100:+.4f}% absolute</div></div>""", unsafe_allow_html=True)
            with c4:
                p_color = '#00c97a' if significant else '#ff6b6b'
                st.markdown(f"""<div class="metric-card"><div class="metric-label">P-Value</div><div class="metric-value" style="color:{p_color};">{r['p_value']:.4f}</div><div class="metric-sub">α = {alpha}</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if significant and r['diff'] > 0:
                verdict_class = 'verdict-ship'
                verdict_icon = '🚀'
                verdict_title = 'Ship It'
                verdict_color = '#00c97a'
                verdict_text = f'The treatment outperforms control by {r["rel_diff"]*100:.2f}% and the result is statistically significant (p={r["p_value"]:.4f}). You can confidently roll out the new version.'
            elif significant and r['diff'] < 0:
                verdict_class = 'verdict-hold'
                verdict_icon = '🛑'
                verdict_title = 'Keep Control'
                verdict_color = '#ff6b6b'
                verdict_text = f'The treatment performs worse than control by {abs(r["rel_diff"])*100:.2f}% and the result is statistically significant (p={r["p_value"]:.4f}). Do not ship the new version.'
            else:
                verdict_class = 'verdict-inconclusive'
                verdict_icon = '⚠️'
                verdict_title = 'Inconclusive'
                verdict_color = '#f7b731'
                verdict_text = f'No statistically significant difference detected (p={r["p_value"]:.4f} > α={alpha}). The observed difference of {r["diff"]*100:+.4f}% is likely due to random chance. Run the test longer or redesign the experiment.'

            st.markdown(f"""
            <div class="{verdict_class}">
              <div style="font-size:36px;margin-bottom:10px;">{verdict_icon}</div>
              <div style="font-size:24px;font-weight:700;color:{verdict_color};margin-bottom:10px;letter-spacing:-0.5px;">{verdict_title}</div>
              <div style="font-size:14px;color:#c8e0d4;line-height:1.7;max-width:620px;margin:0 auto;">{verdict_text}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="card"><div class="card-title">Conversion Rate Comparison</div>', unsafe_allow_html=True)
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                    x=[control_label, treatment_label],
                    y=[r['conv_control']*100, r['conv_treatment']*100],
                    marker_color=['#00a8e0', '#00c97a' if r['diff'] > 0 else '#ff6b6b'],
                    marker_line_width=0,
                    text=[f"{r['conv_control']*100:.3f}%", f"{r['conv_treatment']*100:.3f}%"],
                    textposition='outside',
                    textfont=dict(color='#3a6050', size=12)
                ))
                fig1.update_layout(**CHART_THEME, height=260, bargap=0.5, showlegend=False,
                                   yaxis=dict(gridcolor='#0d2a1a', linecolor='#0d2a1a', ticksuffix='%'),
                                   xaxis=dict(linecolor='#0d2a1a'))
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="card"><div class="card-title">Confidence Interval <span>95%</span></div>', unsafe_allow_html=True)
                fig2 = go.Figure()
                fig2.add_shape(type='line', x0=0, x1=0, y0=-0.5, y1=1.5,
                               line=dict(color='#3a6050', width=1, dash='dash'))
                fig2.add_trace(go.Scatter(
                    x=[r['diff']*100], y=[0],
                    mode='markers',
                    marker=dict(color=verdict_color, size=16, symbol='diamond'),
                    error_x=dict(
                        type='data', symmetric=False,
                        array=[(r['ci_upper'] - r['diff'])*100],
                        arrayminus=[(r['diff'] - r['ci_lower'])*100],
                        color=verdict_color, thickness=2, width=12
                    ),
                    showlegend=False
                ))
                fig2.update_layout(**CHART_THEME, height=260,
                                   xaxis=dict(gridcolor='#0d2a1a', linecolor='#0d2a1a',
                                             title='Difference in conversion rate (%)', ticksuffix='%'),
                                   yaxis=dict(visible=False))
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-title">Statistical Summary</div>', unsafe_allow_html=True)
            summary_data = {
                'Metric': ['Z-statistic', 'P-value', 'Significant', "Effect Size (Cohen's h)", 'CI Lower (95%)', 'CI Upper (95%)', 'Absolute Difference', 'Relative Difference'],
                'Value': [
                    f"{r['z_stat']:.4f}",
                    f"{r['p_value']:.4f}",
                    '✓ Yes' if significant else '✗ No',
                    f"{r['cohen_h']:.4f}",
                    f"{r['ci_lower']*100:.4f}%",
                    f"{r['ci_upper']*100:.4f}%",
                    f"{r['diff']*100:+.4f}%",
                    f"{r['rel_diff']*100:+.2f}%"
                ],
                'Interpretation': [
                    'Test statistic — how many std devs from null',
                    f"{'Below' if significant else 'Above'} α={alpha} threshold",
                    f"{'Reject' if significant else 'Fail to reject'} null hypothesis",
                    'Small if <0.2, Medium <0.5, Large >0.5',
                    'Lower bound of true difference',
                    'Upper bound of true difference',
                    'Raw percentage point difference',
                    'Percentage change relative to control'
                ]
            }
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

elif "About" in page:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#071510 0%,#0a1628 100%);border:1px solid #0d2a1a;border-radius:20px;padding:2.5rem;margin-bottom:1.5rem;text-align:center;margin-top:0.5rem;">
      <div style="display:inline-block;background:rgba(0,201,122,0.12);color:#00c97a;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:1px;margin-bottom:1rem;">⚡ Portfolio Project</div>
      <div style="font-size:28px;font-weight:700;color:#e2f0eb;margin-bottom:0.75rem;">A/B Test Engine</div>
      <div style="font-size:14px;color:#3a6050;line-height:1.7;max-width:600px;margin:0 auto;">
        An automated statistical experiment analyzer that runs two-proportion Z-tests, computes confidence intervals, and delivers plain-English business verdicts on any A/B test dataset.
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="card">
          <div class="card-title">What is A/B Testing?</div>
          <div style="font-size:13px;color:#c8e0d4;line-height:1.7;">
            A/B testing is a controlled experiment where two versions of something are tested simultaneously on randomly split user groups.
            The goal is to determine with statistical confidence whether a change produces a meaningful improvement — not just random noise.
            Companies like Netflix, Airbnb, and Stripe run thousands of A/B tests every year.
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="card">
          <div class="card-title">Tech Stack</div>
          <div style="margin-top:0.5rem;">
            <span style="display:inline-block;background:rgba(0,201,122,0.08);border:1px solid rgba(0,201,122,0.2);color:#00c97a;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Python</span>
            <span style="display:inline-block;background:rgba(0,201,122,0.08);border:1px solid rgba(0,201,122,0.2);color:#00c97a;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Pandas</span>
            <span style="display:inline-block;background:rgba(0,168,224,0.08);border:1px solid rgba(0,168,224,0.2);color:#00a8e0;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">SciPy</span>
            <span style="display:inline-block;background:rgba(0,168,224,0.08);border:1px solid rgba(0,168,224,0.2);color:#00a8e0;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Statsmodels</span>
            <span style="display:inline-block;background:rgba(124,92,191,0.08);border:1px solid rgba(124,92,191,0.2);color:#a07ce0;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Plotly</span>
            <span style="display:inline-block;background:rgba(124,92,191,0.08);border:1px solid rgba(124,92,191,0.2);color:#a07ce0;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Streamlit</span>
            <span style="display:inline-block;background:rgba(0,201,122,0.08);border:1px solid rgba(0,201,122,0.2);color:#00c97a;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">NumPy</span>
            <span style="display:inline-block;background:rgba(0,168,224,0.08);border:1px solid rgba(0,168,224,0.2);color:#00a8e0;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:500;margin:4px;">Pingouin</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class="card">
          <div class="card-title">How It Was Built</div>
          <div style="display:flex;flex-direction:column;gap:14px;margin-top:0.5rem;">
            <div style="display:flex;gap:12px;align-items:flex-start;">
              <div style="width:32px;height:32px;border-radius:10px;background:rgba(0,201,122,0.12);color:#00c97a;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0;">1</div>
              <div><div style="font-size:14px;font-weight:600;color:#e2f0eb;margin-bottom:3px;">EDA + Sanity Checks</div><div style="font-size:12px;color:#3a6050;line-height:1.5;">294k rows explored — mismatches, duplicates, and type issues identified and fixed.</div></div>
            </div>
            <div style="display:flex;gap:12px;align-items:flex-start;">
              <div style="width:32px;height:32px;border-radius:10px;background:rgba(0,168,224,0.12);color:#00a8e0;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0;">2</div>
              <div><div style="font-size:14px;font-weight:600;color:#e2f0eb;margin-bottom:3px;">Hypothesis Testing</div><div style="font-size:12px;color:#3a6050;line-height:1.5;">Two-proportion Z-test with p-value, confidence intervals, and Cohen's h effect size.</div></div>
            </div>
            <div style="display:flex;gap:12px;align-items:flex-start;">
              <div style="width:32px;height:32px;border-radius:10px;background:rgba(124,92,191,0.12);color:#a07ce0;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0;">3</div>
              <div><div style="font-size:14px;font-weight:600;color:#e2f0eb;margin-bottom:3px;">Business Verdict Engine</div><div style="font-size:12px;color:#3a6050;line-height:1.5;">Automated Ship / Hold / Inconclusive verdict with plain English reasoning.</div></div>
            </div>
            <div style="display:flex;gap:12px;align-items:flex-start;">
              <div style="width:32px;height:32px;border-radius:10px;background:rgba(0,201,122,0.12);color:#00c97a;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0;">4</div>
              <div><div style="font-size:14px;font-weight:600;color:#e2f0eb;margin-bottom:3px;">Deployed as a Tool</div><div style="font-size:12px;color:#3a6050;line-height:1.5;">Works on any A/B test CSV — not just this dataset. Upload, map, analyze.</div></div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="text-align:center;padding:2rem;">
      <div style="font-size:13px;color:#3a6050;margin-bottom:0.5rem;">Built by</div>
      <div style="font-size:20px;font-weight:700;background:linear-gradient(90deg,#00c97a,#00a8e0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Gayathri Menon</div>
    </div>
    """, unsafe_allow_html=True)
