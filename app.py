# Import required libraries
import streamlit as st  # For web interface
import yfinance as yf  # For fetching stock data
import pandas as pd    # For data manipulation
import numpy as np     # For numerical operations
from datetime import datetime, timedelta  # For date handling
import plotly.graph_objects as go  # For interactive plots
from io import BytesIO  # For handling file downloads

def get_stock_data(ticker, start_date, end_date):
    """
    Fetch stock data using yfinance, ensuring we get enough historical data
    for the moving average calculation
    
    Args:
        ticker (str): Stock symbol (e.g., 'AAPL')
        start_date (datetime): Beginning of analysis period
        end_date (datetime): End of analysis period
        
    Returns:
        DataFrame: Stock data with OHLCV information
    """
    # Add 30 extra days to start_date to account for the 20-day moving average calculation
    # This prevents lookback bias at the start of our analysis period
    adjusted_start = (pd.to_datetime(start_date) - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=adjusted_start, end=end_date)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def analyze_breakouts(df, volume_threshold, price_threshold, holding_period):
    """
    Analyze stock data for breakout conditions and calculate returns
    
    Args:
        df (DataFrame): Stock price data
        volume_threshold (float): Minimum volume increase percentage vs 20-day average
        price_threshold (float): Minimum price increase percentage for the day
        holding_period (int): Number of days to hold each position
        
    Returns:
        DataFrame: Results of breakout analysis with entry/exit points and returns
    """
    # Calculate 20-day moving average of volume for baseline
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
    
    # Calculate day-over-day price changes
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Calculate volume ratio (today's volume / 20-day average)
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
    
    # Identify days that meet both volume and price criteria for a breakout
    breakout_condition = (df['Volume_Ratio'] > volume_threshold/100) & \
                        (df['Daily_Return'] > price_threshold/100)
    
    # Storage for our analysis results
    breakout_results = []
    
    # Get all days where breakout conditions were met
    breakout_days = df[breakout_condition].index
    
    # Analyze each breakout event
    for breakout_day in breakout_days:
        try:
            # Get entry price (close price on breakout day)
            entry_price = df.loc[breakout_day, 'Close']
            entry_date = breakout_day
            
            # Calculate exit point based on holding period
            # If holding period would exceed our data, use last available day
            exit_date_idx = min(df.index.get_loc(breakout_day) + holding_period, len(df) - 1)
            exit_date = df.index[exit_date_idx]
            exit_price = df.iloc[exit_date_idx]['Close']
            
            # Calculate percentage return for this trade
            trade_return = (exit_price - entry_price) / entry_price * 100
            
            # Store results for this breakout event
            breakout_results.append({
                'Entry_Date': entry_date.strftime('%Y-%m-%d'),
                'Entry_Price': round(entry_price, 2),
                'Exit_Date': exit_date.strftime('%Y-%m-%d'),
                'Exit_Price': round(exit_price, 2),
                'Return_Pct': round(trade_return, 2),
                'Volume_Ratio': round(df.loc[breakout_day, 'Volume_Ratio'], 2)
            })
        except Exception as e:
            st.warning(f"Could not calculate returns for breakout on {breakout_day}: {str(e)}")
            continue
            
    return pd.DataFrame(breakout_results)

def create_summary_stats(results_df):
    """
    Calculate summary statistics for the breakout strategy
    
    Args:
        results_df (DataFrame): DataFrame containing all breakout trade results
        
    Returns:
        Series: Summary statistics including win rate and returns metrics
    """
    # Handle case where no breakouts were found
    if len(results_df) == 0:
        return pd.Series({
            'Total_Trades': 0,
            'Win_Rate': 0,
            'Average_Return': 0,
            'Max_Return': 0,
            'Min_Return': 0,
            'Std_Dev': 0
        })
    
    # Calculate strategy performance metrics    
    summary = {
        'Total_Trades': len(results_df),
        'Win_Rate': (results_df['Return_Pct'] > 0).mean() * 100,  # Percentage of profitable trades
        'Average_Return': results_df['Return_Pct'].mean(),        # Average return per trade
        'Max_Return': results_df['Return_Pct'].max(),            # Best performing trade
        'Min_Return': results_df['Return_Pct'].min(),            # Worst performing trade
        'Std_Dev': results_df['Return_Pct'].std()                # Volatility of returns
    }
    return pd.Series(summary).round(2)

# Set up the Streamlit web interface
st.title('Stock Breakout Analysis Tool')

# Create two-column layout for input parameters
col1, col2 = st.columns(2)

# Left column inputs
with col1:
    ticker = st.text_input('Stock Ticker', value='AAPL').upper()
    start_date = st.date_input('Start Date', 
                              value=datetime.now() - timedelta(days=365))
    end_date = st.date_input('End Date', 
                            value=datetime.now())

# Right column inputs
with col2:
    volume_threshold = st.number_input('Volume Breakout Threshold (%)', 
                                     value=200, min_value=100)
    price_threshold = st.number_input('Daily Change Threshold (%)', 
                                    value=2.0, min_value=0.0)
    holding_period = st.number_input('Holding Period (Days)', 
                                   value=10, min_value=1)

# Analysis trigger button
if st.button('Generate Report'):
    # Get historical data
    df = get_stock_data(ticker, start_date, end_date)
    
    if df is not None and not df.empty:
        # Perform breakout analysis
        results_df = analyze_breakouts(df, volume_threshold, price_threshold, holding_period)
        
        if not results_df.empty:
            # Display results section
            
            # 1. Summary Statistics
            st.subheader('Summary Statistics')
            summary_stats = create_summary_stats(results_df)
            st.dataframe(pd.DataFrame(summary_stats).T)
            
            # 2. Detailed Trade Results
            st.subheader('Detailed Trade Results')
            st.dataframe(results_df)
            
            # 3. Visual Distribution of Returns
            fig = go.Figure(data=[go.Histogram(x=results_df['Return_Pct'], 
                                             nbinsx=20,
                                             name='Returns Distribution')])
            fig.update_layout(title='Distribution of Returns',
                            xaxis_title='Return (%)',
                            yaxis_title='Frequency')
            st.plotly_chart(fig)
            
            # 4. CSV Download Option
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name=f"{ticker}_breakout_analysis.csv",
                mime="text/csv"
            )
        else:
            st.warning('No breakout conditions found for the given parameters.')
    else:
        st.error('No data available for the selected date range.')