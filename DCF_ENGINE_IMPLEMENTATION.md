# DCF Valuation Engine Implementation Summary

## Overview
A complete, production-ready DCF valuation engine with comprehensive input validation, flexible financial modeling, and detailed error messaging.

---

## Implementation Details

### 1. **DcfInputs Dataclass** (`dcf.py`)

**Purpose:** Container for all DCF model assumptions with built-in validation.

**Fields:**
| Field | Type | Description | Valid Range |
|-------|------|-------------|-------------|
| `revenue0` | float | Year 0 base revenue | > 0 |
| `years` | int | Projection period in years | > 0 |
| `growth_rates` | List[float] | Annual growth rates (must have length = years) | -50% to 30% |
| `ebit_margin_start` | float | Starting EBIT margin (% of revenue) | 0 to 1 |
| `ebit_margin_end` | float | Ending EBIT margin after linear interpolation | 0 to 1 |
| `tax_rate` | float | Corporate tax rate | 0 to 1 |
| `reinvestment_rate` | float | Reinvestment as % of NOPAT | 0 to 1 |
| `wacc` | float | Weighted Average Cost of Capital | 0 < x < 1 |
| `terminal_growth` | float | Perpetual long-term growth rate | 0 ≤ x < 1 |
| `net_debt` | float | Total debt minus cash | any value |
| `shares_outstanding` | float | Shares outstanding (in millions) | > 0 |

**Validation (`__post_init__` method):**
- ✓ Revenue must be positive
- ✓ Years must be positive
- ✓ Growth rates list length must equal years
- ✓ Each growth rate must be numeric and >= -50%
- ✓ Margins must be in [0, 1]
- ✓ Tax rate must be in [0, 1]
- ✓ Reinvestment rate must be in [0, 1]
- ✓ WACC must be in (0, 1) exclusive
- ✓ Terminal growth must be in [0, 1)
- ✓ **CRITICAL: WACC > terminal_growth** (enforced before any calculations)
- ✓ Shares outstanding must be positive

---

### 2. **Core Functions**

#### `project_financials(inputs: DcfInputs) -> pd.DataFrame`

**Purpose:** Generate year-by-year revenue and free cash flow projections.

**Process:**
1. **Revenue Growth:** Applies annual growth rates to base revenue
   ```
   Revenue_t = Revenue_(t-1) × (1 + growth_rate_t)
   ```

2. **EBIT Margin Progression:** Linear interpolation from start to end margin
   ```
   Margin_t = start + (end - start) × (t-1) / (years-1)
   ```

3. **EBIT Calculation:** Revenue × EBIT Margin

4. **NOPAT (Net Operating Profit After Tax):**
   ```
   NOPAT = EBIT × (1 - tax_rate)
   ```

5. **Reinvestment:** Capital expenditures and working capital changes
   ```
   Reinvestment = NOPAT × reinvestment_rate
   ```

6. **Free Cash Flow:** Available to all investors (debt and equity)
   ```
   FCF = NOPAT - Reinvestment
   ```

**Output Columns:**
- Year: 1 to N
- Revenue: Projected annual revenue
- EBITMargin: EBIT as % of revenue
- EBIT: Earnings before interest and taxes
- NOPAT: Operating profit after taxes
- Reinvestment: Reinvestment needs
- FCF: Free cash flow

**Example:**
```
For a company with $500M base revenue, 10% growth, 10→15% margin expansion:
Year 1: $550M revenue, 10.0% margin = $55M EBIT → $43.4M NOPAT → $26.1M FCF
Year 10: $979.7M revenue, 15.0% margin = $147M EBIT → $116.1M NOPAT → $69.7M FCF
```

---

#### `discount_cashflows(df: pd.DataFrame, wacc: float) -> pd.DataFrame`

**Purpose:** Convert nominal FCFs to present values.

**Calculation:**
```
DiscountFactor_t = 1 / (1 + WACC)^t
PV_FCF_t = FCF_t × DiscountFactor_t
```

**Output Additions:**
- DiscountFactor: Discount factor for each year
- PV_FCF: Present value of free cash flow

