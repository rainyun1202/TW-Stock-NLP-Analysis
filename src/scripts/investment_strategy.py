import pandas as pd
import numpy as np
import json
import pickle

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))

data_dir = project_root / 'data'

with open(data_dir / 'binary_y_pred_dict.pkl', 'rb') as f:
    y_pred_dict = pickle.load(f)

#%%
avg_y_pred_dict = {}
# avg_class_report_dict = {}
models = ['lag1_pos_neg_jou_lr_0.9_djia',
          'lag1_pos_neg_jou_svc_0.9_djia',
          'lag1_pos_neg_jou_rfc_0.9_djia',
          'lag1_pos_neg_jou_xgb_0.9_djia',
          'lag1_pos_neg_jou_sv_0.9_djia',
          'lag1_pos_neg_jou_lstm_0.9_djia',
          'lag1_pos_neg_jou_lr_0.8_djia',
          'lag1_pos_neg_jou_svc_0.8_djia',
          'lag1_pos_neg_jou_rfc_0.8_djia',
          'lag1_pos_neg_jou_xgb_0.8_djia',
          'lag1_pos_neg_jou_sv_0.8_djia',
          'lag1_pos_neg_jou_lstm_0.8_djia',
          'lag1_pos_neg_jou_lr_0.7_djia',
          'lag1_pos_neg_jou_svc_0.7_djia',
          'lag1_pos_neg_jou_rfc_0.7_djia',
          'lag1_pos_neg_jou_xgb_0.7_djia',
          'lag1_pos_neg_jou_sv_0.7_djia',
          'lag1_pos_neg_jou_lstm_0.7_djia',
]

for model, lists in y_pred_dict.items():
    if model in models:
        arrays = np.array(lists)
        average_result = np.mean(arrays, axis=0)
        avg_y_pred_dict[model] = average_result

#%%
data = pd.read_csv(data_dir / 'daily_reg_data_with_lag.csv')
data.columns
# daily_return = data['daily_return']
open_close_return = data['open_close_return']

# open_p            = data['open']
# close_p           = data['close']
# gap               = data['gap']
# gap_return        = data['gap_return']

# lag1_open              = data['lag1_open']
# lag1_close             = data['lag1_close']
# lag1_open_close_return = data['lag1_open_close_return']
# lag1_gap               = data['lag1_gap']
# lag1_gap_return        = data['lag1_gap_return']

#%%
def calculate_portfolio_performance(
    avg_y_pred_dict,
    model_key,
    real_return,
    initial_capital=1000000,
    trade_fee=True,
    risk_free_rate=0.01 # Annual risk-free rate
):
    # Retrieve model predictions
    y_pred = np.array(avg_y_pred_dict[model_key]).flatten()
    
    # Generate trading positions: 1 for buy, -1 for sell, 0 for no action
    positions = np.where(y_pred >= 0.9, 1, np.where(y_pred <= 0.1, -1, 0))
    
    # Calculate the number of buy (1) and sell (-1) trades
    num_buys  = np.sum(positions == 1)
    num_sells = np.sum(positions == -1)
    trading_num = int((num_buys + num_sells) * 2)
    
    # Calculate trading fees
    trading_fee = trading_num * initial_capital * 0.001425
    
    # Calculate daily portfolio returns
    portfolio_return = positions * real_return * 0.01
    
    # Apply trading fees if applicable
    if trade_fee:
        final_return = ((initial_capital * (1 + np.sum(portfolio_return)) - trading_fee) / 1000000) - 1
    else:
        final_return = (initial_capital * (1 + np.sum(portfolio_return)) / 1000000) - 1
    
    # Calculate Sharpe Ratio
    # Convert annual risk-free rate to daily risk-free rate
    daily_rf_rate = (1 + risk_free_rate) ** (1/252) - 1
    
    # Calculate average daily return and daily return standard deviation
    avg_daily_return = np.mean(portfolio_return)
    daily_std = np.std(portfolio_return)
    
    # Calculate Sharpe Ratio (annualized)
    sharpe_ratio = (avg_daily_return - daily_rf_rate) / daily_std
    annual_sharpe_ratio = sharpe_ratio * np.sqrt(252)
    
    return [final_return, trading_num, annual_sharpe_ratio]

return_dict = {}

for model, lists in avg_y_pred_dict.items():
    if model[-8:-5] == '0.7':
        real_return = open_close_return[-736:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, risk_free_rate=0.01035)
        return_dict[model] = final_return
    if model[-8:-5] == '0.8':
        real_return = open_close_return[-491:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, risk_free_rate=0.00755)
        return_dict[model] = final_return
    if model[-8:-5] == '0.9':
        real_return = open_close_return[-246:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, risk_free_rate=0.00755)
        return_dict[model] = final_return
        
return_non_fee_dict = {}

for model, lists in avg_y_pred_dict.items():
    if model[-8:-5] == '0.7':
        real_return = open_close_return[-736:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, trade_fee=False, risk_free_rate=0.01035)
        return_non_fee_dict[model] = final_return
    if model[-8:-5] == '0.8':
        real_return = open_close_return[-491:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, trade_fee=False, risk_free_rate=0.00755)
        return_non_fee_dict[model] = final_return
    if model[-8:-5] == '0.9':
        real_return = open_close_return[-246:]
        final_return = calculate_portfolio_performance(
            avg_y_pred_dict, model, real_return, trade_fee=False, risk_free_rate=0.00755)
        return_non_fee_dict[model] = final_return

