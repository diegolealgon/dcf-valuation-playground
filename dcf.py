"""
DCF Valuation Engine for comprehensive financial modeling.

Pure Python functions without Streamlit dependencies.
Handles revenue-to-FCF projections with margin dynamics and terminal value.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np


@dataclass
class DcfInputs:
    """Input parameters for DCF valuation model."""
    
    revenue0: float
    years: int
    growth_rates: List[float]
    ebit_margin_start: float
    ebit_margin_end: float
    tax_rate: float
    reinvestment_rate: float
    wacc: float
    terminal_growth: float
    net_debt: float
    shares_outstanding: float
    
    def __post_init__(self):
        """Validate inputs after initialization."""
        # Revenue validation
        if self.revenue0 <= 0:
            raise ValueError(f"revenue0 must be positive, got {self.revenue0}")
        
        # Years validation
        if self.years <= 0:
            raise ValueError(f"years must be positive, got {self.years}")
        
        # Growth rates validation
        if len(self.growth_rates) != self.years:
            raise ValueError(
                f"growth_rates length ({len(self.growth_rates)}) must equal "
                f"years ({self.years})"
            )
        
        for i, rate in enumerate(self.growth_rates):
            if not isinstance(rate, (int, float)):
                raise ValueError(
                    f"growth_rates[{i}] must be numeric, got {type(rate)}"
                )
            if rate < -0.5:  # Allow negative growth but with bounds
                raise ValueError(
                    f"growth_rates[{i}] = {rate} is unrealistic (< -50%)"
                )
        
        # Margin validation
        if not 0 <= self.ebit_margin_start <= 1:
            raise ValueError(
                f"ebit_margin_start must be between 0 and 1, got {self.ebit_margin_start}"
            )
        if not 0 <= self.ebit_margin_end <= 1:
            raise ValueError(
                f"ebit_margin_end must be between 0 and 1, got {self.ebit_margin_end}"
            )
        
        # Tax rate validation
        if not 0 <= self.tax_rate <= 1:
            raise ValueError(
                f"tax_rate must be between 0 and 1, got {self.tax_rate}"
            )
        
        # Reinvestment rate validation
        if not 0 <= self.reinvestment_rate <= 1:
            raise ValueError(
                f"reinvestment_rate must be between 0 and 1, got {self.reinvestment_rate}"
            )
        
        # WACC validation
        if self.wacc <= 0 or self.wacc >= 1:
            raise ValueError(
                f"wacc must be between 0 and 1 (exclusive), got {self.wacc}"
            )
        
        # Terminal growth validation
        if self.terminal_growth < 0 or self.terminal_growth >= 1:
            raise ValueError(
                f"terminal_growth must be between 0 and 1 (exclusive), got {self.terminal_growth}"
            )
        
        # WACC vs terminal growth check
        if self.wacc <= self.terminal_growth:
            raise ValueError(
                f"WACC ({self.wacc:.1%}) must exceed terminal_growth ({self.terminal_growth:.1%})"
            )
        
        # Net debt validation (can be negative for net cash)
        if not isinstance(self.net_debt, (int, float)):
            raise ValueError(f"net_debt must be numeric, got {type(self.net_debt)}")
        
        # Shares outstanding validation
        if self.shares_outstanding <= 0:
            raise ValueError(
                f"shares_outstanding must be positive, got {self.shares_outstanding}"
            )


def project_financials(inputs: DcfInputs) -> pd.DataFrame:
    """
    Project financial metrics from revenue through free cash flow.
    
    Args:
        inputs: DcfInputs dataclass with model parameters
        
    Returns:
        DataFrame with columns: Year, Revenue, EBITMargin, EBIT, NOPAT, 
                               Reinvestment, FCF
    """
    rows = []
    revenue = inputs.revenue0
    
    for year in range(1, inputs.years + 1):
        # Apply growth rate
        revenue = revenue * (1 + inputs.growth_rates[year - 1])
        
        # Linear interpolation of EBIT margin
        margin_progress = (year - 1) / (inputs.years - 1) if inputs.years > 1 else 0
        ebit_margin = (
            inputs.ebit_margin_start +
            (inputs.ebit_margin_end - inputs.ebit_margin_start) * margin_progress
        )
        
        # Calculate EBIT and NOPAT
        ebit = revenue * ebit_margin
        nopat = ebit * (1 - inputs.tax_rate)
        
        # Reinvestment and FCF
        reinvestment = nopat * inputs.reinvestment_rate
        fcf = nopat - reinvestment
        
        rows.append({
            'Year': year,
            'Revenue': revenue,
            'EBITMargin': ebit_margin,
            'EBIT': ebit,
            'NOPAT': nopat,
            'Reinvestment': reinvestment,
            'FCF': fcf,
        })
    
    return pd.DataFrame(rows)


def discount_cashflows(df: pd.DataFrame, wacc: float) -> pd.DataFrame:
    """
    Add present value columns to financial projections.
    
    Args:
        df: DataFrame with Year and FCF columns (from project_financials)
        wacc: Weighted average cost of capital
        
    Returns:
        DataFrame with added DiscountFactor and PV_FCF columns
    """
    if 'Year' not in df.columns or 'FCF' not in df.columns:
        raise ValueError("DataFrame must contain 'Year' and 'FCF' columns")
    
    df = df.copy()
    df['DiscountFactor'] = (1 + wacc) ** (-df['Year'])
    df['PV_FCF'] = df['FCF'] * df['DiscountFactor']
    
    return df


def terminal_value(last_fcf: float, wacc: float, g: float) -> float:
    """
    Calculate terminal value using Gordon Growth Model (perpetuity growth).
    
    Args:
        last_fcf: Free cash flow in final projection year
        wacc: Weighted average cost of capital
        g: Perpetual growth rate
        
    Returns:
        Terminal value
        
    Raises:
        ValueError: If WACC <= perpetual growth rate or invalid inputs
    """
    if not isinstance(last_fcf, (int, float)):
        raise ValueError(f"last_fcf must be numeric, got {type(last_fcf)}")
    if not isinstance(wacc, (int, float)):
        raise ValueError(f"wacc must be numeric, got {type(wacc)}")
    if not isinstance(g, (int, float)):
        raise ValueError(f"g must be numeric, got {type(g)}")
    
    if last_fcf < 0:
        raise ValueError(f"last_fcf must be non-negative, got {last_fcf}")
    
    if wacc <= g:
        raise ValueError(
            f"WACC ({wacc:.1%}) must strictly exceed perpetual growth ({g:.1%}). "
            f"Difference: {(wacc - g):.2%}"
        )
    
    return last_fcf * (1 + g) / (wacc - g)


def dcf_valuation(inputs: DcfInputs) -> Dict:
    """
    Complete DCF valuation: project financials, discount, and value equity.
    
    Args:
        inputs: DcfInputs dataclass with all model assumptions
        
    Returns:
        Dictionary with keys:
            - enterprise_value: Total firm value
            - equity_value: Enterprise value - net debt
            - value_per_share: Equity value / shares outstanding
            - pv_fcf: Present value of projected FCFs
            - pv_terminal: Present value of terminal value
            - df: Full projection DataFrame with PV columns
    """
    # Project financials
    df = project_financials(inputs)
    
    # Discount cash flows
    df = discount_cashflows(df, inputs.wacc)
    
    # Calculate terminal value
    last_fcf = df['FCF'].iloc[-1]
    tv = terminal_value(last_fcf, inputs.wacc, inputs.terminal_growth)
    
    # Discount terminal value
    terminal_discount_factor = (1 + inputs.wacc) ** (-inputs.years)
    pv_terminal_value = tv * terminal_discount_factor
    
    # Sum present values
    pv_fcf_total = df['PV_FCF'].sum()
    enterprise_value = pv_fcf_total + pv_terminal_value
    
    # Equity value
    equity_value = enterprise_value - inputs.net_debt
    
    # Value per share
    if inputs.shares_outstanding <= 0:
        raise ValueError("shares_outstanding must be positive for per-share valuation")
    
    value_per_share = equity_value / inputs.shares_outstanding
    
    return {
        'enterprise_value': enterprise_value,
        'equity_value': equity_value,
        'value_per_share': value_per_share,
        'pv_fcf': pv_fcf_total,
        'pv_terminal': pv_terminal_value,
        'df': df,
    }


def sensitivity_table(
    inputs: DcfInputs,
    wacc_values: List[float],
    g_values: List[float]
) -> pd.DataFrame:
    """
    Generate sensitivity analysis table for value per share.
    
    Creates a table where rows represent terminal growth rates and 
    columns represent WACC values. Each cell contains the value per share
    for that combination of assumptions.
    
    Args:
        inputs: Base case DcfInputs with all assumptions
        wacc_values: List of WACC values (as decimals, e.g., 0.08 for 8%)
        g_values: List of terminal growth rates (as decimals, e.g., 0.025 for 2.5%)
        
    Returns:
        pandas.DataFrame with:
            - Index: g_values (terminal growth rates) 
            - Columns: wacc_values (WACC values)
            - Values: value_per_share for each combination
            - NaN for invalid combinations (WACC <= terminal growth)
    """
    # Sort values for better table readability
    wacc_vals = sorted(wacc_values)
    g_vals = sorted(g_values)
    
    # Initialize result matrix
    sensitivity_data = []
    
    for g in g_vals:
        row = []
        for wacc in wacc_vals:
            if wacc <= g:
                # Invalid combination: WACC must exceed terminal growth
                row.append(np.nan)
            else:
                try:
                    # Create modified inputs with this WACC and terminal growth
                    test_inputs = DcfInputs(
                        revenue0=inputs.revenue0,
                        years=inputs.years,
                        growth_rates=inputs.growth_rates,
                        ebit_margin_start=inputs.ebit_margin_start,
                        ebit_margin_end=inputs.ebit_margin_end,
                        tax_rate=inputs.tax_rate,
                        reinvestment_rate=inputs.reinvestment_rate,
                        wacc=wacc,
                        terminal_growth=g,
                        net_debt=inputs.net_debt,
                        shares_outstanding=inputs.shares_outstanding,
                    )
                    
                    # Run valuation
                    results = dcf_valuation(test_inputs)
                    row.append(results['value_per_share'])
                    
                except (ValueError, ZeroDivisionError):
                    row.append(np.nan)
        
        sensitivity_data.append(row)
    
    # Create DataFrame with proper labeling
    df_sensitivity = pd.DataFrame(
        sensitivity_data,
        index=g_vals,
        columns=wacc_vals
    )
    
    # Format index and column names for readability
    df_sensitivity.index.name = 'Terminal Growth (g)'
    df_sensitivity.columns.name = 'WACC'
    
    return df_sensitivity
