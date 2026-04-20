import csv
from matplotlib import ticker
import numpy as np
import pandas as pd
#Copied from D-Wave Systems portfolio optimization training project

# Prepare Stock data from the csv files
def get_tickers(verbose=False):
    df = pd.read_csv('data/lastprice_data.csv')
    tickers = df['Ticker'].astype(str).tolist()
    if verbose:
        print(tickers)
        print(len(tickers))
    return tickers


def get_stock_info(verbose=True):
    # Read in stock returns and price information from CSV
    df_price = pd.read_csv('data/lastprice_data.csv')
    print(df_price.head())

    ############### calculate mean returns #############################
    df_dailyreturn = pd.read_csv('data/returns_data.csv', index_col='Date')
    avg_daily_returns = df_dailyreturn.mean(axis=0)
    annual_returns = avg_daily_returns * 252
    returns = list(annual_returns)

    ############# calculate variance ###################################
    covariance = (df_dailyreturn.cov() * 252).values.tolist()
    
    ############ calculate coskew tensor ###############################
    returns_array = df_dailyreturn.to_numpy()
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

    if verbose:
        print("Data Check")
        print(f"Length of Price Array: {len(df_price)}")
        print("Monthly return(the first 5 lines):")
        print(df_dailyreturn.head(5))
        print("Average monthly return:")
        print(f"Length of monthly returns: {len(returns)}")
        #print(returns)

    return df_price, returns, covariance, coskew_tensor

# Function to process samples and print the best feasible solution found
def process_sampleset(sampleset, tickers):
    """Read in sampleset returned from sample_cqm command and display solution."""
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
    # Print the solution as which stocks to buy
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
    print(df_results)

    df_results.to_csv("portfolio_data.csv", index=False)










    #print("Portfolio Results:")
    #df_results = pd.DataFrame(list(best_sample.items()), columns=['Variable', 'Value'])
    #df_results.to_csv("portfolio_data.csv", index=False)
    
    #stock_list = []
    #is_one_list = []
    #shares_list = []
    #no_of_shares = []

    #i = 0
    #for stk, shares in best_sample.items():
      
      #if i < len(stockcodes):
       # stock_list.append(stk)
       # is_one_list.append(shares)
      #else:
      #  shares_list.append(stk)
      #  no_of_shares.append(shares)
      #i+=1
#    
    #df_stocks = pd.DataFrame({
    #'Stock': stock_list,
    #'InPortfolio': is_one_list,
    #})
    #df_shares = pd.DataFrame({
    #'Shares_Var': shares_list,
    #'Shares_Number': no_of_shares
    #})
    #df_shares = df_shares["Shares_Var"].str[7:].astype(int) 
    #df_shares.sort_values("Shares_Var", inplace=True)
#    
    #df_results1 = pd.concat([df_stocks, df_shares], axis=1)   
    #print(df_results1.head())
    #df_results2 = 
    #df_results3 = df_results1[(df_results1['InPortfolio'] == 1) & (df_results1['Shares_Number'] > 0)]
#    print(df_results3)


 #   print("\n")



      
  #      if shares > 0 and best_sample[stk] > 0:  # Only show what you actually bought
  #          stk_price = df.loc[df['Ticker'] == stk[2:], "2023-12-29"]
  #          print(f"{stk[2:]}: {int(shares)} shares at price {stk_price.values[0]}")

  #        for stk in stockcodes:
        #    if best_sample[f's_{stk}'] == 1:
        #        stk_price = df.loc[df['Ticker'] == stk, "2023-12-29"]
         #       print(f"{stk} at price {stk_price.values[0]}")


# Read the lastday's closing price from csv file, 
    # and store them in the list, then convert it as numpy array
    # price_read = []
    # with open('data/lastday_closing_price.csv') as f:
    #     reader = csv.reader(f)
    #     for row in reader:
    #         price_read.append(row)
    # price = np.array(price_read[0],dtype=float)

    # Compute the average monthly returns for each stock
    # df_monthreturn = pd.read_csv("data/monthly_returns.csv", index_col='Date')