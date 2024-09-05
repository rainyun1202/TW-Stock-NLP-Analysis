import pandas as pd
from functools import reduce

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))

data_dir = project_root / 'data'

#%% 讀入月資料總經指標，新股發行比 (月資料)，券資比、道指報酬率、恐慌指數 (日資料)
def prepare_macro_data(base_paths):
    """
    讀取和處理數據，生成基期調整後的數據及其滯後一個月的數據。
    
    Parameters
    ----------
        base_paths : dict
            包含各變數資料檔案路徑的字典。
            每個鍵是一個字符串，代表數據類型（如 'CPI'、'IPI'等），
            對應的值是一個字符串，指向相關 CSV 文件的路徑。

    Returns
    -------
        tuple
            第一個元素是 pandas DataFrame，為合併後的總體經濟指標數據；
            第二個元素是 pandas DataFrame，為原數據滯後一月的版本。

    Notes
    -----
        - 所有輸入的 CSV 檔案需有一個名為 'date' 的欄位，用於進行數據合併。
        - 合併數據時採用內連接，以確保所有數據檔案中的日期都能匹配。
    """

    CPI = pd.read_csv(base_paths['CPI'])
    IPI = pd.read_csv(base_paths['IPI'])
    UNE = pd.read_csv(base_paths['UNE'])
    M1B = pd.read_csv(base_paths['M1B'])
    new_issue = pd.read_csv(base_paths['new_issue'])

    # 使用 reduce() 函數和 merge() 方法逐一合併多個 DataFrame
    macro_dfs = [CPI, IPI, UNE, M1B, new_issue]
    macro_df = reduce(
        lambda x, y: pd.merge(x, y, on='date', how='inner'), macro_dfs)
    
    # 用來畫月資料的圖
    # macro_df.to_csv('monthly_data_graph.csv', index = False)

    # 產生 LAG 一個月的總經指標
    column_names = ['date', 'lag1_cpi', 'lag1_cpi_grate',
                    'lag1_ipi', 'lag1_ipi_grate',
                    'lag1_un_rate', 'lag1_M1B', 'lag1_M1B_grate',
                    'lag1_new_issue']
    lag_macro_df = macro_df.set_index('date').shift(1)
    lag_macro_df.reset_index(inplace=True)
    
    macro_df['date'] = pd.to_datetime(macro_df['date'])
    lag_macro_df['date'] = pd.to_datetime(lag_macro_df['date'])
    lag_macro_df.columns = column_names
    
    unless_col = ['cpi', 'ipi', 'M1B']
    lag_unless_col = ['lag1_cpi', 'lag1_ipi', 'lag1_M1B']
    macro_df.drop(unless_col, axis=1, inplace=True)
    lag_macro_df.drop(lag_unless_col, axis=1, inplace=True)

    return macro_df, lag_macro_df

base_paths = {
    'CPI': data_dir / 'macro_var' / 'CPI.csv',
    'IPI': data_dir / 'macro_var' / 'IPI.csv',
    'UNE': data_dir / 'macro_var' / 'UNE.csv',
    'M1B': data_dir / 'macro_var' / 'M1B.csv',
    'new_issue': data_dir / 'macro_var' / 'senti_var' / 'new_issue_stock_ratio.csv'
}

macro_df, lag_macro_df = prepare_macro_data(base_paths)
# 券資比
shtmrg = pd.read_csv(data_dir / 'macro_var' / 'senti_var' / 'shtmrg.csv')

# vix         = pd.read_csv(data_dir / 'macro_var' / 'senti_var' / 'VIX.csv')
# djia_return = pd.read_csv(data_dir / 'macro_var' / 'senti_var' / 'djia_return.csv')

