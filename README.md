# Stock Breakout Analyzer

A Python-based web application that analyzes stock volume and price breakouts. The tool identifies potential breakout opportunities based on customizable volume thresholds and price changes, calculates holding period returns, and provides detailed statistical analysis with interactive visualizations.

## Features

- **Volume Breakout Detection**: Identifies days where volume exceeds historical averages by a user-defined threshold
- **Price Movement Analysis**: Filters for significant price movements above specified thresholds
- **Customizable Parameters**:
  - Volume threshold percentage
  - Price change threshold
  - Holding period duration
  - Date range selection
- **Interactive Visualizations**: Distribution of returns and performance metrics
- **Statistical Analysis**: Win rate, average return, maximum return, and other key metrics
- **Data Export**: Download results as CSV for further analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-breakout-analyzer.git
cd stock-breakout-analyzer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the web interface (typically at http://localhost:8501)

3. Enter analysis parameters:
   - Stock ticker symbol (e.g., AAPL)
   - Start and end dates for analysis
   - Volume breakout threshold (minimum % above 20-day average)
   - Daily price change threshold (minimum % increase)
   - Holding period (number of days to hold after breakout)

4. Click "Generate Report" to run the analysis

## Sample Analysis

Here's how to perform a basic analysis:

1. Enter "AAPL" as the ticker
2. Set date range (e.g., last 12 months)
3. Set volume threshold to 200%
4. Set price threshold to 2%
5. Set holding period to 10 days
6. Generate report and view results

The tool will display:
- Summary statistics
- Detailed trade results
- Return distribution visualization
- Option to download results as CSV

## Technical Details

### Data Source
- Stock data is fetched using the `yfinance` library
- 20-day moving average is used for volume comparison
- Adjusted closing prices are used for return calculations

### Breakout Detection Logic
```python
# Volume condition
Volume_Today > (Volume_MA20 * threshold_percentage)

# Price condition
Price_Change_Today > price_threshold
```

### Return Calculation
```python
Return = (Exit_Price - Entry_Price) / Entry_Price * 100
```

## Dependencies

- streamlit
- yfinance
- pandas
- numpy
- plotly
- python-dateutil

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice, and any trading decisions should be made after thorough research and consultation with financial professionals.

## Contact

Your Name - Sashrik Rajesh
Project Link: 

## Acknowledgments

- `yfinance` for providing access to market data
- Streamlit for the web application framework
- Plotly for interactive visualizations
