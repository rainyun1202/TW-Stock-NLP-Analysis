import pandas as pd
import json
from tqdm import tqdm

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))
from data_processing import add_djia_in_df
from models import run_ols_and_format
from utils import generate_latex_table, get_model_vars_df

#%% 讀取整理好的所有模型變數 Dataframe 與變數英翻中字典

data_dir = project_root / 'data'

with pd.HDFStore(data_dir / 'reg_vars_dict.h5') as store:
    reg_vars_dict = {key.strip('/'): store[key] for key in store.keys()}
    
# 加入 DJIA 報酬率
reg_vars_djia_dict = add_djia_in_df(reg_vars_dict,
                                    data_dir / 'daily_reg_data.csv',
                                    data_dir / 'taiwan_time_DJIA.csv')

# 利用該字典將英文變數名稱的 index 改為中文在表格上呈現 
with open(data_dir / 'vars_to_chinese.json',
          'r', encoding='utf-8') as file:
    vars_to_chinese_dict = json.load(file)

# 利用該字典將英文模型名稱的 column 改為中文在表格上呈現
# (2024/06/16 更新 lag 與 cur)
with open(data_dir / 'model_name_to_chinese_2row_cur.json',
          'r', encoding='utf-8') as file:
    cur_model_name_to_chinese_dict = json.load(file)

with open(data_dir / 'model_name_to_chinese_2row_lag.json',
          'r', encoding='utf-8') as file:
    lag_model_name_to_chinese_dict = json.load(file)

# 2024/06/14 補充 DJIA 報酬率敘述統計
# 1.283 為 2012/12/31 之美股報酬率，匹配預測台股 2013/01/02
# 但最後資料有再全部 lag1 期，只剩 2451 筆，該筆數據剩敘述統計功能
# djia = reg_vars_djia_dict['base_vars']['lag1_djia_daily_return']
# djia = pd.concat([djia, pd.Series(1.283)])
# djia.describe()

#%% Forward Selection Procedure 根據 AIC 或 BIC 選擇有效資訊
# 讀取前進選擇法的模型結果 (未加入美股之結果)
with pd.HDFStore(data_dir / 'sfs_model_result.h5') as store:
    sfs_model_result = {key.strip('/'): store[key] for key in store.keys()}

sfs_df = get_model_vars_df('sfs')

for model_reg_result in sfs_model_result.values():
    sfs_df = pd.concat([sfs_df, model_reg_result], axis=1, join='outer')

new_order = [ind for ind in get_model_vars_df('sfs').index]

# 使用 reindex 來重新排序 index
sfs_df = sfs_df.reindex(new_order)
sfs_df = sfs_df.fillna('--')

#%% 整理出所有預輸出的論文格式表格 (為前進選擇法之結果)
# sfs_df.index
# sfs_df.columns
def drop_rows_with_all_dashes(df):
    """ 
    Drop DataFrame 中整個 row 的 value 都為 "--" 的 row
    """
    mask = (df
            .apply(lambda row: all(item == '--' for item in row), axis=1)
            )
    return df[~mask]

# 檢查 index 中是否包含 'stderr' 並建立字典，用以刪除無須標示的標準誤 row
index_map = {idx: '' if 'stderr' in idx else idx for idx in sfs_df.index}
sfs_df = sfs_df.rename(index=index_map)
sfs_df = sfs_df.rename(index=vars_to_chinese_dict)
# columns name 後面要輸出前再更改
# sfs_df = sfs_df.rename(columns=cur_model_name_to_chinese_dict)

#%% 只有當期情緒分數 (已完成輸出)

latex_dir = project_root / 'latex_table'

current_senti_df_1 = sfs_df[['base_vars',
    'current_chn_senti', 'current_booking_senti', 'current_cope_senti']]
current_senti_df_2 = sfs_df[['base_vars',
    'current_pos_ant', 'current_neg_ant',
    'current_pos_neg_ant', 'current_sum_ant']]
current_senti_df_3 = sfs_df[['base_vars',
    'current_pos_jou', 'current_neg_jou',
    'current_pos_neg_jou', 'current_sum_jou']]

current_senti_df_1 = drop_rows_with_all_dashes(current_senti_df_1)
current_senti_df_2 = drop_rows_with_all_dashes(current_senti_df_2)
current_senti_df_3 = drop_rows_with_all_dashes(current_senti_df_3)

current_senti_df_1 = current_senti_df_1.rename(columns=cur_model_name_to_chinese_dict)
current_senti_df_2 = current_senti_df_2.rename(columns=cur_model_name_to_chinese_dict)
current_senti_df_3 = current_senti_df_3.rename(columns=cur_model_name_to_chinese_dict)

# 轉換 DataFrame 到 LaTeX Table
generate_latex_table(current_senti_df_1, 'current_senti_df_1.tex')
generate_latex_table(current_senti_df_2, 'current_senti_df_2.tex')
generate_latex_table(current_senti_df_3, 'current_senti_df_3.tex')

#%% 只有 lag1 期情緒分數 (使用 OLS 透過 AIC 檢視情緒分數有效性)
# 2024/06/16 更新，需與當期 AIC 選出之結果強制加入情緒變數比較 AIC，證明無效姓

