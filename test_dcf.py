#!/usr/bin/env python3
"""Test script for DCF valuation engine."""

from dcf import DcfInputs, dcf_valuation

def main():
    # Create test inputs for a fictional company
    inputs = DcfInputs(
        revenue0=500.0,                    # $500M base revenue
        years=10,                           # 10-year projection
        growth_rates=[0.10]*5 + [0.04]*5,  # 10% growth for 5 years, then 4%
        ebit_margin_start=0.10,             # Start at 10% EBIT margin
        ebit_margin_end=0.15,               # End at 15% EBIT margin
        tax_rate=0.21,                      # 21% tax rate
        reinvestment_rate=0.40,             # 40% of NOPAT reinvested
        wacc=0.08,                          # 8% WACC
        terminal_growth=0.025,              # 2.5% terminal growth
        net_debt=100.0,                     # $100M net debt
        shares_outstanding=100.0            # 100M shares
    )

    # Run valuation
    results = dcf_valuation(inputs)

    # Print summary
    print("\n" + "="*70)
    print("DCF VALUATION RESULTS - TechCorp Inc (Fictional Company)")
    print("="*70)
    print(f"\nEnterprise Value:       ${results['enterprise_value']:>14,.0f}M")
    print(f"Equity Value:           ${results['equity_value']:>14,.0f}M")
    print(f"Value per Share:        ${results['value_per_share']:>14,.2f}")
    
    print(f"\nPV of Projected FCFs:   ${results['pv_fcf']:>14,.0f}M")
    print(f"PV of Terminal Value:   ${results['pv_terminal']:>14,.0f}M")
    terminal_pct = (results['pv_terminal'] / results['enterprise_value'] * 100)
    print(f"Terminal Value % of EV:  {terminal_pct:>13.1f}%")

    print("\n" + "-"*70)
    print("YEAR-BY-YEAR FINANCIAL PROJECTIONS ($ millions)")
    print("-"*70)

    df = results['df'].copy()
    df['EBITMargin%'] = df['EBITMargin'] * 100
    
    # Format and display
    display_cols = ['Year', 'Revenue', 'EBITMargin%', 'EBIT', 'NOPAT', 'Reinvestment', 'FCF', 'PV_FCF']
    display_df = df[display_cols].copy()
    for col in ['Revenue', 'EBIT', 'NOPAT', 'Reinvestment', 'FCF', 'PV_FCF']:
        display_df[col] = display_df[col].round(1)
    display_df['EBITMargin%'] = display_df['EBITMargin%'].round(1)
    
    print(display_df.to_string(index=False))

    print("\n" + "="*70)
    print("✅ DCF Engine Test Successful!")
    print("="*70)

if __name__ == "__main__":
    main()
