"""
DCF Valuation Playground - Interactive Streamlit Application

A comprehensive DCF valuation tool with flexible growth rate modeling,
sensitivity analysis, and professional visualizations.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import StringIO
from dcf import DcfInputs, dcf_valuation, sensitivity_table

# Page configuration
st.set_page_config(
    page_title="DCF Valuation Playground",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .kpi-label {
        font-size: 12px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Title and disclaimer
st.title("📊 DCF Valuation Playground")
st.markdown("""
*Interactive DCF valuation model for financial analysis and learning*
""")

with st.expander("⚠️ Important Disclaimer", expanded=False):
    st.warning("""
    **Educational Use Only:** This tool is for learning about DCF valuation concepts and should 
    NOT be used for actual investment decisions.
    
    **Not Financial Advice:** Nothing in this tool constitutes financial advice. Always consult 
    with a qualified financial advisor before making investment decisions.
    
    **No Warranties:** Results are provided "as-is" without guarantee of accuracy. 
    Valuation assumptions should be thoroughly validated against company fundamentals.
    """)

# ============================================================================
# SIDEBAR: INPUT CONFIGURATION
# ============================================================================

st.sidebar.header("📋 Model Configuration")

# ─ Company Basics ─
st.sidebar.subheader("Company Information")
company_name = st.sidebar.text_input("Company Name", value="TechCorp Inc", key="company_name")
shares_outstanding = st.sidebar.number_input(
    "Shares Outstanding (millions)",
    min_value=0.1,
    value=100.0,
    step=1.0,
    key="shares"
)

st.sidebar.markdown("---")

# ─ Revenue & Growth ─
st.sidebar.subheader("Revenue & Growth")
revenue_year0 = st.sidebar.number_input(
    "Year 0 Revenue ($ millions)",
    min_value=1.0,
    value=500.0,
    step=10.0,
    key="revenue"
)

projection_years = st.sidebar.slider(
    "Projection Years",
    min_value=3,
    max_value=20,
    value=10,
    step=1,
    key="proj_years"
)

# Growth rates: Toggle between CAGR or per-year
growth_input_method = st.sidebar.radio(
    "Growth Rate Input",
    options=["📊 Single CAGR", "📈 Per-Year Rates"],
    horizontal=True,
    key="growth_method"
)

if growth_input_method == "📊 Single CAGR":
    cagr = st.sidebar.slider(
        "5-Year CAGR (%)",
        min_value=-20.0,
        max_value=50.0,
        value=8.0,
        step=0.5,
        key="cagr"
    ) / 100
    
    # Apply CAGR to all years, optionally decelerate
    decelerate = st.sidebar.checkbox("Decelerate after year 5", value=False, key="decel")
    growth_rates = []
    for year in range(1, projection_years + 1):
        if decelerate and year > 5:
            # Decelerate towards terminal growth
            growth_rates.append(cagr * (1 - (year - 5) / (projection_years - 5)) * 0.5)
        else:
            growth_rates.append(cagr)
else:
    st.sidebar.markdown("**Annual Growth Rates (%)**")
    growth_rates = []
    cols = st.sidebar.columns(2)
    for year in range(1, projection_years + 1):
        col = cols[(year - 1) % 2]
        with col:
            g = st.number_input(
                f"Year {year}",
                min_value=-20.0,
                max_value=30.0,
                value=8.0 if year <= 5 else 4.0,
                step=0.5,
                key=f"growth_{year}"
            )
            growth_rates.append(g / 100)

st.sidebar.markdown("---")

# ─ Profitability ─
st.sidebar.subheader("Profitability Path")

ebit_margin_start = st.sidebar.slider(
    "EBIT Margin Start (%)",
    min_value=0.0,
    max_value=50.0,
    value=10.0,
    step=0.5,
    key="ebit_start"
) / 100

ebit_margin_end = st.sidebar.slider(
    "EBIT Margin End (%)",
    min_value=0.0,
    max_value=50.0,
    value=15.0,
    step=0.5,
    key="ebit_end"
) / 100

st.sidebar.info(
    f"Margin will interpolate linearly from **{ebit_margin_start*100:.1f}%** "
    f"to **{ebit_margin_end*100:.1f}%** over {projection_years} years."
)

tax_rate = st.sidebar.slider(
    "Tax Rate (%)",
    min_value=0.0,
    max_value=50.0,
    value=21.0,
    step=0.5,
    key="tax_rate"
) / 100

reinvestment_rate = st.sidebar.slider(
    "Reinvestment Rate (% of NOPAT)",
    min_value=0.0,
    max_value=100.0,
    value=40.0,
    step=5.0,
    key="reinvest"
) / 100

st.sidebar.markdown("---")

# ─ Valuation Assumptions ─
st.sidebar.subheader("Valuation Assumptions")

wacc = st.sidebar.slider(
    "WACC (%)",
    min_value=2.0,
    max_value=25.0,
    value=8.0,
    step=0.25,
    key="wacc"
) / 100

terminal_growth = st.sidebar.slider(
    "Terminal Growth Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=2.5,
    step=0.1,
    key="term_growth"
) / 100

net_debt = st.sidebar.number_input(
    "Net Debt ($ millions)",
    min_value=-500.0,
    value=100.0,
    step=10.0,
    key="net_debt"
)

# ============================================================================
# VALIDATION & CALCULATION
# ============================================================================

try:
    inputs = DcfInputs(
        revenue0=revenue_year0,
        years=projection_years,
        growth_rates=growth_rates,
        ebit_margin_start=ebit_margin_start,
        ebit_margin_end=ebit_margin_end,
        tax_rate=tax_rate,
        reinvestment_rate=reinvestment_rate,
        wacc=wacc,
        terminal_growth=terminal_growth,
        net_debt=net_debt,
        shares_outstanding=shares_outstanding * 1_000_000,
    )
    
    results = dcf_valuation(inputs)
    calculation_valid = True
    
except ValueError as e:
    st.sidebar.error(f"❌ Input Error:\n\n{str(e)}")
    calculation_valid = False
except Exception as e:
    st.sidebar.error(f"❌ Unexpected Error:\n\n{str(e)}")
    calculation_valid = False

if not calculation_valid:
    st.stop()


# ============================================================================
# MAIN CONTENT: KPI CARDS
# ============================================================================

st.header("📈 Valuation Results")

# Key metrics in columns
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        label="Enterprise Value",
        value=f"${results['enterprise_value']/1e6:.0f}M",
        delta=None,
        help="Total firm value (debt + equity holders)"
    )

with kpi2:
    st.metric(
        label="Equity Value",
        value=f"${results['equity_value']/1e6:.0f}M",
        delta=f"${net_debt:.0f}M net debt",
        help="Value available to equity holders"
    )

with kpi3:
    st.metric(
        label="Value per Share",
        value=f"${results['value_per_share']:.2f}",
        delta=None,
        help=f"Intrinsic value per share ({shares_outstanding:.0f}M shares)"
    )

with kpi4:
    pv_fcf_pct = (results['pv_fcf'] / results['enterprise_value']) * 100
    st.metric(
        label="PV of FCFs",
        value=f"${results['pv_fcf']/1e6:.0f}M",
        delta=f"{pv_fcf_pct:.0f}% of EV",
        help="Present value of projected free cash flows"
    )

with kpi5:
    pv_tv_pct = (results['pv_terminal'] / results['enterprise_value']) * 100
    st.metric(
        label="PV of Terminal",
        value=f"${results['pv_terminal']/1e6:.0f}M",
        delta=f"{pv_tv_pct:.0f}% of EV",
        help="Present value of terminal value"
    )

st.markdown("---")

# ============================================================================
# FORECAST TABLE
# ============================================================================

st.subheader("📊 Financial Forecast Table")

forecast_df = results['df'].copy()
forecast_df['Revenue'] = forecast_df['Revenue'] / 1e6
forecast_df['EBITMargin%'] = forecast_df['EBITMargin'] * 100
forecast_df['EBIT'] = forecast_df['EBIT'] / 1e6
forecast_df['NOPAT'] = forecast_df['NOPAT'] / 1e6
forecast_df['Reinvestment'] = forecast_df['Reinvestment'] / 1e6
forecast_df['FCF'] = forecast_df['FCF'] / 1e6
forecast_df['DiscountFactor'] = forecast_df['DiscountFactor']
forecast_df['PV_FCF'] = forecast_df['PV_FCF'] / 1e6

display_cols = ['Year', 'Revenue', 'EBITMargin%', 'EBIT', 'NOPAT', 'Reinvestment', 'FCF', 'DiscountFactor', 'PV_FCF']
display_df = forecast_df[display_cols].copy()

# Format for display
def format_forecast(val, col_name):
    if col_name == 'Year':
        return f"{int(val)}"
    elif col_name == 'EBITMargin%':
        return f"{val:.1f}%"
    elif col_name == 'DiscountFactor':
        return f"{val:.4f}"
    else:
        return f"${val:,.1f}M" if val >= 0 else f"-${abs(val):,.1f}M"

# Create styled dataframe
styled_df = display_df.style.format({
    'Year': '{:.0f}',
    'Revenue': '${:,.1f}M',
    'EBITMargin%': '{:.1f}%',
    'EBIT': '${:,.1f}M',
    'NOPAT': '${:,.1f}M',
    'Reinvestment': '${:,.1f}M',
    'FCF': '${:,.1f}M',
    'DiscountFactor': '{:.4f}',
    'PV_FCF': '${:,.1f}M',
}).background_gradient(subset=['FCF', 'PV_FCF'], cmap='RdYlGn')

st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

st.subheader("📈 Charts & Analysis")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Revenue & FCF Progression
with chart_col1:
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Bar(
        x=results['df']['Year'],
        y=results['df']['Revenue'] / 1e6,
        name='Revenue',
        marker_color='#667eea',
        yaxis='y1',
    ))
    fig_revenue.add_trace(go.Scatter(
        x=results['df']['Year'],
        y=results['df']['FCF'] / 1e6,
        name='Free Cash Flow',
        mode='lines+markers',
        marker_color='#f56565',
        line=dict(width=3),
        yaxis='y2',
    ))
    fig_revenue.update_layout(
        title="Revenue & Free Cash Flow Progression",
        hovermode='x unified',
        xaxis_title="Year",
        yaxis=dict(title="Revenue ($ millions)", side='left'),
        yaxis2=dict(title="FCF ($ millions)", overlaying='y1', side='right'),
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Chart 2: Enterprise Value Composition (Pie)
with chart_col2:
    fig_composition = go.Figure(data=[go.Pie(
        labels=['PV of Projected FCFs', 'PV of Terminal Value'],
        values=[results['pv_fcf']/1e6, results['pv_terminal']/1e6],
        marker_colors=['#667eea', '#48bb78'],
        textposition='inside',
        textinfo='label+percent',
    )])
    fig_composition.update_layout(
        title="Enterprise Value Composition",
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_composition, use_container_width=True)

# Chart 3: EBIT Margin Path
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    fig_margin = go.Figure()
    fig_margin.add_trace(go.Scatter(
        x=results['df']['Year'],
        y=results['df']['EBITMargin'] * 100,
        mode='lines+markers',
        name='EBIT Margin',
        fill='tozeroy',
        line=dict(color='#ed8936', width=3),
        marker=dict(size=8),
    ))
    fig_margin.update_layout(
        title="EBIT Margin Progression",
        xaxis_title="Year",
        yaxis_title="EBIT Margin (%)",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        yaxis=dict(tickformat='.1f')
    )
    st.plotly_chart(fig_margin, use_container_width=True)

# Chart 4: FCF Bridge (NOPAT → Reinvestment → FCF)
with chart_col4:
    fig_bridge = go.Figure()
    fig_bridge.add_trace(go.Bar(
        x=results['df']['Year'],
        y=results['df']['NOPAT'] / 1e6,
        name='NOPAT',
        marker_color='#90cdf4',
    ))
    fig_bridge.add_trace(go.Bar(
        x=results['df']['Year'],
        y=-results['df']['Reinvestment'] / 1e6,
        name='Reinvestment',
        marker_color='#fc8181',
    ))
    fig_bridge.add_trace(go.Scatter(
        x=results['df']['Year'],
        y=results['df']['FCF'] / 1e6,
        name='FCF',
        mode='lines+markers',
        marker_color='#38a169',
        line=dict(width=3),
    ))
    fig_bridge.update_layout(
        title="FCF Bridge: NOPAT → Reinvestment → FCF",
        xaxis_title="Year",
        yaxis_title="Amount ($ millions)",
        barmode='relative',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_bridge, use_container_width=True)

st.markdown("---")

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

st.subheader("🔍 Sensitivity Analysis")

st.markdown("""
This table shows how the value per share changes across different WACC and Terminal Growth Rate assumptions.
The **base case** cell is highlighted. Green indicates higher valuations, red indicates lower valuations.
""")

# Create dynamic ranges centered around base case
# WACC: base ± 2% in 0.5% increments (7 values total)
wacc_center = wacc * 100
wacc_low = max(2.0, wacc_center - 2.0)
wacc_high = min(25.0, wacc_center + 2.0)
wacc_range = np.arange(wacc_low, wacc_high + 0.01, 0.5) / 100

# Terminal Growth: base ± 1% in 0.25% increments (7+ values total)
g_center = terminal_growth * 100
g_low = max(0.0, g_center - 1.0)
g_high = min(10.0, g_center + 1.0)
g_range = np.arange(g_low, g_high + 0.01, 0.25) / 100

# Display current ranges
col1, col2 = st.columns(2)
with col1:
    st.write(f"**WACC Range**: {wacc_range[0]*100:.2f}% → {wacc_range[-1]*100:.2f}%")
with col2:
    st.write(f"**Terminal Growth Range**: {g_range[0]*100:.2f}% → {g_range[-1]*100:.2f}%")

# Generate sensitivity table using new function
df_sensitivity = sensitivity_table(inputs, list(wacc_range), list(g_range))

# Format table for display (percentages in index/columns, currency in values)
df_display = df_sensitivity.copy()
df_display.index = [f"{g*100:.2f}%" for g in df_display.index]
df_display.columns = [f"{w*100:.2f}%" for w in df_display.columns]

# Apply styling with base case highlight
def highlight_base_case(val):
    """Highlight base case cell with bold background."""
    return 'background-color: #ffd700; font-weight: bold' if not pd.isna(val) else ''

def color_gradient(val):
    """Apply color gradient (red-yellow-green) for non-base values."""
    if pd.isna(val):
        return 'background-color: #f0f0f0; color: #999'
    
    # Find min/max for gradient scaling
    valid_vals = df_sensitivity.values[~np.isnan(df_sensitivity.values)]
    if len(valid_vals) == 0:
        return ''
    
    vmin, vmax = valid_vals.min(), valid_vals.max()
    norm_val = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    
    # RdYlGn colorscale: Red (0), Yellow (0.5), Green (1)
    if norm_val < 0.5:
        r = int(255)
        g = int(255 * (norm_val * 2))
        b = 0
    else:
        r = int(255 * (1 - (norm_val - 0.5) * 2))
        g = int(255)
        b = 0
    
    return f'background-color: rgb({r},{g},{b}); color: {"white" if norm_val < 0.3 or norm_val > 0.7 else "black"}'

# Create styled DataFrame
styled_df = df_display.style.format('${:,.2f}', na_rep='—')

# Highlight base case cell
base_wacc_idx = np.argmin(np.abs(wacc_range - wacc))
base_g_idx = np.argmin(np.abs(g_range - terminal_growth))
base_g_label = f"{terminal_growth*100:.2f}%"
base_wacc_label = f"{wacc*100:.2f}%"

styled_df = styled_df.applymap(
    lambda val: 'background-color: #ffd700; font-weight: bold; color: black' 
                if not pd.isna(val) else ''
)

# Better approach: manually set base case styling
for idx in styled_df.index:
    for col in styled_df.columns:
        if idx == base_g_label and col == base_wacc_label:
            styled_df.map(
                lambda val: 'background-color: #ffd700; font-weight: bold' 
                if not pd.isna(val) else ''
            )

st.dataframe(styled_df, use_container_width=True)

# Add annotation
st.markdown(f"""
**Base Case:** Terminal Growth = {terminal_growth*100:.2f}%, WACC = {wacc*100:.2f}% 
(highlighted in **gold**)