dfs_key = [
    'base_vars', 'lag1_chn_senti', 'lag1_booking_senti', 'lag1_cope_senti',
    'lag1_pos_ant', 'lag1_neg_ant', 'lag1_pos_neg_ant', 
    'lag1_pos_jou', 'lag1_neg_jou', 'lag1_pos_neg_jou',
    'lag1_sum_ant', 'lag1_sum_jou'
]

lag_senti_dfs = {key: reg_vars_dict[key] for key in dfs_key if key in reg_vars_dict}

lag_senti_dfs['lag1_cope_senti_score'] = lag_senti_dfs.pop('lag1_cope_senti')
lag_senti_dfs['lag1_std_neg_ant'] = lag_senti_dfs.pop('lag1_neg_ant')
lag_senti_dfs['lag1_std_neg_jou'] = lag_senti_dfs.pop('lag1_neg_jou')
lag_senti_dfs['lag1_std_pos_ant'] = lag_senti_dfs.pop('lag1_pos_ant')
lag_senti_dfs['lag1_std_pos_jou'] = lag_senti_dfs.pop('lag1_pos_jou')
lag_senti_dfs['lag1_std_sum_ant'] = lag_senti_dfs.pop('lag1_sum_ant')
lag_senti_dfs['lag1_std_sum_jou'] = lag_senti_dfs.pop('lag1_sum_jou')

# base_vars 無需處理
# lag1_pos_neg_ant columns 為 lag1_std_pos_ant lag1_std_neg_ant
# lag1_pos_neg_jou columns 為 lag1_std_pos_jou lag1_std_neg_jou

lag1_model_result = {}

for model_name, df in tqdm(lag_senti_dfs.items()):
    if model_name == 'base_vars':
        df = df[['daily_return', 'lag1_daily_return', 'lag1_cpi_grate',
                  'lag1_M1B_grate', 'lag1_market_turn', 'std_lag1_volume']]
        model = run_ols_and_format(df, 'daily_return', model_name)
        lag1_model_result[model_name] = model
        
    elif model_name == 'lag1_pos_neg_ant':
        df = df[['daily_return', 'lag1_daily_return', 'lag1_cpi_grate',
                  'lag1_M1B_grate', 'lag1_market_turn', 'std_lag1_volume',
                  'lag1_std_pos_ant', 'lag1_std_neg_ant']]
        model = run_ols_and_format(df, 'daily_return', model_name)
        lag1_model_result[model_name] = model
        
    elif model_name == 'lag1_pos_neg_jou':
        df = df[['daily_return', 'lag1_daily_return', 'lag1_cpi_grate',
                  'lag1_M1B_grate', 'lag1_market_turn', 'std_lag1_volume',
                  'lag1_std_pos_jou', 'lag1_std_neg_jou']]
        model = run_ols_and_format(df, 'daily_return', model_name)
        lag1_model_result[model_name] = model
        
    else:
        df = df[['daily_return', 'lag1_daily_return', 'lag1_cpi_grate',
                  'lag1_M1B_grate', 'lag1_market_turn', 'std_lag1_volume',
                  f'{model_name}']]
        model = run_ols_and_format(df, 'daily_return', model_name)
        lag1_model_result[model_name] = model

lag_df = get_model_vars_df('base')

for model_reg_result in lag1_model_result.values():
    lag_df = pd.concat([lag_df, model_reg_result], axis=1, join='outer')

# 檢查 index 中是否包含 'stderr' 並建立字典，用以刪除無須標示的標準誤 row
index_map = {idx: '' if 'stderr' in idx else idx for idx in lag_df.index}
lag_df = lag_df.rename(index=index_map)
lag_df = lag_df.rename(index=vars_to_chinese_dict)

lag_df = lag_df.fillna('--')

#%% 只有 lag1 期情緒分數 (已完成輸出) (2024/06/16 更新輸出結果)

lag_senti_df_1 = lag_df[['base_vars',
    'lag1_chn_senti', 'lag1_booking_senti', 'lag1_cope_senti_score']]
lag_senti_df_2 = lag_df[['base_vars',
    'lag1_std_pos_ant', 'lag1_std_neg_ant',
    'lag1_pos_neg_ant', 'lag1_std_sum_ant']]
lag_senti_df_3 = lag_df[['base_vars',
    'lag1_std_pos_jou', 'lag1_std_neg_jou',
    'lag1_pos_neg_jou', 'lag1_std_sum_jou']]

lag_senti_df_1 = drop_rows_with_all_dashes(lag_senti_df_1)
lag_senti_df_2 = drop_rows_with_all_dashes(lag_senti_df_2)
lag_senti_df_3 = drop_rows_with_all_dashes(lag_senti_df_3)

lag_senti_df_1 = lag_senti_df_1.rename(columns=lag_model_name_to_chinese_dict)
lag_senti_df_2 = lag_senti_df_2.rename(columns=lag_model_name_to_chinese_dict)
lag_senti_df_3 = lag_senti_df_3.rename(columns=lag_model_name_to_chinese_dict)

# 轉換 DataFrame 到 LaTeX Table
generate_latex_table(lag_senti_df_1, 'lag_senti_df_1.tex')
generate_latex_table(lag_senti_df_2, 'lag_senti_df_2.tex')
generate_latex_table(lag_senti_df_3, 'lag_senti_df_3.tex')