**Example:**
```
Year 1: FCF=$26.1M, DF=0.9259 (8% WACC) → PV=$24.1M
Year 10: FCF=$69.7M, DF=0.4632 → PV=$32.3M
```

---

#### `terminal_value(last_fcf: float, wacc: float, g: float) -> float`

**Purpose:** Calculate value of company beyond explicit projection period.

**Method:** Gordon Growth Model (Perpetuity Growth)

**Formula:**
```
Terminal Value = FCF_final × (1 + g) / (WACC - g)
```

**Guardrails:**
- ✓ All inputs must be numeric
- ✓ last_fcf must be non-negative
- ✓ **CRITICAL: WACC must strictly exceed g**, with clear error message showing the gap

**Example:**
```
Last FCF: $69.7M
WACC: 8.0%, Terminal Growth: 2.5%
TV = $69.7M × 1.025 / 0.055 = $1,301M
```

**Why This Matters:**
Terminal value typically represents 60-70% of enterprise value. Small errors in WACC or terminal growth assumptions create large valuation swings.

---

#### `dcf_valuation(inputs: DcfInputs) -> Dict`

**Purpose:** Complete end-to-end DCF valuation orchestration.

**Process:**
1. Call `project_financials()` to build 10-year projection
2. Call `discount_cashflows()` to calculate PV of FCFs
3. Call `terminal_value()` to estimate company value after projection
4. Discount terminal value to present
5. Sum all present values for enterprise value
6. Subtract net debt to get equity value
7. Divide by shares to get per-share value

**Output Dictionary:**
```python
{
    'enterprise_value': float,    # Total firm value (debt + equity)
    'equity_value': float,        # Value available to equity holders
    'value_per_share': float,     # Price per share
    'pv_fcf': float,             # Sum of discounted projected FCFs
    'pv_terminal': float,        # Present value of terminal value
    'df': pd.DataFrame            # Full projection with PV columns
}
```

**Typical Results:**
```
TechCorp Inc Example:
  Enterprise Value:  $902M (300M from projections, 601M from terminal)
  Equity Value:      $802M (after subtracting $100M net debt)
  Value per Share:   $8.02 (for 100M shares)
  Terminal as % of EV: 66.7% (typical range is 60-70%)
```

---

## Validation Summary

### Input Validation Points

1. **Structural Validation**
   - Revenue, years, shares must be positive
   - Growth rates list length matches years
   - All numeric fields are actual numbers

2. **Bounds Validation**
   - Margins: [0, 1]
   - Tax rate: [0, 1]
   - Reinvestment rate: [0, 1]
   - WACC: (0, 1) exclusive
   - Terminal growth: [0, 1)
   - Growth rates: [-50%, 30%]

3. **Financial Feasibility**
   - **WACC must strictly exceed terminal growth** (checked in `__post_init__` AND `terminal_value()`)
   - Clear error messages show actual vs. required values

### Error Messages

All validation errors provide:
- ✓ What went wrong
- ✓ What was provided
- ✓ What range/condition is required
- ✓ Why it matters (for WACC vs growth)

**Example:**
```
ValueError: WACC (2.5%) must exceed terminal_growth (2.5%). Difference: 0.00%
```

---

## Test Results

### Functional Test (test_dcf.py)
```
✅ TechCorp Inc Example:
   Enterprise Value:        $902M
   Equity Value:            $802M
   Value per Share:         $8.02
   PV of Projected FCFs:    $300M
   PV of Terminal Value:    $601M
   Terminal Value % of EV:  66.7%

Year-by-year progression verified:
   - Revenue grows from $550M (Year 1) to $980M (Year 10)
   - EBIT margin expands linearly from 10% to 15%
   - FCF grows from $26.1M to $69.7M
```

### Validation Test (test_validation.py)
```
✅ All 7 validation tests passed:
   1. WACC <= terminal_growth → ValueError
   2. Growth rates length mismatch → ValueError
   3. EBIT margin > 1 → ValueError
   4. Terminal value with WACC < g → ValueError
   5. Negative revenue → ValueError
   6. Tax rate > 1 → ValueError
   7. Reinvestment rate > 1 → ValueError
```

---

## Integration with Streamlit App

