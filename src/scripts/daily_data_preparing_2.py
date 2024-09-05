import pandas as pd

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))
from data_processing import create_lagged_features

data_dir = project_root / 'data'

#%% 選擇並創造 lag 期，僅保留模型需要的數據，移除因為 lag 與未開市而產生的缺失值

data = pd.read_csv(data_dir / 'daily_reg_data.csv')
# 敘述統計使用的 Dataframe
# daily_describe_df = data.describe()
# daily_describe_df.to_csv('daily_describe_df.csv')

data = data.dropna()
data.columns
# 2024/08/11 加入開收盤價格，開盤到收盤的報酬率，與缺口
columns = ['daily_return', 'open', 'close', 'open_close_return',
    'gap', 'gap_return', 'volume', 'market_turn', 'cpi_grate',
    'ipi_grate', 'un_rate', 'M1B_grate', 'new_issue_stock_ratio',
    'shtmrg', # 當期情緒在後續分析還會用到，沒有 drop 掉
    'cope_senti_score', 'new_num', 'chn_senti', 'booking_senti',
    'std_pos_ant', 'std_neg_ant', 'std_pos_jou', 'std_neg_jou',
    'std_sum_ant', 'std_sum_jou']

# data.columns
drop_columns = ['date', 'volume', 'market_turn', 'cpi_grate',
    'ipi_grate', 'un_rate', 'M1B_grate', 'new_issue_stock_ratio',
    'shtmrg', 'new_num', 'pos_ant', 'neg_ant', 'pos_jou',
    'neg_jou', 'sum_ant', 'sum_jou']

lag = 1
data = create_lagged_features(data, columns, lag, drop_columns)
# data.to_csv(data_dir / 'daily_reg_data_with_lag.csv', index=False)

#%% 資料標準化
from data_processing import standardize_column

std_columns = ['lag1_volume']
for column in std_columns:
    data = standardize_column(data, column)

#%% 準備所有情緒分數與包含中研院模型放入之變數、總經變數之 Dataframe 方便迴歸
from data_processing import create_reg_vars

# 定義模型基礎變數列表
base_vars = ['daily_return', 'lag1_daily_return',
             'lag1_market_turn', 'lag1_shtmrg',
             'lag1_cpi_grate', 'lag1_ipi_grate',
             'lag1_un_rate', 'lag1_M1B_grate',
             'lag1_new_issue_stock_ratio', 'std_lag1_volume']

# data.columns # 方便選取 columns
reg_vars_dict = {}
reg_vars_dict['base_vars'] = create_reg_vars(data, base_vars)

# CopeOpi 情緒分數
reg_vars_dict['current_cope_senti']  = (
    create_reg_vars(data, base_vars, ['cope_senti_score'])
    )
reg_vars_dict['lag1_cope_senti']     = (
    create_reg_vars(data, base_vars, ['lag1_cope_senti_score'])
    )
reg_vars_dict['cur_lag1_cope_senti'] = (
    create_reg_vars(data, base_vars, ['cope_senti_score', 'lag1_cope_senti_score'])
    )

# 使用 HanLP 方法製作的譚松波情緒分數
reg_vars_dict['current_chn_senti']  = (
    create_reg_vars(data, base_vars, ['chn_senti'])
    )
reg_vars_dict['lag1_chn_senti']     = (
    create_reg_vars(data, base_vars, ['lag1_chn_senti'])
    )
reg_vars_dict['cur_lag1_chn_senti'] = (
    create_reg_vars(data, base_vars, ['chn_senti', 'lag1_chn_senti'])
    )

# 使用 HanLP 方法自行透過 Booking 評論資料集訓練的正負面情緒分數
reg_vars_dict['current_booking_senti']  = (
    create_reg_vars(data, base_vars, ['booking_senti'])
    )
reg_vars_dict['lag1_booking_senti']     = (
    create_reg_vars(data, base_vars, ['lag1_booking_senti'])
    )
reg_vars_dict['cur_lag1_booking_senti'] = (
    create_reg_vars(data, base_vars, ['booking_senti', 'lag1_booking_senti'])
    )

#%% 中研院匹配方法與 ANTUSD
# 中研院方法分為: 將正面情緒與負面情緒拆開的模型，以及最後的加總模型

# 使用 ANTUSD 匹配的情緒分數，正面部份
reg_vars_dict['current_pos_ant']  = (
    create_reg_vars(data, base_vars, ['std_pos_ant'])
    )
reg_vars_dict['lag1_pos_ant']     = (
    create_reg_vars(data, base_vars, ['lag1_std_pos_ant'])
    )
reg_vars_dict['cur_lag1_pos_ant'] = (
    create_reg_vars(data, base_vars, ['std_pos_ant', 'lag1_std_pos_ant'])
    )

