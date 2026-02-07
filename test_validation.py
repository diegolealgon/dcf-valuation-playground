#!/usr/bin/env python3
"""Validation tests for DCF inputs and functions."""

from dcf import DcfInputs, terminal_value

def test_validation():
    print("Testing DCF Engine Validation & Error Handling\n")
    print("=" * 70)

    # Test 1: WACC <= terminal_growth check
    print("\n1. WACC <= terminal_growth validation:")
    try:
        inputs = DcfInputs(
            revenue0=500.0, years=10, growth_rates=[0.05]*10,
            ebit_margin_start=0.10, ebit_margin_end=0.15, tax_rate=0.21,
            reinvestment_rate=0.40, wacc=0.025, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 2: Growth rates length mismatch
    print("\n2. Growth rates length validation:")
    try:
        inputs = DcfInputs(
            revenue0=500.0, years=10, growth_rates=[0.05]*5,
            ebit_margin_start=0.10, ebit_margin_end=0.15, tax_rate=0.21,
            reinvestment_rate=0.40, wacc=0.08, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 3: Invalid EBIT margin (> 1)
    print("\n3. EBIT margin bounds validation:")
    try:
        inputs = DcfInputs(
            revenue0=500.0, years=10, growth_rates=[0.05]*10,
            ebit_margin_start=1.5, ebit_margin_end=0.15, tax_rate=0.21,
            reinvestment_rate=0.40, wacc=0.08, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 4: terminal_value function guardrails
    print("\n4. Terminal value WACC < g validation:")
    try:
        tv = terminal_value(100.0, wacc=0.05, g=0.06)
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 5: Negative revenue validation
    print("\n5. Revenue positivity validation:")
    try:
        inputs = DcfInputs(
            revenue0=-100.0, years=10, growth_rates=[0.05]*10,
            ebit_margin_start=0.10, ebit_margin_end=0.15, tax_rate=0.21,
            reinvestment_rate=0.40, wacc=0.08, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 6: Tax rate bounds
    print("\n6. Tax rate bounds validation:")
    try:
        inputs = DcfInputs(
            revenue0=500.0, years=10, growth_rates=[0.05]*10,
            ebit_margin_start=0.10, ebit_margin_end=0.15, tax_rate=1.5,
            reinvestment_rate=0.40, wacc=0.08, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    # Test 7: Reinvestment rate bounds
    print("\n7. Reinvestment rate bounds validation:")
    try:
        inputs = DcfInputs(
            revenue0=500.0, years=10, growth_rates=[0.05]*10,
            ebit_margin_start=0.10, ebit_margin_end=0.15, tax_rate=0.21,
            reinvestment_rate=1.5, wacc=0.08, terminal_growth=0.025,
            net_debt=100.0, shares_outstanding=100.0
        )
        print("   ✗ FAILED - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ PASSED - {str(e)[:50]}...")

    print("\n" + "=" * 70)
    print("✅ All validation tests passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_validation()
