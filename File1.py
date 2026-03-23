import dimod              #core library of D-Wave Ocean SDK
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.system import LeapHybridCQMSampler
import utilities          #stock data handling utilities
from dimod import ConstrainedQuadraticModel
from dimod import Binary

def bin_variables(tickers):
   
    #define list of binary stock variables
    stocks = [Binary(f's_{stk}') for stk in tickers]
    return stocks

def build_cqm(stocks, num_stocks_to_buy, budget, returns):
    cqm = ConstrainedQuadraticModel()
    
    #constraint: number of stocks to buy
    cqm.add_constraint(sum(bin_variables) == num_stocks_to_buy, label='choose k stocks')

    #constraint: Sum of (price * stock_variable) <= budget
    cqm.add_constraint(sum(prices[i] * stocks[i] for i in range(len(stocks))) <= budget, label='budget_limitation')

    #return component - minimize the negative to maximize
    return_obj = sum(r * s for r, s in zip(returns, stocks))

    #risk component - use variance and covariance to approximate risk
    risk_obj = sum(variance[i][j] * stocks[i] * stocks[j] 
               for i in range(len(stocks)) 
               for j in range(len(stocks)))
    
    #combine return and risk terms
    #alpha scales the importance of the risk
    alpha = 0.5 
    cqm.set_objective(alpha * risk_obj - return_obj)

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
    tickers=["T", "SFL", "PFE", "XOM", "MO", "VZ", "IBM", "TSLA", "GILD", "GE"]

    #compute price, average returns, and covariance
    price, returns, variance = utilities.get_stock_info()

    #number of stocks to buy
    num_stocks_to_buy = 2

    budget = 100

    #add binary variables for stocks
    stocks = bin_variables(tickers)

    #build CQM
    cqm = build_cqm(stocks, num_stocks_to_buy, returns)

    #run CQM on hybrid solver
    sampleset = sample_cqm(cqm)
    
    #process and print solution
    print("\nPart 1 solution:\n")
    utilities.process_sampleset(sampleset, stockcodes)