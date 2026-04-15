import dimod              #core library of D-Wave Ocean SDK
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.system import LeapHybridCQMSampler
import utilities          #stock data handling utilities
from dimod import ConstrainedQuadraticModel
from dimod import Binary
from dimod import Integer

def bin_variables(tickers):
   
    #define list of binary stock variables
    stocks = [Binary(f'b_{stk}') for stk in tickers]
    return stocks

def int_variables(tickers):
    shares = [Integer(f'shares_{stk}', lower_bound=0, upper_bound=100) for stk in tickers] 
    return shares 

def build_cqm(stocks, shares, num_stocks_to_buy, budget, returns, price):
    cqm = ConstrainedQuadraticModel() 

    #constraint: number of stocks to buy
    cqm.add_constraint(sum(stocks) == num_stocks_to_buy, label='choose k stocks')

    #constraint: Sum of (price * stock_variable) <= budget
    cqm.add_constraint(sum(price[i] * shares[i] * stocks[i] for i in range(len(stocks))) >= budget*0.90, label='minimum_limitation')
    cqm.add_constraint(sum(price[i] * shares[i] * stocks[i] for i in range(len(stocks))) <= budget, label='budget_limitation')
  
    #add minimim constraint for shares assigned to each stock
     
    for i in range(len(stocks)):
      c2_label = f'less_than_y_shares_must_be_assigned_to_stock_{i}'
      cqm.add_constraint(shares[i] <= 100, label=c2_label) 
    
    #return component - minimize the negative to maximize
    return_obj = sum(r * s1 * s2 * p for r, s1, s2, p in zip(returns, shares, stocks, price))

    #risk component - use variance and covariance to approximate risk
    risk_obj = sum(variance[i][j] * price[i] * shares[i] * price[j] * shares[j]
               for i in range(len(stocks)) 
               for j in range(len(stocks)))
    
    #Penalize if a a stock that is not selected (stock variable = 0) has shares assigned (shares > 0)
    shares_obj = sum( shares[i] *(1 - stocks[i]) for i in range(len(stocks)))

    #combine return and risk terms
    #alpha scales the importance of the risk
    alpha = 0.5
    p = 1000 
    cqm.set_objective(alpha * risk_obj + p * shares_obj - return_obj)

    return cqm

def sample_cqm(cqm):

   #define sampler - hybrid sampler uses a combination of CPUs or GPUs and the QPU to solve the problem
   sampler = LeapHybridCQMSampler()
   
   #sample the cqm and store the result - the model returns multiple solutions
   #each solution includes: values for binary variables, energy, constraint feasibility
   sampleset = sampler.sample_cqm(cqm, label='Portfolio Optimization 1')

   return sampleset


if __name__ == '__main__':

    # 10 sample stocks 
    #tickers=["T", "SFL", "PFE", "XOM", "MO", "VZ", "IBM", "TSLA", "GILD", "GE"]
    tickers = utilities.get_tickers()

    #compute price, average returns, and covariance
    price, returns, variance = utilities.get_stock_info()

    #number of stocks to buy
    num_stocks_to_buy = 50

    budget = 10000

    #add binary variables for stocks
    stocks = bin_variables(tickers)

    #add integer variables for number of shares to buy for each stock
    shares = int_variables(tickers)
    
    #build CQM
    cqm = build_cqm(stocks, shares, num_stocks_to_buy, budget, returns, price)

    #run CQM on hybrid solver
    sampleset = sample_cqm(cqm)
    
    #process and print solution
    print("\nPart 1 solution:\n")
    utilities.process_sampleset(sampleset, tickers)


    #if 'embedding_context' in sampleset.info:
    #  embedding = sampleset.info['embedding_context']['embedding']
     # print(f"Number of logical variables: {len(embedding.keys())}")
     # print(f"Number of physical qubits used in embedding: {sum(len(chain) for chain in embedding.values())}")
    #else:
    # Handle the case where no embedding occurred
    #  print("Warning: No embedding context found.")

