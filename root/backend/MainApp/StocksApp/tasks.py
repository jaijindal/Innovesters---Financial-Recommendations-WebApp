import math
import numpy as np
import scipy.optimize as optimization
from celery import shared_task
from StocksApp.SentimentAnalysis import SentimentAnalysis
from StocksApp.OptimalPortfolio import optimize_portfolio, generate_portfolios, calculate_return, download_data, statistics

class Portfolio:
    def __init__(self, risk, stocks):
        self.stocks = stocks
        self.dataset = download_data(self.stocks)
        self.log_daily_returns = calculate_return(self.dataset)
        self.pweights, self.means, self.risks = generate_portfolios(self.log_daily_returns, self.stocks)
        self.constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        self.bounds = tuple((0, 1) for _ in range(len(self.stocks)))

        if risk == 'HR':
            self.optimum_portfolio = self.optimize_portfolio_with_function(self.max_expected_return)
        elif risk == 'LR':
            self.optimum_portfolio = self.optimize_portfolio_with_function(self.min_function_volatility)
        else:
            self.optimum_portfolio = optimize_portfolio(self.pweights, self.log_daily_returns, self.stocks)
        
        self.portfolio_weights = self.optimum_portfolio['x'].round(3)
        self.expected_return, self.volatility, self.sharpe_ratio = statistics(self.portfolio_weights, self.log_daily_returns)


    def optimize_portfolio_with_function(self, fun):
        return optimization.minimize(fun=fun, x0=self.pweights[0],
                                     args=self.log_daily_returns, method='SLSQP', bounds=self.bounds,
                                     constraints=self.constraints)

    def max_expected_return(self, weights, returns):
        return -statistics(weights, returns)[0]

    def min_function_volatility(self, weights, returns):
        return statistics(weights, returns)[1]

@shared_task
def calculate_portfolio(risk):
    stocks = SentimentAnalysis()
    portfolio = Portfolio(risk, stocks)
    data = {
        'dataset': portfolio.dataset.reset_index().to_dict('records'),
        'means': portfolio.means.tolist(),
        'risks': portfolio.risks.tolist(),
        'expected_return': portfolio.expected_return,
        'volatility': portfolio.volatility,
        'sharpe_ratio': portfolio.sharpe_ratio,
        'portfolio_weights': portfolio.portfolio_weights.tolist(),
        'stocks': portfolio.stocks,
    }
    return data

def replace_invalid_floats(data):
    if isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None  # or replace with a specific value
    elif isinstance(data, dict):
        return {k: replace_invalid_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_invalid_floats(v) for v in data]
    return data

@shared_task
def calculate_playground(risk, stocks):
    portfolio = Portfolio(risk, stocks)
    data = {
        'dataset': portfolio.dataset.reset_index().to_dict('records'),
        'means': portfolio.means.tolist(),
        'risks': portfolio.risks.tolist(),
        'expected_return': portfolio.expected_return,
        'volatility': portfolio.volatility,
        'sharpe_ratio': portfolio.sharpe_ratio,
        'portfolio_weights': portfolio.portfolio_weights.tolist(),
        'stocks': portfolio.stocks,
    }
    return replace_invalid_floats(data)