# 使用 ANTUSD 匹配的情緒分數，負面部份
reg_vars_dict['current_neg_ant']  = (
    create_reg_vars(data, base_vars, ['std_neg_ant'])
    )
reg_vars_dict['lag1_neg_ant']     = (
    create_reg_vars(data, base_vars, ['lag1_std_neg_ant'])
    )
reg_vars_dict['cur_lag1_neg_ant'] = (
    create_reg_vars(data, base_vars, ['std_neg_ant', 'lag1_std_neg_ant'])
    )

# 使用 ANTUSD 匹配的情緒分數，正負面一起放入
reg_vars_dict['current_pos_neg_ant']  = (
    create_reg_vars(data, base_vars, ['std_pos_ant', 'std_neg_ant'])
    )
reg_vars_dict['lag1_pos_neg_ant']     = (
    create_reg_vars(data, base_vars, ['lag1_std_pos_ant', 'lag1_std_neg_ant'])
    )
reg_vars_dict['cur_lag1_pos_neg_ant'] = (
    create_reg_vars(data, base_vars, ['std_pos_ant', 'lag1_std_pos_ant', 
                                      'std_neg_ant', 'lag1_std_neg_ant'])
    )

# 使用 ANTUSD 匹配的情緒分數，將正負面加總視為一個變數
reg_vars_dict['current_sum_ant']  = (
    create_reg_vars(data, base_vars, ['std_sum_ant'])
    )
reg_vars_dict['lag1_sum_ant']     = (
    create_reg_vars(data, base_vars, ['lag1_std_sum_ant'])
    )
reg_vars_dict['cur_lag1_sum_ant'] = (
    create_reg_vars(data, base_vars, ['std_sum_ant', 'lag1_std_sum_ant'])
    )

#%% 中研院匹配方法與中研院期刊自製字典

# 使用中研院期刊自製字典匹配的情緒分數，正面部份
reg_vars_dict['current_pos_jou']  = (
    create_reg_vars(data, base_vars, ['std_pos_jou'])
    )
reg_vars_dict['lag1_pos_jou']     = (
    create_reg_vars(data, base_vars, ['lag1_std_pos_jou'])
    )
reg_vars_dict['cur_lag1_pos_jou'] = (
    create_reg_vars(data, base_vars, ['std_pos_jou', 'lag1_std_pos_jou'])
    )

# 使用中研院期刊自製字典匹配的情緒分數，負面部份
reg_vars_dict['current_neg_jou']  = (
    create_reg_vars(data, base_vars, ['std_neg_jou'])
    )
reg_vars_dict['lag1_neg_jou']     = (
    create_reg_vars(data, base_vars, ['lag1_std_neg_jou'])
    )
reg_vars_dict['cur_lag1_neg_jou'] = (
    create_reg_vars(data, base_vars, ['std_neg_jou', 'lag1_std_neg_jou'])
    )

# 使用中研院期刊自製字典匹配的情緒分數，正負面一起放入
reg_vars_dict['current_pos_neg_jou']  = (
    create_reg_vars(data, base_vars, ['std_pos_jou', 'std_neg_jou'])
    )
reg_vars_dict['lag1_pos_neg_jou']     = (
    create_reg_vars(data, base_vars, ['lag1_std_pos_jou', 'lag1_std_neg_jou'])
    )
reg_vars_dict['cur_lag1_pos_neg_jou'] = (
    create_reg_vars(data, base_vars, ['std_pos_jou', 'lag1_std_pos_jou', 
                                      'std_neg_jou', 'lag1_std_neg_jou'])
    )

# 使用中研院期刊自製字典匹配的情緒分數，將正負面加總視為一個變數
reg_vars_dict['current_sum_jou']  = (
    create_reg_vars(data, base_vars, ['std_sum_jou'])
    )
reg_vars_dict['lag1_sum_jou']     = (
    create_reg_vars(data, base_vars, ['lag1_std_sum_jou'])
    )
reg_vars_dict['cur_lag1_sum_jou'] = (
    create_reg_vars(data, base_vars, ['std_sum_jou', 'lag1_std_sum_jou'])
    )

#%% 創建 HDF5 文件來儲存 value 都是 DataFrame 的 dict

with pd.HDFStore(data_dir / 'reg_vars_dict.h5') as store:
    for key, df in reg_vars_dict.items():
        store[key] = df

# 僅保留 lag1 期之可預測模型，後續進行機器學習
ml_vars_dict = {k: v for k, v in reg_vars_dict.items() if not k.startswith('cur')}

with pd.HDFStore(data_dir / 'ml_vars_dict.h5') as store_:
    for key, df in ml_vars_dict.items():
        store_[key] = df
