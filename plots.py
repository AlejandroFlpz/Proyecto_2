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
    
    min_test_len = min(len(test['Datetime']), len(test_portfolio))
    min_val_len = min(len(validation['Datetime']), len(validation_portfolio))
    
    plt.figure(figsize=(12, 6))
    plt.plot(test['Datetime'].iloc[:min_test_len], test_portfolio.iloc[:min_test_len], label='Test', color='red')
    plt.plot(validation['Datetime'].iloc[:min_val_len], validation_portfolio.iloc[:min_val_len], label='Validation', color='green')
    plt.title('Portfolio value through Test and Validation Periods')
    plt.xlabel('Date')
    plt.ylabel('Portfolio value')
    plt.legend()
    plt.show()



