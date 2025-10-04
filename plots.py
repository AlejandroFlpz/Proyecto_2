import pandas as pd
import matplotlib.pyplot as plt

def plot_portfolio_value_train(portfolio_value_train):
    
    plt.figure(figsize=(10, 5))
    plt.plot(portfolio_value_train,  color='cornflowerblue', linewidth=1.8, label='Train Portfolio')
    plt.title('Portfolio Value over Training Period')
    plt.xlabel('Time')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.show()


def plot_test_validation(test_portfolio, validation_portfolio, test, validation):
    
    plt.figure(figsize=(12, 6))
    plt.plot(test['Datetime'].reset_index(drop=True), test_portfolio, label='Test', color='red')
    plt.plot(validation['Datetime'].reset_index(drop=True), validation_portfolio, label='Validation', color='green')
    plt.title('Portfolio value over time (test + validation)')
    plt.xlabel('Date')
    plt.ylabel('Portfolio value')
    plt.legend()
    plt.show()



