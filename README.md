# DCF Valuation Playground

An interactive educational tool for discounted cash flow (DCF) valuation analysis, built with Streamlit.

## Overview

DCF Valuation Playground provides an intuitive interface to explore company valuation using the discounted cash flow method. Adjust assumptions in real-time and visualize how changes impact enterprise value and equity value per share.

**⚠️ Disclaimer:** This tool is for educational purposes only and should not be used as financial advice. Always consult with a qualified financial advisor before making investment decisions.

## Features

- **Interactive Valuation Model**: Adjust company assumptions and see real-time valuation updates
- **FCF Projections**: Visualize projected free cash flows over your selected period
- **Sensitivity Analysis**: Explore value ranges across different WACC and growth rate assumptions
- **Detailed Breakdown**: Review present values, discount factors, and terminal value composition
- **Professional Charts**: Interactive visualizations with Plotly for insights and exploration

## Key Assumptions

The model uses the following assumptions:

### Input Parameters
- **Initial FCF**: Year 1 free cash flow (customizable)
- **FCF Growth Rate**: Expected annual growth rate during projection period
- **Projection Period**: Years to project explicit FCFs (typically 5-10 years)
- **Terminal Growth Rate**: Perpetual growth rate for terminal value calculation
- **WACC**: Weighted Average Cost of Capital used for discounting
- **Net Debt**: Total debt minus cash and equivalents
- **Shares Outstanding**: Number of shares for per-share valuation

### Model Methodology
1. **FCF Projection**: Projects free cash flows using constant growth rate
2. **Terminal Value**: Calculated using Gordon Growth Model (perpetuity growth method)
3. **Present Value**: Discounts all cash flows using WACC
4. **Enterprise Value**: Sum of PV(FCFs) + PV(Terminal Value)
5. **Equity Value**: Enterprise Value - Net Debt
6. **Value per Share**: Equity Value / Shares Outstanding

### Limitations
- Assumes constant growth rates (simplified model)
- Does not account for seasonality or business cycles
- Terminal value calculations assume stable perpetual growth
- Does not incorporate tax, capital structure changes, or working capital adjustments

## How to Run Locally

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone or download the project:**
   ```bash
   cd dcf_example
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

## How to Deploy on Streamlit Community Cloud

### Step 1: Prepare Your Repository
1. Push your project to GitHub (public repository recommended for Community Cloud)
2. Ensure all files are in the root or appropriate subdirectory

### Step 2: Deploy on Streamlit Cloud
1. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
2. Click "New app" and sign in with your GitHub account
3. Select your repository, branch, and the `app.py` file
4. Click "Deploy"

### Step 3: Configuration (Optional)
- Customize app settings in `.streamlit/config.toml`
- Monitor app logs in the Streamlit Cloud dashboard
- Share your app URL with others

### Environment Variables
If needed, add secrets via the Streamlit Cloud dashboard:
1. Go to your app settings
2. Add secrets in the "Secrets" section
3. Access them in code with `st.secrets`

**Example:** `streamlit run://dcf-valuation-playground.streamlit.app`

## Project Structure

```
dcf_example/
├── app.py                 # Streamlit application UI
├── dcf.py                 # Pure Python DCF valuation functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore           # Git ignore patterns
```

## Usage Guide

### Basic Workflow
1. **Enter Company Assumptions**: Name, shares outstanding in the sidebar
2. **Set Financial Inputs**: Initial FCF, growth rates, projection period
3. **Configure Valuation Parameters**: WACC, net debt
4. **Review Results**: Enterprise value, equity value, value per share
5. **Analyze Sensitivity**: Adjust ranges to explore valuation drivers
6. **Export Insights**: Take screenshots or note key metrics

### Tips for Realistic Valuations
- **WACC**: Typically ranges from 5-12% depending on company risk
- **FCF Growth**: Consider historical growth and industry averages
- **Terminal Growth**: Usually 2-3% (GDP growth proxy)
- **Projection Period**: 5-10 years is standard for mature companies
- **Validate**: Compare results with other valuation methods

## Technical Details

### Dependencies
- **Streamlit**: Web app framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations

### Code Organization
- `dcf.py`: Pure functions with no Streamlit dependencies for reusability
- `app.py`: Streamlit-specific UI and interactivity

## Contributing

This is an educational project. Feel free to:
- Extend the model with additional features
- Add more sophisticated DCF methodologies
- Improve visualizations
- Report issues or suggest enhancements

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

**Educational Use Only**: This tool is designed for learning about DCF valuation concepts and should not be used for actual financial decision-making.

**Not Financial Advice**: Nothing in this tool should be interpreted as financial advice. Valuation is complex and requires careful analysis of company fundamentals, market conditions, and competitive dynamics.

**No Warranties**: The calculations and results are provided "as-is" without any guarantees of accuracy. Always validate assumptions and consult with qualified financial professionals.

---

**Last Updated**: February 2026