#%% 轉換為日資料 (將當月資料視為當月每日資料)
def monthly_to_daily(data, start_date=None, end_date=None):
    """
    將含月資料的 DataFrame 擴展為日資料 DataFrame，並向前填充數據。
    
    Parameters
    ----------
    data : pd.DataFrame
        含有 'date' 和其他變數的月資料 DataFrame。
    start_date : str, optional
        開始日期，如果不指定則使用 data 中的最早日期。
    end_date : str, optional
        結束日期，如果不指定則使用 data 中的最晚日期。

    Returns
    -------
    pd.DataFrame
        擴展至每日的 DataFrame，所有非日期資料向前填充。
    """
    # 使用副本來避免改變原始 DataFrame
    data_copy = data.copy()
    
    data_copy['date'] = pd.to_datetime(data_copy['date'])
    if not start_date:
        start_date = data_copy['date'].min()
    if not end_date:
        end_date = data_copy['date'].max()

    data_copy.set_index('date', inplace=True)
    date_range = pd.date_range(start=start_date, end=end_date)
    # ffill() 將 nan 值填入上一筆非 nan 的值
    data_copy = (
        data_copy
        .reindex(date_range)
        .ffill()
        .reset_index()
        .rename(columns={'index': 'date'})
    )
    
    return data_copy

daily_macro_df     = monthly_to_daily(macro_df, end_date='2022-12-31')
daily_lag_macro_df = monthly_to_daily(lag_macro_df, end_date='2022-12-31')

#%% 處理 Copeopi 與 HanLP 每日情緒分數 (當日所有新聞分數之平均)
def get_daily_anue_senti():
    anue_data   = pd.read_csv(data_dir / 'anue_clear(256662).csv') 
    senti_score = pd.read_csv(data_dir / 'all_senti_score.csv')
    
    anue_senti = pd.concat([anue_data, senti_score], axis=1) # 水平合併
    anue_senti['publishAt'] = (pd
                               .to_datetime(anue_senti['publishAt'])
                               .dt.date # 只留下日
                               )
    anue_senti = anue_senti.rename(columns={'publishAt': 'date'})
    
    # 使用 groupby 分組並計算 CopeOpi 每日 score 的平均值、數量、總和
    daily_cope_senti = (anue_senti
                        .groupby('date')['cope_senti_score']
                        .agg(['mean', 'count', 'sum'])
                        .reset_index()
                        )
    
    daily_cope_senti = (daily_cope_senti
                        .rename(columns = {'mean' : 'cope_senti_score',
                                           'count': 'new_num',
                                           'sum'  : 'sum_senti_score'})
                        )
    daily_cope_senti = daily_cope_senti[['date', 'cope_senti_score', 'new_num']]
    
    daily_chn_senti     = (anue_senti
                           .groupby('date')['chn_senti']
                           .mean()
                           .reset_index()
                           )
    
    daily_booking_senti = (anue_senti
                           .groupby('date')['booking_senti']
                           .mean()
                           .reset_index()
                           )
    # 生成完整日期範圍
    full_date_range = pd.date_range(
        start = daily_cope_senti['date'].min(),
        end   = daily_cope_senti['date'].max(), freq='D')
    
    # 找出缺失 (沒新聞) 的日期 2019-10-11 與 2021-06-14
    # missing_dates = full_date_range.difference(daily_anue_senti['date'])  
    full_daily_anue = pd.DataFrame({'date': full_date_range})
    full_daily_anue['date'] = full_daily_anue['date'].dt.date
    
    # 使用 join 進行合併，並填充缺失值為 0
    daily_cope_senti    = daily_cope_senti.set_index('date')
    daily_chn_senti     = daily_chn_senti.set_index('date')
    daily_booking_senti = daily_booking_senti.set_index('date')
    
    daily_senti = (daily_cope_senti
                   .join([daily_chn_senti, daily_booking_senti],
                         how='outer')
                   )
    
    daily_anue_senti = pd.merge(full_daily_anue, daily_senti,
                                on='date', how='left').fillna(0)
    
    return daily_anue_senti

daily_anue_senti = get_daily_anue_senti()

# 重新排序日期
daily_anue_senti = daily_anue_senti.sort_values('date')
daily_anue_senti.reset_index(drop=True, inplace=True)

