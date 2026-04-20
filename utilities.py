import csv
from matplotlib import ticker
import numpy as np
import pandas as pd
#Adapted from D-Wave Systems portfolio optimization training project

# Prepare Stock data from the csv files
def get_tickers(verbose=False):
    df = pd.read_csv('data/lastprice_data.csv')
    tickers = df['Ticker'].astype(str).tolist()
    if verbose:
        print(tickers)
        print(len(tickers))
    return tickers

# Generate stock data
def get_stock_info(pass_no = 1, df_firstpass = None, coskew_compute = False, verbose=True):
    # Read in stock returns and price information from CSV
    df_price = pd.read_csv('data/lastprice_data.csv')
    print(df_price.head())

    ############### calculate mean returns #############################
    df_dailyreturn = pd.read_csv('data/returns_data.csv', index_col='Date')

    if pass_no == 2:
      df_price = pd.merge(df_price, df_firstpass, on = ['Ticker'])
      columnlist = df_firstpass['Ticker'].astype(str).tolist()
      df_dailyreturn = df_dailyreturn[columnlist]

    avg_daily_returns = df_dailyreturn.mean(axis=0)
    annual_returns = avg_daily_returns * 252
    returns = list(annual_returns)

    ############# calculate variance ###################################
    covariance = (df_dailyreturn.cov() * 252).values.tolist()
    
    ############ calculate coskew tensor ###############################
    if (len(annual_returns) <=5000) and (coskew_compute == True):
      returns_array = df_dailyreturn.to_numpy(dtype='float32')
      print(returns_array)
      # Standardize the returns: (R - mu) / sigma 
      mu = np.mean(returns_array, axis=0)
      print("MEAN RETURNS ARRAY")
      print(mu)
      sigma = np.std(returns_array, axis=0)
      print("SIGMA ARRAY")  
      print(sigma)
      z_scores = (returns_array - mu) / sigma
  
      # Calculate the Coskewness Tensor 
      # Using Einstein Summation:
      # t is day, i, j, k are individual stocks
      # Multiply z_i * z_j * z_k for every day and average. 
      coskew_tensor = np.einsum('ti,tj,tk->ijk', z_scores, z_scores, z_scores) / returns_array.shape[0]

      print(f"Tensor Shape: {coskew_tensor.shape}")
      # Accessing S(X, Y, Z) for stocks 0, 1, and 2:
      print(f"Coskew (0,1,2): {coskew_tensor[0, 1, 2]:.4f}")  
    else:
        coskew_tensor = None

    if verbose:
        print("Data Check")
        print(f"Length of Price Array: {len(df_price)}")
        print("Return(the first 5 lines):")
        print(df_dailyreturn.head(5))
        print(f"Length of daily returns: {len(returns)}")
        #print(returns)

    return df_price, returns, covariance, coskew_tensor

# Function to process samples and print the best feasible solution found
def process_sampleset(sampleset, tickers, df_price):
    """Read in sampleset returned from sample_cqm command and display solution."""
    # used with CQM only
    # Find the first feasible solution
    first_run = True
    feasible = False
    for sample, feas in sampleset.data(fields=['sample','is_feasible']):
        if first_run:
            best_sample = sample
        if feas:
            best_sample = sample
            feasible = True
            break
    print(best_sample)

    print("Solution:\n")
    if not feasible:
        print("No feasible solution found.\n")
    else:
        print("Best feasible solution found:")

    # List to hold the portfolio data
    portfolio_data = []

    # Get the values of the variables and append to the portfolio data list
    for stock in tickers:
      buy_decision = best_sample.get(f"b_{stock}", 0)
      share_count = best_sample.get(f"shares_{stock}", 0)
      portfolio_data.append({
        'Stock': stock,
        'Buy': buy_decision,
        'Shares': share_count
      })

    # Convert to DataFrame 
    df_results = pd.DataFrame(portfolio_data)
    df_results = df_results[(df_results['Buy'] == 1) & (df_results['Shares'] > 0)]
    
    # Write all data into file to be back tested using code in jupyter notebook
    df_results = df_results[['Stock','Shares']]
    df_results = df_results.rename(columns = {'Stock':'Ticker', 'Shares':'Weight'})
    df_results = df_results.merge(df_price, on = 'Ticker')
    df_results['Cost of Shares'] = df_results['Weight']*df_results['2023-12-29']
    df_results = df_results.rename(columns = {'Ticker':'Stock'})
    df_results.to_csv("portfolio_data_CQM.csv", index=False)
    
    return df_results









  