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
    """Read in stock returns and price information from CSV."""
    df = pd.read_csv('data/lastprice_data.csv')
    print(df.head())
    price = np.array(df['2023-12-29'].values)
    #print(price)
    
    df_monthreturn = pd.read_csv("data/returns_data.csv", index_col='Date')
    ave_monthly_returns = df_monthreturn.mean(axis=0)
    returns = list(ave_monthly_returns)

    # Compute the variance from the monthly returns
    variance = df_monthreturn.cov().values.tolist()

    if verbose:
        print("Data Check")
        print(f"Length of Price Array: {len(price)}")
        print("Monthly return(the first 5 lines):")
        print(df_monthreturn.head(5))
        print("Average monthly return:")
        print(f"Length of monthly returns: {len(returns)}")
        #print(returns)

    return price, returns, variance

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