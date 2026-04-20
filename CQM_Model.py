import dimod              #core library of D-Wave Ocean SDK
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.system import LeapHybridCQMSampler
import utilities          #stock data handling utilities
from dimod import ConstrainedQuadraticModel, BinaryQuadraticModel, QuadraticModel
from dimod import Binary
from dimod import Integer
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def bin_variables(tickers):
   
    #define list of binary stock variables
    stocks = [Binary(f'b_{stk}') for stk in tickers]
    return stocks

def int_variables(tickers):
    shares = [Integer(f'shares_{stk}', lower_bound=0, upper_bound=10000) for stk in tickers] 
    return shares 

def build_cqm(stocks, shares, covariance, num_stocks_to_buy, budget, returns, price):
   
  #  bqm_obj = BinaryQuadraticModel()
    cqm = ConstrainedQuadraticModel() 

    returns_arr = np.array(returns, dtype ='float32')
    price_arr = np.array(price, dtype ='float32')
    covariance_arr = np.array(covariance, dtype ='float32')

    #constraint: number of stocks to buy
    cqm.add_constraint(sum(stocks) == num_stocks_to_buy, label='choose k stocks')

    #constraint: Sum of (price * stock_variable) <= budget
    cqm.add_constraint(sum(price_arr[i] * shares[i] * stocks[i] for i in range(len(stocks))) >= budget*0.90, label='minimum_limitation')
    cqm.add_constraint(sum(price_arr[i] * shares[i] * stocks[i] for i in range(len(stocks))) <= budget, label='budget_limitation')
  
    #add minimum constraint for shares assigned to each stock
     
    for i in range(len(stocks)):
      c2_label = f'less_than_y_shares_must_be_assigned_to_stock_{i}'
      cqm.add_constraint(shares[i] <= 10000, label=c2_label) 

    #return component - minimize the negative to maximize
    return_obj = sum((r * s1 * s2 * p)/budget for r, s1, s2, p in zip(returns_arr, shares, stocks, price_arr))

    #risk component - use covariance to approximate risk
    risk_obj = sum((covariance_arr[i][j] * price_arr[i] * shares[i] * price_arr[j] * shares[j])/budget
               for i in range(len(stocks)) 
               for j in range(len(stocks)))
    
    #Penalize if a stock that is not selected (stock variable = 0) but has shares assigned (shares > 0)
    shares_obj = sum( shares[i] *(1 - stocks[i]) for i in range(len(stocks)))

    #combine return and risk terms
    #alpha scales the importance of the risk
    alpha = 0.3
    beta = 10
    p = 1 
    cqm.set_objective(alpha * risk_obj + p * shares_obj - beta * return_obj)

    return cqm

def sample_cqm(cqm):

   #define sampler - hybrid sampler uses a combination of CPUs or GPUs and the QPU to solve the problem
   sampler = LeapHybridCQMSampler()
   
   #sample the cqm and store the result - the model returns multiple solutions
   #each solution includes: values for binary variables, energy, constraint feasibility
   sampleset = sampler.sample_cqm(cqm, label='Portfolio Optimization 1')

   return sampleset


if __name__ == '__main__':

    tickers = utilities.get_tickers()

    #compute price, average returns, and covariance
    df_price, returns, covariance, coskewness = utilities.get_stock_info()
    price = df_price['2023-12-29'].values.tolist()

    #number of stocks to buy
    num_stocks_to_buy = 30

    budget = 100000

    #add binary variables for stocks
    stocks = bin_variables(tickers)

    #add integer variables for number of shares to buy for each stock
    shares = int_variables(tickers)
    
    #build CQM
    cqm = build_cqm(stocks, shares, covariance, num_stocks_to_buy, budget, returns, price)
    
    print("something")
    #run CQM on hybrid solver
    sampleset = sample_cqm(cqm)
    print("Objective set successfully!", flush=True)
    results = utilities.process_sampleset(sampleset, tickers, df_price)
 