#%% 處理台灣加權指數報酬率與市場週轉率
def get_taiex_return():
    y2013_2015 = pd.read_csv(data_dir / 'TAIEX' / 'y2013_2015.csv')
    y2016_2018 = pd.read_csv(data_dir / 'TAIEX' / 'y2016_2018.csv')
    y2019_2022 = pd.read_csv(data_dir / 'TAIEX' / 'y2019_2022.csv')
    
    df_return = pd.concat([y2013_2015, y2016_2018, y2019_2022])
    df_return = df_return.rename(columns = {'年月日': 'date',
                                            '報酬率％': 'daily_return',
                                            '週轉率％': 'market_turn',
                                            '成交量(千股)': 'volume',
                                            '開盤價(元)': 'open',
                                            '收盤價(元)': 'close'})
    
    df_return = df_return[['date', 'daily_return', 'open', 'close',
                           'volume', 'market_turn']]
    df_return['date'] = pd.to_datetime(df_return['date'])
    # 根據 datetime 列排序，並從遠到近排序
    df_return = df_return.sort_values(by='date', ascending=True)
    df_return.reset_index(drop=True, inplace=True)
    
    df_return['open_close_return'] = ((df_return['close']
                                      - df_return['open'])
                                      / df_return['open']
                                      ) * 100
    
    df_return['gap'] = df_return['open'] - df_return['close'].shift(1)
    df_return['gap_return'] = ((df_return['open']
                               - df_return['close'].shift(1))
                               / df_return['close'].shift(1)
                               ) * 100
    # 從 yahoo finace 資料計算填補 2013/01/02 的缺失值
    df_return.at[0, 'gap'] = 38.55
    df_return.at[0, 'gap_return'] = 0.500682
    return df_return

df_return = get_taiex_return()

#%% 合併數據集

df_return['date'] = df_return['date'].dt.date # 去除時間資訊，只保留到日
daily_macro_df['date'] = daily_macro_df['date'].dt.date
shtmrg['date'] = pd.to_datetime(shtmrg['date']).dt.date

dfs = [df_return, daily_macro_df, shtmrg, daily_anue_senti]

# 使用 reduce() 函數和 merge() 方法逐一合併多個 DataFrame
# how = 'outer' 保留所有日期，以利後續處理未開市時段累積之情緒
reg_df = reduce(
    lambda x, y: pd.merge(x, y, on = 'date', how = 'outer'), dfs)

# 重新排序日期
reg_df = reg_df.sort_values('date')
reg_df.reset_index(drop = True, inplace = True)

def convert_volume(volume):
    try:
        # 移除逗號並轉為數值
        return int(volume.replace(',', ''))*1000 # 單位為千元
    except:
        # 遇到 nan 就返回原值
        return volume

reg_df['volume'] = reg_df['volume'].apply(convert_volume)

#%% 正確考慮了非交易日的情緒分數累積問題

# 越靠近交易日的情緒分數佔比會越重
# 遇到非交易日時，就會先把該非交易日與前一交易日之情緒分數取平均
# 連續第二個非交易日則再與上一個非交易日與交易日取出來的平均情緒分數取平均
# 舉例來說，禮拜一的情緒，周日佔50%，周六與周五各佔25%
# 遇到長期非交易日會繼續遞減，12.5% ... 依此類推
df = reg_df[['daily_return', 'cope_senti_score',
             'chn_senti', 'booking_senti']].copy()

def process_senti_score(df, df_return_col, df_senti_col):

    for i, trading_day in enumerate(df[df_return_col]):
        if i > 0: # 數據第一天為元旦未開市，跳過不處理  
            # 遇到非交易日時，將該日的情緒分數與前一日取平均並儲存
            # 遇到連續非交易日，離開始交易越遠的情緒比重會因為平均越來越小
            if str(trading_day) == 'nan':
                df[df_senti_col].iloc[i] = (
                    (df[df_senti_col].iloc[i]
                     + 
                     df[df_senti_col].iloc[i - 1]) / 2
                )
                        
            # 正常交易日，不須重新計算情緒分數
            else:
                continue

    return df

df = process_senti_score(df, 'daily_return', 'cope_senti_score')
df = process_senti_score(df, 'daily_return', 'chn_senti')
df = process_senti_score(df, 'daily_return', 'booking_senti')

reg_df['cope_senti_score'] = df['cope_senti_score']
reg_df['chn_senti']        = df['chn_senti']
reg_df['booking_senti']    = df['booking_senti']

#%% 新增中研院期刊方法計算的情緒分數

# 沒新聞的日期 2019-10-11 與 2021-06-14 (已填充)
jou_senti_score = pd.read_csv(data_dir / 'daily_journal_score.csv')
jou_senti_score['date'] = pd.to_datetime(jou_senti_score['date'])
reg_df['date'] = pd.to_datetime(reg_df['date'])
reg_df = pd.merge(reg_df, jou_senti_score, on='date', how='outer')

# reg_df.to_csv(data_dir / 'daily_reg_data.csv', index=False)
