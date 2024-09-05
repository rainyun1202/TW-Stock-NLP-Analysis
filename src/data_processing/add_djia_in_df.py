import pandas as pd

def add_djia_in_df(reg_vars_dict, daily_data_path, djia_data_path):
    """
    處理 reg_vars_dict 中每個 DataFrame，
    加入 DJIA 美股報酬率並進行資料清洗、合併和轉換步驟，準備用於迴歸分析的數據。

    Parameters
    ----------
        reg_vars_dict : dict
            包含迴歸變數的 DataFrame 的字典。
        daily_data_path : str
            獲取日期數據 CSV 文件的路徑。
        djia_data_path : str
            DJIA 數據 CSV 文件的路徑。

    Returns
    -------
        dict
            加入 DJIA 後的 DataFrames 字典。

    Examples
    --------
    # Example usage:
    # reg_vars_dict = {'lag1_pos_neg_jou': pd.DataFrame(...), ...}
    # add_djia_in_df = add_djia_in_df(reg_vars_dict, 'daily_reg_data.csv', 'taiwan_time_DJIA.csv')
    """
    # 讀取並處理日期數據
    raw_df = pd.read_csv(daily_data_path)
    raw_df.dropna(inplace=True)
    raw_df['date'] = pd.to_datetime(raw_df['date'])
    date_df = raw_df[['date']]
    
    # 讀取並預處理 DJIA 數據
    djia_df = pd.read_csv(djia_data_path)
    djia_df['date'] = pd.to_datetime(djia_df['date'])
    djia_df = djia_df[['date', 'djia_daily_return']]

    reg_vars_djia_dict = {}

    # 處理字典中的每個 DataFrame
    for key, df in reg_vars_dict.items():
        df = pd.concat([date_df, df], axis=1)
        reg_df = pd.merge(df, djia_df, on='date', how='outer')
        reg_df['lag1_djia_daily_return'] = reg_df['djia_daily_return'].shift(1)
        reg_df.at[0, 'lag1_djia_daily_return'] = 2.354 # 2013/01/02 報酬率，人工算得
        reg_df.dropna(subset=['daily_return'], inplace=True)
        reg_df.fillna(0, inplace=True)
        reg_df.drop(columns=['date', 'djia_daily_return'], inplace=True)

        reg_vars_djia_dict[key] = reg_df

    return reg_vars_djia_dict
