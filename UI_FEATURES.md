# Streamlit UI Features - Quick Reference

## 🎯 Main UI Sections

### 1️⃣ Sidebar Configuration
**Collapsible, organized into 5 sections:**
- 📋 Company Information (name, shares)
- 📊 Revenue & Growth (base revenue, projection years, growth rate toggle)
- 💰 Profitability Path (EBIT margins, tax rate, reinvestment)
- 💵 Valuation Assumptions (WACC, terminal growth, net debt)

### 2️⃣ Growth Rate Input Toggle
**Two methods:**
- **Single CAGR:** 5-year CAGR slider + optional deceleration checkbox
- **Per-Year Rates:** Individual sliders for each projection year

### 3️⃣ KPI Cards (5 Metrics)
```
┌──────────────────────────────────────────────────────────────────┐
│ Enterprise Value │ Equity Value │ Value/Share │ PV of FCF │ PV of Terminal │
│   $902M          │    $802M     │    $8.02    │  $300M    │     $601M      │
└──────────────────────────────────────────────────────────────────┘
```

### 4️⃣ Forecast Table
| Year | Revenue | EBIT Margin % | EBIT | NOPAT | Reinvestment | FCF | Discount Factor | PV_FCF |
|------|---------|---------------|------|-------|--------------|-----|-----------------|--------|
| 1 | $550.0M | 10.0% | $55.0M | $43.4M | $17.4M | $26.1M | 0.9259 | $24.1M |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Features:**
- ✅ Green-yellow-red gradient on FCF & PV_FCF
- ✅ Formatted currency with commas
- ✅ Percentage display with %
- ✅ Interactive sorting/filtering

### 5️⃣ Four Charts

**Chart 1: Revenue & FCF Progression**
- Bar chart (Revenue in blue)
- Line chart (FCF in red)
- Dual Y-axes
- Interactive hover

**Chart 2: Enterprise Value Composition**
- Pie chart
- Segments: PV(FCFs) vs PV(Terminal)
- Color-coded, percentage labels

**Chart 3: EBIT Margin Progression**
- Line chart with filled area
- Shows margin path (linear interpolation)
- Year-by-year view

**Chart 4: FCF Bridge (Waterfall)**
- NOPAT (positive bar)
- Reinvestment (negative bar)
- FCF (overlay line)
- Shows calculation flow

### 6️⃣ Sensitivity Analysis Heatmap
```
         WACC: 5%   6%    7%    8%    9%   10%   11%
Terminal:
  2.0%   $12.50  $11.75 $11.05 $10.40 $9.80 $9.25 $8.75
  2.5%   $13.20  $12.40 $11.65 $10.95 $10.30 $9.70 $9.15
  3.0%   $14.00  $13.10 $12.30 $11.55 $10.85 $10.20 $9.60
  ...
```
- 7×7 grid (49 scenarios)
- Red-Yellow-Green color scale
- Hover shows exact values
- Prevents invalid combos (WACC ≤ g)

### 7️⃣ CSV Export (3 Files)

**Button 1: Download Forecast (CSV)**
- All projection years
- All financial metrics
- Formatted output

**Button 2: Download Summary (CSV)**
- 9 key metrics
- Valuation results
- Easy for reports

**Button 3: Download Assumptions (CSV)**
- All input parameters
- Perfect for auditing
- Shareable with stakeholders

### 8️⃣ Documentation (Expandable)

**Expander 1: How the DCF Model Works**
- Revenue-to-FCF waterfall
- Valuation methodology
- Typical ranges by metric

**Expander 2: Sensitivity Analysis Guide**
- How to interpret the table
- WACC vs Terminal Growth dynamics
- Color interpretation

**Expander 3: Typical Valuation Ranges**
- Benchmark table
- Conservative/Base/Optimistic scenarios

### 9️⃣ Disclaimer Section
- ⚠️ Educational use only
- ⚠️ Not financial advice
- ⚠️ Always validate assumptions
- Professional orange warning styling

---

## 🎮 User Interactions

### Sidebar (Left)
- **Sliders:** Drag to adjust numeric ranges
- **Number Inputs:** Type exact values
- **Toggle Button:** Switch growth rate method
- **Checkbox:** Enable/disable deceleration

### Main Content (Right)
- **Expandable Sections:** Click to view details
- **Interactive Charts:** Hover for values, zoom, pan
- **Table:** Click column headers to sort
- **Download Buttons:** Click to export CSV files

---

## 🔧 Technical Features

### Error Handling
```python
# Validation on sidebar
❌ WACC <= terminal growth → "Error: WACC must exceed..."
❌ Growth rates wrong length → "Error: length mismatch..."
✅ Valid inputs → Full calculation and display
```

