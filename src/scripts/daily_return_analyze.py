import pandas as pd
from tqdm import tqdm
import json

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))
from data_processing import add_djia_in_df
from models import stepwise_forward_selection, format_reg_model
from utils import generate_latex_table

#%% 讀取整理好的所有模型變數 Dataframe

data_dir = project_root / 'data'

with pd.HDFStore(data_dir / 'reg_vars_dict.h5') as store:
    reg_vars_dict = {key.strip('/'): store[key] for key in store.keys()}

# 加入 DJIA 報酬率
reg_vars_djia_dict = add_djia_in_df(reg_vars_dict,
                                    data_dir / 'daily_reg_data.csv',
                                    data_dir / 'taiwan_time_DJIA.csv')

# 輸出相關係數表
# pearson_corr = reg_vars_dict['base_vars'].corr(method='pearson')

#%% Forward Selection Procedure 根據 AIC 或 BIC 選擇有效資訊
sfs_model_result = {} 

for model_name, X_vars in tqdm(reg_vars_dict.items()):
    # reg_vars_dict 原始迴歸資料，reg_vars_djia_dict 加入美股
    # 執行加入美股的結果在下方程式碼直接輸出為 DataFrame 儲存
    model, aic_bic_with_candidates = stepwise_forward_selection(
        X_vars, 'daily_return',
        ['lag1_daily_return'], 'aic') # 預設放入的變數須為 list 格式，[] 代表不預設
    # 將 sfs 結果整理成論文格式表格
    sfs_model_result[model_name] = format_reg_model(model, f'{model_name}')

# 儲存所有 sfs 結果為 .h5 檔案 (原先未加入美股之結果)
# with pd.HDFStore(data_dir / 'sfs_model_result.h5') as store:
#     for key, df in sfs_model_result.items():
#         store[key] = df

#%%
# 加入美股後 lag1 期情緒指標前進選擇法之選擇結果都相同 (僅額外挑出 cpi, M1B)
# 因此隨意取一即可，column name 要手動更改
djia_sfs_df = sfs_model_result['lag1_pos_neg_jou']

# 利用該字典將英文變數名稱的 index 改為中文在表格上呈現 
with open(data_dir / 'vars_to_chinese.json',
          'r', encoding='utf-8') as file:
    vars_to_chinese_dict = json.load(file)
# 利用該字典將英文模型名稱的 column 改為中文在表格上呈現 
with open(data_dir / 'model_name_to_chinese_2row_lag.json',
          'r', encoding='utf-8') as file:
    model_name_to_chinese_dict = json.load(file)

# 檢查 index 中是否包含 'stderr' 並建立字典，用以刪除無須標示的標準誤 row
index_map = {idx: '' if 'stderr' in idx else idx for idx in djia_sfs_df.index}
djia_sfs_df = djia_sfs_df.rename(index=index_map)
djia_sfs_df = djia_sfs_df.rename(index=vars_to_chinese_dict)
djia_sfs_df = djia_sfs_df.rename(columns=model_name_to_chinese_dict)

# 輸出 latex 精美表格結果 (需使用 reg_vars_djia_dict 進行前進選擇法)
# generate_latex_table(djia_sfs_df, 'djia_sfs_lag1_senti_df.tex')