return_df = (pd
             .DataFrame
             .from_dict(return_dict,
                        orient='index',
                        columns=['return', 'trade_num', 'sharpe_ratio']
                        )
             )

return_non_fee = (pd
                  .DataFrame
                  .from_dict(return_non_fee_dict,
                             orient='index',
                             columns=['return', 'trade_num', 'sharpe_ratio']
                             )
                  )

# return_df.to_csv(data_dir / 'ml_trading_return.csv')
# return_non_fee.to_csv(data_dir / 'ml_trading_return_non_fee.csv')

#%%
def calculate_combined_strategy_performance(
    avg_y_pred_dict,
    models,
    real_return,
    initial_capital=1000000,
    trade_fee=True,
    risk_free_rate=0.01 # Annual risk-free rate
):
    
    # Retrieve model predictions and calculate the average prediction
    y_pred = np.mean([np.array(avg_y_pred_dict[key]).flatten() for key in models], axis=0)

    # Generate trading positions based on the average prediction
    # positions = np.where(y_pred >= 0.5, 1, -1)
    positions = np.where(y_pred >= 0.9, 1, np.where(y_pred <= 0.1, -1, 0))

    num_buys  = np.sum(positions == 1)
    num_sells = np.sum(positions == -1)
    trading_num = int((num_buys + num_sells) * 2)
    trading_fee = (trading_num) * initial_capital * 0.001425
    
    # Calculate daily portfolio return
    portfolio_return = positions * real_return * 0.01
    if trade_fee:
        final_return = ((initial_capital * (1 + np.sum(portfolio_return)) - trading_fee) / 1000000) - 1
    else:
        final_return = (initial_capital * (1 + np.sum(portfolio_return)) / 1000000) - 1

    # Calculate Sharpe Ratio
    # Convert annual risk-free rate to daily risk-free rate
    daily_rf_rate = (1 + risk_free_rate) ** (1/252) - 1
    
    # Calculate average daily return and daily return standard deviation
    avg_daily_return = np.mean(portfolio_return)
    daily_std = np.std(portfolio_return)
    
    # Calculate Sharpe Ratio (annualized)
    sharpe_ratio = (avg_daily_return - daily_rf_rate) / daily_std
    annual_sharpe_ratio = sharpe_ratio * np.sqrt(252)
    
    return [final_return, trading_num, annual_sharpe_ratio]      

# 多模型組合策略計算
models_9 = ['lag1_pos_neg_jou_lr_0.9_djia',
            'lag1_pos_neg_jou_svc_0.9_djia',
            'lag1_pos_neg_jou_rfc_0.9_djia',
            'lag1_pos_neg_jou_xgb_0.9_djia',
            'lag1_pos_neg_jou_sv_0.9_djia',
            'lag1_pos_neg_jou_lstm_0.9_djia'
]

models_8 = ['lag1_pos_neg_jou_lr_0.8_djia',
            'lag1_pos_neg_jou_svc_0.8_djia',
            'lag1_pos_neg_jou_rfc_0.8_djia',
            'lag1_pos_neg_jou_xgb_0.8_djia',
            'lag1_pos_neg_jou_sv_0.8_djia',
            'lag1_pos_neg_jou_lstm_0.8_djia'
]

models_7 = ['lag1_pos_neg_jou_lr_0.7_djia',
            'lag1_pos_neg_jou_svc_0.7_djia',
            'lag1_pos_neg_jou_rfc_0.7_djia',
            'lag1_pos_neg_jou_xgb_0.7_djia',
            'lag1_pos_neg_jou_sv_0.7_djia',
            'lag1_pos_neg_jou_lstm_0.7_djia'
]

ml_mix_dict = {'0.9_mix':'',
               '0.8_mix':'',
               '0.7_mix':'',
               '0.9_mix_non_fee':'',
               '0.8_mix_non_fee':'',
               '0.7_mix_non_fee':''}

ml_mix_dict['0.9_mix'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_9, open_close_return[-246:], risk_free_rate=0.01035)

ml_mix_dict['0.8_mix'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_8, open_close_return[-491:], risk_free_rate=0.00755)

ml_mix_dict['0.7_mix'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_7, open_close_return[-736:], risk_free_rate=0.00755)


ml_mix_dict['0.9_mix_non_fee'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_9, open_close_return[-246:], trade_fee=False, risk_free_rate=0.01035)

ml_mix_dict['0.8_mix_non_fee'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_8, open_close_return[-491:], trade_fee=False, risk_free_rate=0.00755)

ml_mix_dict['0.7_mix_non_fee'] = calculate_combined_strategy_performance(
    avg_y_pred_dict, models_7, open_close_return[-736:], trade_fee=False, risk_free_rate=0.00755)

ml_mix_df = pd.DataFrame.from_dict(ml_mix_dict, orient='index', columns=['return', 'trade_num', 'sharpe_ratio'])

# ml_mix_df.to_csv(data_dir / 'ml_mix_trading_return.csv')