The DCF engine integrates seamlessly with `app.py`:

1. **User Input Collection:** Sidebar gathers all DcfInputs parameters
2. **Instance Creation:** Creates DcfInputs dataclass (validation runs automatically)
3. **Valuation Execution:** Calls `dcf_valuation(inputs)`
4. **Results Display:** Metrics, tables, and charts from returned dictionary
5. **Error Handling:** ValueError exceptions caught and displayed to user

**Flow:**
```
User Input (Streamlit) → DcfInputs creation (validates) → dcf_valuation()
    ↓
   Results dict → Extract enterprise_value, equity_value, value_per_share
    ↓
Display metrics, projections table, visualizations
```

---

## Key Assumptions & Limitations

### Assumptions Baked Into Model
- **Linear Margin Progression:** EBIT margin changes linearly (simplified, not circular)
- **Constant Reinvestment Rate:** Same % of NOPAT reinvested each year
- **Single Tax Rate:** No tax rate changes during projection
- **Gordon Growth Terminal:** Assumes company reaches steady state perpetual growth
- **No Capital Structure Changes:** Debt/equity ratio static

### Limitations
- **Deterministic Only:** No sensitivity analysis or Monte Carlo
- **Simplified Operations:** No working capital modeling, seasonal adjustments, or M&A
- **Terminal Value Dominance:** Results highly sensitive to WACC and terminal growth (typically 60-70% of value)
- **Historical Data Not Used:** Pure forward-looking, doesn't validate against actuals

### Usage Best Practices
- ✓ Validate against other valuation methods (comparable companies, precedent transactions)
- ✓ Perform sensitivity analysis on WACC and terminal growth
- ✓ Use conservative terminal growth (2-3% for mature companies)
- ✓ Build 5-10 year projections (shorter = higher terminal %, more risk)
- ✓ Always include a disclaimer (educational/research only)

---

## Files Included

| File | Purpose |
|------|---------|
| `dcf.py` | Core DCF engine (DcfInputs class + 4 functions) |
| `app.py` | Streamlit interactive UI |
| `test_dcf.py` | Functional test with TechCorp example |
| `test_validation.py` | Validation test suite (7 tests) |
| `requirements.txt` | Python dependencies |
| `README.md` | User documentation |
| `.gitignore` | Git ignore patterns |
| `LICENSE` | MIT License |

---

## Example Usage

```python
from dcf import DcfInputs, dcf_valuation

# Define assumptions
inputs = DcfInputs(
    revenue0=500.0,
    years=10,
    growth_rates=[0.10]*5 + [0.04]*5,    # Decelerate over time
    ebit_margin_start=0.10,               # 10% initially
    ebit_margin_end=0.15,                 # 15% at year 10
    tax_rate=0.21,
    reinvestment_rate=0.40,
    wacc=0.08,
    terminal_growth=0.025,
    net_debt=100.0,
    shares_outstanding=100.0
)

# Run valuation (validation runs in __post_init__)
results = dcf_valuation(inputs)

# Access results
print(f"Value per share: ${results['value_per_share']:.2f}")
print(f"Enterprise value: ${results['enterprise_value']:.0f}M")
print(f"Terminal value contribution: {results['pv_terminal']/results['enterprise_value']*100:.1f}%")

# Access full projection
df = results['df']
print(df[['Year', 'Revenue', 'EBIT', 'FCF', 'PV_FCF']])
```

---

## Summary

✅ **Complete DCF Engine**
- DcfInputs dataclass with comprehensive validation
- Revenue-to-FCF projection with dynamic margins
- Present value calculations with WACC discounting
- Terminal value using Gordon Growth Model
- End-to-end orchestration function

✅ **Robust Error Handling**
- 14+ validation checks with clear error messages
- Critical guardrail: WACC > terminal growth
- Type checking and bounds validation

✅ **Well-Tested**
- Functional test with realistic TechCorp example
- 7-test validation suite (all passing)
- Integration with Streamlit UI verified

✅ **Production-Ready**
- Pure Python (no external dependencies except pandas/numpy)
- Reusable for any application (Streamlit, CLI, API, batch processing)
- Clean code structure and documentation

