import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimization

# on average there are 252 trading days in a year
NUM_TRADING_DAYS = 252
# we will generate random w (different portfolios)
NUM_PORTFOLIOS = 10000


# historical data - define START and END dates
start_date = '2010-01-01'
end_date = '2023-01-01'


def download_data(stocks):
    # name of the stock (key) - stock values (2010-1017) as the values
    stock_data = {}

    for stock in stocks:
        # closing prices
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date)['Close']

    return pd.DataFrame(stock_data)


def show_data(data):
    data.plot(figsize=(10, 5))
    plt.show()
# chart


def calculate_return(data):
    # NORMALIZATION - to measure all variables in comparable metric
    log_return = np.log(data / data.shift(1))
    return log_return[1:]


def show_statistics(returns):
    # instead of daily metrics we are after annual metrics
    # mean of annual return
    print(returns.mean() * NUM_TRADING_DAYS)
    print(returns.cov() * NUM_TRADING_DAYS)


def show_mean_variance(returns, weights):
    # we are after the annual return
    portfolio_return = np.sum(returns.mean() * weights) * NUM_TRADING_DAYS
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov()
                                                            * NUM_TRADING_DAYS, weights)))
    print("Expected portfolio mean (return): ", portfolio_return)
    print("Expected portfolio volatility (standard deviation): ", portfolio_volatility)


def show_portfolios(returns, volatilities):
    plt.figure(figsize=(10, 6))
    plt.scatter(volatilities, returns, c=returns / volatilities, marker='o')
    plt.grid(True)
    plt.xlabel('Expected Volatility')
    plt.ylabel('Expected Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.show()
# chart - done


def generate_portfolios(returns, stocks):
    portfolio_means = []
    portfolio_risks = []
    portfolio_weights = []

    for _ in range(NUM_PORTFOLIOS):
        w = np.random.random(len(stocks))
        w /= np.sum(w)
        portfolio_weights.append(w)
        portfolio_means.append(np.sum(returns.mean() * w) * NUM_TRADING_DAYS)
        portfolio_risks.append(np.sqrt(np.dot(w.T, np.dot(returns.cov()
                                                          * NUM_TRADING_DAYS, w))))

    return np.array(portfolio_weights), np.array(portfolio_means), np.array(portfolio_risks)


def statistics(weights, returns):
    portfolio_return = np.sum(returns.mean() * weights) * NUM_TRADING_DAYS
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov()
                                                            * NUM_TRADING_DAYS, weights)))
    return np.array([portfolio_return, portfolio_volatility,
                     portfolio_return / portfolio_volatility])


# scipy optimize module can find the minimum of a given function
# the maximum of a f(x) is the minimum of -f(x)
def min_function_sharpe(weights, returns):
    return -statistics(weights, returns)[2]


# what are the constraints? The sum of weights = 1 !!!
# f(x)=0 this is the function to minimize
def optimize_portfolio(weights, returns, stocks):
    # the sum of weights is 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # the weights can be 1 at most: 1 when 100% of money is invested into a single stock
    bounds = tuple((0, 1) for _ in range(len(stocks)))
    return optimization.minimize(fun=min_function_sharpe, x0=weights[0], args=returns
                                 , method='SLSQP', bounds=bounds, constraints=constraints)


def print_optimal_portfolio(optimum, returns, stocks):
    portfolio_weights = optimum['x'].round(3)
    expected_return, volatility, sharpe_ratio = statistics(portfolio_weights, returns)

    # Print the optimal portfolio allocation and statistics
    print("Optimal portfolio allocation:")
    for i in range(len(portfolio_weights)):
        print(f"{stocks[i]}: {portfolio_weights[i]}")
    print("Expected return, volatility, and Sharpe ratio: ", (expected_return, volatility, sharpe_ratio))

    # Create a pie chart to visualize the portfolio allocation
    labels = stocks
    sizes = portfolio_weights
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
    plt.title("Optimal Portfolio Allocation")

    # Display the pie chart
    plt.show()
# chart

def show_optimal_portfolio(opt, rets, portfolio_rets, portfolio_vols):
    plt.figure(figsize=(10, 6))
    plt.scatter(portfolio_vols, portfolio_rets, c=portfolio_rets / portfolio_vols, marker='o')
    plt.grid(True)
    plt.xlabel('Expected Volatility')
    plt.ylabel('Expected Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.plot(statistics(opt['x'], rets)[1], statistics(opt['x'], rets)[0], 'g*', markersize=20.0)
    plt.show()
# chart


# if __name__ == '__main__':
#     dataset = download_data()
#     show_data(dataset)
#     log_daily_returns = calculate_return(dataset)

#     #show_statistics(log_daily_returns)
#     pweights, means, risks = generate_portfolios(log_daily_returns)
#     show_portfolios(means, risks)



#     # Optimize for high risk, high return portfolio (maximize expected return)
#     constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})


#     def max_expected_return(weights, returns):
#         return -statistics(weights, returns)[0]  # Maximize expected return

#     bounds = tuple((0, 1) for _ in range(len(stocks)))  # Define bounds

#     optimum_high_risk_high_return = optimization.minimize(fun=max_expected_return, x0=pweights[0],
#                                                            args=log_daily_returns, method='SLSQP', bounds=bounds,
#                                                            constraints=constraints)


#     # Optimize for low risk, decent return portfolio (minimize volatility)
#     def min_function_volatility(weights, returns):
#         return statistics(weights, returns)[1]  # Minimize volatility

#     optimum_low_risk_decent_return = optimization.minimize(fun=min_function_volatility, x0=pweights[0],
#                                                            args=log_daily_returns, method='SLSQP', bounds=bounds,
#                                                            constraints=constraints)

#     print("High Risk, High Return Portfolio:")
#     print_optimal_portfolio(optimum_high_risk_high_return, log_daily_returns, stocks)

#     print("Low Risk, Decent Return Portfolio:")
#     print_optimal_portfolio(optimum_low_risk_decent_return, log_daily_returns, stocks)


#     print("Most Optimal Portfolio:")
#     optimum = optimize_portfolio(pweights, log_daily_returns)
#     print_optimal_portfolio(optimum, log_daily_returns,stocks)
#     show_optimal_portfolio(optimum, log_daily_returns, means, risks)
#     print(stocks)

