import dimod              #core library of D-Wave Ocean SDK
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.system import LeapHybridNLSampler
import utilities          #stock data handling utilities
from dimod import Binary
from dimod import Integer
import numpy
import pandas as pd
from dwave.optimization.model import ArraySymbol, Model
import numpy.typing
import typing

def portfolio_opt(stocks_names: numpy.typing.ArrayLike, num_stocks_to_buy: int, budget: float, returns: numpy.typing.ArrayLike, 
                  price: numpy.typing.ArrayLike, covariance: numpy.typing.ArrayLike, coskewness: numpy.typing.ArrayLike) -> Model:
 
    # Construct the model
    model = Model()

    # Convert inputs to model constants
    returns = model.constant(returns)
    price = model.constant(price)
    covariance = model.constant(covariance)
    coskewness = model.constant(coskewness)
    budget = model.constant(budget)
    num_stocks_to_buy = model.constant(num_stocks_to_buy)

    # Define decision variables
    stocks = model.binary(len(stocks_names))
    #set minimum and maximum number of shares that can be assigned to each stock
    shares = model.integer(len(stocks_names), lower_bound = 0, upper_bound=100) 

    # Add model constraints
     #Full allocation constraint
    _= model.add_constraint(sum(price[i] * shares[i]  for i in range(len(stocks_names))) >= budget*0.90)

    #BudgetConstraint
    _= model.add_constraint(sum(price[i] * shares[i]  for i in range(len(stocks_names))) <= budget)

    #coskew constraint
    _=model.add_constraint(sum(coskewness[i][j][k] * (price[i] * shares[i]/budget) * (price[j] * shares[j]/budget) * (price[k] * shares[k]/budget)
               for i in range(len(stocks_names)) 
               for j in range(i,len(stocks_names))
               for k in range(j,len(stocks_names))) >= -0.15)
    
    # Cardinality constraint - choose exactly k stocks
    _= model.add_constraint(sum(stocks[i] for i in range(len(stocks_names))) == num_stocks_to_buy)

    # Constrain the number of shares to at least 10 if a stock is selected, and to 0 if a stock is not selected
    for i in range(len(stocks_names)):
      # Upper Bound: shares[i] must be 0 if stocks[i] is 0
      model.add_constraint(shares[i] <= 100 * stocks[i])
      # Lower Bound: shares[i] must be at least 1 if stocks[i] is 1
      model.add_constraint(shares[i] >= 1 * stocks[i])

    # Define components of the objective function
    # Return component - minimize the negative to maximize
    return_obj = sum(r * s1  for r, s1 in zip(returns, shares))

    # Risk component - use variance and covariance to approximate risk
    risk_obj = sum(covariance[i][j] * (price[i] * shares[i])/budget * (price[j] * shares[j])/budget
               for i in range(len(stocks_names)) 
               for j in range(len(stocks_names)))
      
    #combine return and risk terms
    #alpha scales the importance of the risk
    alpha = 0.1
    beta  = 1 - alpha
 
    model.minimize(beta * risk_obj - alpha*return_obj)
    model.lock()
    return model

def process_nls_results(model, tickers):

    # Retrieve the optimal values from the model's state (state 0 is the best found)
    all_vars = list(model.iter_decisions())
    
    stocks_var = all_vars[0]  
    shares_var = all_vars[1]  

    # Get  data from state 0
    buy_values = stocks_var.state(0)
    share_values = shares_var.state(0)

    portfolio_data = []
    
    for i, stock in enumerate(tickers):
        portfolio_data.append({
            'Stock': stock,
            'Buy': int(buy_values[i]),
            'Shares': int(share_values[i])
        })
        
    # Create DataFrame and filter for selected stocks
    df_results = pd.DataFrame(portfolio_data)
    df_results = df_results[df_results['Buy'] == 1]
    
    print("Best solution found:")
    print(df_results)
    
    df_results.to_csv("portfolio_data.csv", index=False)


    num_vars = len(list(model.iter_decisions()))
    num_constraints = len(list(model.iter_constraints()))
    total_nodes = model.num_nodes()

    print(f"Decision Variable Symbols: {num_vars}")
    print(f"Total Constraints: {num_constraints}")
    print(f"Total DAG Nodes: {total_nodes}")


if __name__ == '__main__':

    tickers = utilities.get_tickers()

    #compute price, average returns, and covariance
    df_price, returns, covariance, coskewness = utilities.get_stock_info()
    price = df_price['2023-12-29'].values.tolist()

    #number of stocks to buy
    num_stocks_to_buy = 20

    budget = 1000000

    model = portfolio_opt(tickers, num_stocks_to_buy, budget, returns, price, covariance, coskewness)
    
    sampler = LeapHybridNLSampler()
    results = sampler.sample(model, label = "portfolio_opt", time_limit=60) # Updates model state

    # Wait for results if asynchronous
    if hasattr(results, 'result'):
        job_result_object = results.result()
        print(f"Future resolved.")
    else:
        job_result_object = results
        print(f"Synchronous result received.")

    #Process results 
    process_nls_results(model, tickers)