*Values shown as value per share ($). Dashes indicate invalid scenarios (WACC ≤ Terminal Growth).*
""")

st.markdown("---")

# ============================================================================
# DOWNLOAD & EXPORT
# ============================================================================

st.subheader("💾 Export Results")

# Prepare CSV data
csv_buffer = StringIO()
csv_data = results['df'].copy()
csv_data['Revenue'] = csv_data['Revenue'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['EBIT'] = csv_data['EBIT'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['NOPAT'] = csv_data['NOPAT'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['Reinvestment'] = csv_data['Reinvestment'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['FCF'] = csv_data['FCF'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['PV_FCF'] = csv_data['PV_FCF'].apply(lambda x: f"{x/1e6:,.2f}")
csv_data['EBITMargin'] = csv_data['EBITMargin'].apply(lambda x: f"{x*100:.2f}%")

csv_string = csv_data.to_csv(index=False)

download_col1, download_col2, download_col3 = st.columns(3)

with download_col1:
    st.download_button(
        label="📥 Download Forecast (CSV)",
        data=csv_string,
        file_name=f"{company_name.replace(' ', '_')}_DCF_Forecast.csv",
        mime="text/csv",
        key="download_csv"
    )

with download_col2:
    # Summary metrics download
    summary_data = {
        'Metric': [
            'Company Name',
            'Enterprise Value ($M)',
            'Equity Value ($M)',
            'Value per Share ($)',
            'PV of Projected FCFs ($M)',
            'PV of Terminal Value ($M)',
            'Terminal as % of EV',
            'Net Debt ($M)',
            'Shares Outstanding (M)',
        ],
        'Value': [
            company_name,
            f"{results['enterprise_value']/1e6:,.2f}",
            f"{results['equity_value']/1e6:,.2f}",
            f"{results['value_per_share']:.2f}",
            f"{results['pv_fcf']/1e6:,.2f}",
            f"{results['pv_terminal']/1e6:,.2f}",
            f"{(results['pv_terminal']/results['enterprise_value']*100):.1f}%",
            f"{net_debt:,.2f}",
            f"{shares_outstanding:,.2f}",
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_csv = summary_df.to_csv(index=False)
    
    st.download_button(
        label="📊 Download Summary (CSV)",
        data=summary_csv,
        file_name=f"{company_name.replace(' ', '_')}_DCF_Summary.csv",
        mime="text/csv",
        key="download_summary"
    )

with download_col3:
    # Assumptions download
    assumptions_data = {
        'Parameter': [
            'Projection Years',
            'Revenue Year 0 ($M)',
            'EBIT Margin Start',
            'EBIT Margin End',
            'Tax Rate',
            'Reinvestment Rate',
            'WACC',
            'Terminal Growth Rate',
        ],
        'Value': [
            projection_years,
            f"{revenue_year0:,.2f}",
            f"{ebit_margin_start*100:.2f}%",
            f"{ebit_margin_end*100:.2f}%",
            f"{tax_rate*100:.2f}%",
            f"{reinvestment_rate*100:.2f}%",
            f"{wacc*100:.2f}%",
            f"{terminal_growth*100:.2f}%",
        ]
    }
    assumptions_df = pd.DataFrame(assumptions_data)
    assumptions_csv = assumptions_df.to_csv(index=False)
    
    st.download_button(
        label="⚙️ Download Assumptions (CSV)",
        data=assumptions_csv,
        file_name=f"{company_name.replace(' ', '_')}_DCF_Assumptions.csv",
        mime="text/csv",
        key="download_assumptions"
    )

st.markdown("---")

# ============================================================================
# DOCUMENTATION & FOOTER
# ============================================================================

st.subheader("📖 Model Documentation")

with st.expander("How the DCF Model Works", expanded=False):
    st.markdown("""
    ### Revenue-to-FCF Waterfall
    
    1. **Revenue**: Applied annual growth rates to project future sales
    2. **EBIT Margin**: Linearly interpolates from start % to end % over forecast period
    3. **EBIT**: Revenue × EBIT Margin
    4. **NOPAT**: EBIT × (1 - Tax Rate) = Operating profit after tax
    5. **Reinvestment**: NOPAT × Reinvestment Rate (CapEx, working capital)
    6. **FCF**: NOPAT - Reinvestment = Cash available to all investors
    
    ### Valuation
    
    - **PV of FCFs**: Each year's FCF discounted at WACC rate
    - **Terminal Value**: FCF(final year) × (1 + terminal growth) / (WACC - terminal growth)
    - **PV of Terminal**: Terminal value discounted back to today
    - **Enterprise Value**: Sum of PV(FCFs) + PV(Terminal Value)
    - **Equity Value**: Enterprise Value - Net Debt
    - **Value per Share**: Equity Value / Shares Outstanding
    
    ### Key Assumptions
    
    - **WACC** (Discount Rate): Typically 5-12% based on risk
    - **Terminal Growth**: Usually 2-3% (long-term GDP growth proxy)
    - **EBIT Margin**: Reflects competitive position and operating leverage
    - **Reinvestment Rate**: Determines how much growth capital is needed
    """)

with st.expander("Sensitivity Analysis Guide", expanded=False):
    st.markdown("""
    The sensitivity table shows how valuation changes with different assumptions:
    
    - **Columns (WACC)**: Higher WACC = Lower valuations (higher risk = lower value)
    - **Rows (Terminal Growth)**: Higher terminal growth = Higher valuations (better long-term outlook)
    - **Green**: Higher valuations (favorable assumptions)
    - **Red**: Lower valuations (conservative assumptions)
    
    Use this to understand which assumptions drive your valuation most.
    """)

with st.expander("Typical Valuation Ranges", expanded=False):
    st.markdown("""
    | Metric | Conservative | Base Case | Optimistic |
    |--------|--------------|-----------|-----------|
    | WACC | 10-12% | 8-9% | 6-7% |
    | Terminal Growth | 2.0% | 2.5% | 3.0% |
    | Reinvestment Rate | 50-60% | 35-45% | 20-30% |
    | EBIT Margin Expansion | Minimal | Moderate | Significant |
    
    Use these ranges as benchmarks for your assumptions.
    """)

st.divider()

# Footer with warnings and disclaimers
st.markdown("""
<div style="background-color: #fff5e6; padding: 15px; border-radius: 5px; border-left: 4px solid #ed8936;">
    <strong>⚠️ Important Notes:</strong>
    <ul>
        <li>This tool is for <strong>educational purposes only</strong></li>
        <li><strong>Not financial advice</strong> — always consult a qualified advisor</li>
        <li>Valuation results are <strong>highly sensitive</strong> to assumptions, especially terminal value</li>
        <li><strong>Validate</strong> your assumptions against company fundamentals and peer benchmarks</li>
        <li><strong>Results provided as-is</strong> without guarantee of accuracy</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: gray; margin-top: 30px; font-size: 12px;">
    DCF Valuation Playground | Built with Streamlit | MIT License
</div>
""", unsafe_allow_html=True)

