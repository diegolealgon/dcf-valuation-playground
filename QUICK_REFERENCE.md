# DCF Engine - Quick Reference

## 🚀 Quick Start

```bash
# Install and run
cd dcf_example
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Core API

### Import and Create Inputs
```python
from dcf import DcfInputs, dcf_valuation

inputs = DcfInputs(
    revenue0=500.0,                    # Base revenue in millions
    years=10,                          # Projection period
    growth_rates=[0.10]*5 + [0.04]*5,  # Annual growth rates
    ebit_margin_start=0.10,            # 10% EBIT margin initially
    ebit_margin_end=0.15,              # 15% EBIT margin at year 10
    tax_rate=0.21,                     # 21% tax rate
    reinvestment_rate=0.40,            # 40% of NOPAT reinvested
    wacc=0.08,                         # 8% discount rate
    terminal_growth=0.025,             # 2.5% perpetual growth
    net_debt=100.0,                    # $100M net debt
    shares_outstanding=100.0           # 100M shares
)
```

### Run Valuation
```python
results = dcf_valuation(inputs)

# Access results
print(f"Value per share: ${results['value_per_share']:.2f}")
print(f"Enterprise value: ${results['enterprise_value']:.0f}M")
print(f"Equity value: ${results['equity_value']:.0f}M")
print(f"PV of FCFs: ${results['pv_fcf']:.0f}M")
print(f"PV of Terminal Value: ${results['pv_terminal']:.0f}M")

# Get projection table
df = results['df']  # DataFrame with all calculations
```

## ✅ Validation Checklist

These are automatically checked when creating DcfInputs:

| Parameter | Valid Range | Default |
|-----------|------------|---------|
| revenue0 | > 0 | Required |
| years | 1-20 | Required |
| growth_rates | -50% to 30% | Required (1 per year) |
| ebit_margin_start | 0-100% | Required |
| ebit_margin_end | 0-100% | Required |
| tax_rate | 0-100% | Required |
| reinvestment_rate | 0-100% | Required |
| wacc | 1-25% | Required |
| terminal_growth | 0-8% | Required |
| net_debt | Any | Required |
| shares_outstanding | > 0 | Required |

**⚠️ Critical: WACC must be > terminal_growth** (enforced automatically)

## 📈 Typical Results

**TechCorp Example:**
```
Revenue Growth:        $500M → $980M (10 years)
EBIT Margin:          10% → 15% (linear expansion)
Enterprise Value:     $902M
Equity Value:         $802M
Value per Share:      $8.02
Terminal Value % EV:  66.7%
```

## 🔧 Functions

### `project_financials(inputs) → DataFrame`
Generates year-by-year projections with Revenue, EBIT, NOPAT, FCF

### `discount_cashflows(df, wacc) → DataFrame`
Adds DiscountFactor and PV_FCF columns

### `terminal_value(last_fcf, wacc, g) → float`
Calculates Gordon Growth terminal value: FCF × (1+g) / (WACC-g)

### `dcf_valuation(inputs) → dict`
Complete valuation orchestration

## ⚠️ Error Handling

```python
try:
    results = dcf_valuation(inputs)
except ValueError as e:
    print(f"Error: {e}")  # Clear message with context
```

Common errors:
- `WACC must exceed terminal_growth`
- `growth_rates length must equal years`
- `revenue0 must be positive`
- `ebit_margin_start must be between 0 and 1`

## 📁 Files

| File | Purpose |
|------|---------|
| `dcf.py` | Core engine (DcfInputs + 4 functions) |
| `app.py` | Streamlit UI |
| `test_dcf.py` | Functional test |
| `test_validation.py` | Validation tests |
| `requirements.txt` | Dependencies |
| `README.md` | User guide |
| `DCF_ENGINE_IMPLEMENTATION.md` | Technical details |
| `IMPLEMENTATION_SUMMARY.md` | Implementation overview |

## 🎯 Common Patterns

### Conservative Valuation
```python
DcfInputs(
    revenue0=500, years=10,
    growth_rates=[0.05]*10,        # Conservative growth
    ebit_margin_start=0.08, ebit_margin_end=0.10,
    tax_rate=0.21, reinvestment_rate=0.50,
    wacc=0.10,                     # Higher discount rate
    terminal_growth=0.02,
    net_debt=100, shares_outstanding=100
)
```

### Growth Company
```python
DcfInputs(
    revenue0=100, years=10,
    growth_rates=[0.30]*3 + [0.20]*3 + [0.10]*4,  # Decelerating
    ebit_margin_start=0.05, ebit_margin_end=0.15,  # Margin expansion
    tax_rate=0.21, reinvestment_rate=0.60,
    wacc=0.12,                     # Higher risk
    terminal_growth=0.03,
    net_debt=-50, shares_outstanding=50  # Net cash
)
```

### Mature Company
```python
DcfInputs(
    revenue0=1000, years=10,
    growth_rates=[0.03]*10,        # Low stable growth
    ebit_margin_start=0.15, ebit_margin_end=0.16,
    tax_rate=0.25, reinvestment_rate=0.25,
    wacc=0.07,                     # Lower risk
    terminal_growth=0.025,
    net_debt=200, shares_outstanding=200
)
```

## 📊 Interpreting Results

**Value Per Share:**
- Compare to current market price
- If higher → potentially undervalued
- If lower → potentially overvalued
- Always check assumptions

**Terminal Value % of Enterprise Value:**
- Typical range: 60-70%
- Higher % = more assumption risk
- Lower % = shorter payback, less terminal value

**FCF Growth Pattern:**
- Should reflect company life cycle
- Early years: high growth (investment phase)
- Later years: deceleration (mature phase)
- Terminal: perpetual growth (typically GDP growth)

## 🚀 Deployment

### Streamlit Cloud
```bash
git push origin main
# Go to streamlit.io/cloud
# Select repo and app.py
# Deploy
```

### Custom Python Script
```python
from dcf import dcf_valuation, DcfInputs
# Use anywhere: CLI, batch, API, notebooks
```

## 📚 Further Reading

- See `DCF_ENGINE_IMPLEMENTATION.md` for technical deep dive
- See `IMPLEMENTATION_SUMMARY.md` for implementation overview
- See `README.md` for full user guide

---

**Status:** ✅ Production-ready
**Tests:** ✅ All passing (functional + validation)
**Documentation:** ✅ Complete
**Ready to use:** ✅ Yes