### Dynamic Computation
```python
# Sensitivity: 49 scenarios computed instantly
for wacc in np.linspace(low, high, 7):
    for term_g in np.linspace(low, high, 7):
        if wacc > term_g:
            results = dcf_valuation(inputs)
            table[i, j] = results['value_per_share']
```

### Responsive Design
- Wide layout (maximizes screen space)
- Column layouts for metrics
- Responsive charts (scale to container)
- Mobile-friendly sliders

---

## 📊 Example Scenarios

### Conservative Valuation
```
WACC: 10.0%
Terminal Growth: 2.0%
Growth Rates: 4% constant
EBIT Margin: 10% → 12%
Reinvestment: 50%
→ Lower Value/Share
```

### Base Case
```
WACC: 8.0%
Terminal Growth: 2.5%
Growth Rates: 8% year 1-5, 4% year 6-10
EBIT Margin: 10% → 15%
Reinvestment: 40%
→ Mid-range Value/Share
```

### Optimistic Case
```
WACC: 6.0%
Terminal Growth: 3.0%
Growth Rates: 10% constant
EBIT Margin: 10% → 18%
Reinvestment: 30%
→ Higher Value/Share
```

---

## 🚀 Quick Start Checklist

- [ ] Install: `pip install -r requirements.txt`
- [ ] Run: `streamlit run app.py`
- [ ] App opens at `http://localhost:8501`
- [ ] Enter company assumptions in sidebar
- [ ] Review KPI cards and charts
- [ ] Check sensitivity analysis
- [ ] Download results as CSV
- [ ] Close browser or press Ctrl+C to stop

---

## 📱 Display Preview

```
┌────────────────────────────────────────────────────────────────┐
│ DCF Valuation Playground 📊                                    │
│ Interactive DCF valuation model for financial analysis         │
├────────────────────────────────────────────────────────────────┤
│ [📋 Important Disclaimer]                                      │
├─────────────────┬──────────────────────────────────────────────┤
│                 │ 📈 VALUATION RESULTS                          │
│ SIDEBAR         │                                               │
│ ────────────    │ ┌──────┬──────┬──────┬──────┬──────┐         │
│ Company Info    │ │ $902M│ $802M│$8.02 │ $300M│ $601M│         │
│ Growth Rates    │ └──────┴──────┴──────┴──────┴──────┘         │
│ Margins         │                                               │
│ Valuation       │ 📊 FINANCIAL FORECAST TABLE                   │
│ Assumptions     │ [Year|Rev|Margin|EBIT|NOPAT|...]             │
│                 │ [ 1  |550| 10.0%|55.0|43.4  |...]             │
│                 │ [... |...|  ... |... |...   |...]             │
│                 │                                               │
│                 │ 📈 CHARTS                                      │
│                 │ [Chart 1]  [Chart 2]                          │
│                 │ [Chart 3]  [Chart 4]                          │
│                 │                                               │
│                 │ 🔍 SENSITIVITY ANALYSIS                        │
│                 │ [Heatmap 7×7]                                 │
│                 │                                               │
│                 │ 💾 EXPORT RESULTS                              │
│                 │ [Download Forecast] [Download Summary]        │
│                 │ [Download Assumptions]                        │
│                 │                                               │
│                 │ 📖 DOCUMENTATION                               │
│                 │ [Model Explanation] [Analysis Guide]          │
└─────────────────┴──────────────────────────────────────────────┘
```

---

## 🎨 Styling Features

- **Color Scheme:** Modern blues, greens, reds for visualizations
- **Fonts:** Large, readable metrics and titles
- **Spacing:** Clean, organized layout
- **Icons:** Emoji for visual clarity
- **Formatting:** Currency, percentages, thousands separators
- **Gradients:** Conditional formatting on tables
- **Responsive:** Works on desktop, tablet, mobile

---

## 📞 Support & Troubleshooting

**Issue:** "WACC must be greater than terminal growth"
**Solution:** Increase WACC or decrease terminal growth in sidebar

**Issue:** Growth rates don't match years
**Solution:** Make sure growth_rates list length = projection years

**Issue:** Charts not rendering
**Solution:** Check internet connection (Plotly CDN), refresh page

**Issue:** Sensitivity table shows NaN
**Solution:** Normal - means WACC ≤ terminal growth for that cell

---

**Status:** ✅ Production Ready
**Lines of Code:** 752 (app.py)
**Features:** 25+
**Charts:** 4 (Plotly)
**Export Formats:** CSV (3 files)
**Mobile Friendly:** Yes
**Deployment:** Streamlit Cloud ready

