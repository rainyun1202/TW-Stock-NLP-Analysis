import pandas as pd
import re
from tqdm import tqdm

with open('full_ckip_list.txt', 'r', encoding='utf-8') as file:
    news_list = file.readlines()

def process_text(text):
    # 使用正則表達式移除括號內的文字和孤立括號
    text = re.sub(r'\([^)]*\)', '', text)  # 移除正確的括號內容
    text = re.sub(r'\(|\)', '', text)  # 移除孤立的括號
    if len(text) < 6000: # 過長文本內容為無意義新聞文本
        # 根據空格分割文字成為列表，split() 會自動處理多個空格
        words_list = text.split()
        return words_list
    
    else:
        return []

split_news_list = []

for text in tqdm(news_list):
    words_list = process_text(text)
    split_news_list.append(words_list)
    
# 新聞總數為 255653
# filtered_list = [item for item in split_news_list if item != []]

#%% 根據中研院期刊方法計算每篇新聞的情緒分數

antusd = pd.read_csv(r'.\senti_dict\antusd.csv')
journal_pos = pd.read_csv(r'.\senti_dict\journal_pos.csv')
journal_neg = pd.read_csv(r'.\senti_dict\journal_neg.csv')
journal_senti = pd.concat([journal_pos, journal_neg])

def analyze_text(words, df):
    # 將 DataFrame 轉換成字典，以單詞為鍵，分數為值
    word_scores = df.set_index('text')['score'].to_dict()

    positive_score_sum = 0
    positive_count     = 0
    negative_score_sum = 0
    negative_count     = 0
    words_in_dict      = 0

    for word in words:
        if word in word_scores:
            words_in_dict += 1
            score = word_scores[word]
            if score > 0:
                positive_score_sum += score
                positive_count += 1
            elif score < 0:
                negative_score_sum += score
                negative_count += 1

    return {
        "total_words_in_dict": words_in_dict,
        "positive_score_sum" : positive_score_sum,
        "positive_count"     : positive_count,
        "negative_score_sum" : negative_score_sum,
        "negative_count"     : negative_count
    }


antusd_score_dict = {}

for i, new in tqdm(enumerate(split_news_list)):
    antusd_score_dict[i] = analyze_text(new, antusd)

journal_score_dict = {}

for i, new in tqdm(enumerate(split_news_list)):
    journal_score_dict[i] = analyze_text(new, journal_senti)

#%% 讀取新聞發佈日期時間資料

anue_data = pd.read_csv('anue_clear(256662).csv') 
anue_data = anue_data[['publishAt']]
anue_data['publishAt'] = (pd
                          .to_datetime(anue_data['publishAt'])
                          )
anue_data = anue_data.rename(columns={'publishAt': 'date'})

#%% 05/16 更新，將分數儲存為日與月分數

def aggregate_scores(score_dict, anue_data, period):
    """
    根據提供的字典數據，合併並計算每日或每月的正負得分總和。

    Parameters
    ----------
    score_dict : dict
        從日期映射到得分的字典。
    anue_data : DataFrame
        與 score_dict 數據水平合併的額外 DataFrame。
    period : str
        輸出數據的時期，可以是 'daily' 或 'monthly'。

    Returns
    -------
    DataFrame
        包含每日或每月正負得分總和的 DataFrame。
    """
    # 將字典轉換成 DataFrame 並與 anue_data 合併
    df = pd.DataFrame.from_dict(score_dict, orient='index')
    df = (pd
          .concat([df, anue_data], axis=1)
          )
    df['date'] = pd.to_datetime(df['date']).dt.date  # 只留下日期部分

    # 根據日期分組，計算每日的正負分數總和
    grouped = df.groupby('date').agg({
        'positive_score_sum': 'sum',
        'negative_score_sum': 'sum'
    }).reset_index()

    # 處理可能缺失的日期
    # 沒新聞的日期 2019-10-11 與 2021-06-14
    full_date_range = (pd
                       .date_range(
                           start=grouped['date'].min(),
                           end=grouped['date'].max(),
                           freq='D')
                       )
    grouped.set_index('date', inplace=True)
    grouped = (grouped
               .reindex(full_date_range, fill_value=0)
               .rename_axis('date')
               .reset_index()
               )
    
    # 決定是返回每日還是每月數據
    if period == 'daily':
        return grouped
    
    elif period == 'monthly':
        grouped['month'] = grouped['date'].dt.to_period('M')
        return grouped.groupby('month').agg({
            'positive_score_sum': 'sum',
            'negative_score_sum': 'sum'
        }).reset_index()

#%% 日分數

daily_ant_score = aggregate_scores(antusd_score_dict, anue_data, 'daily')
daily_ant_score = (daily_ant_score
                   .rename(columns={'positive_score_sum': 'pos_ant',
                                    'negative_score_sum': 'neg_ant'})
                   )

daily_jou_score = aggregate_scores(journal_score_dict, anue_data, 'daily')
daily_jou_score = (daily_jou_score
                   .rename(columns={'positive_score_sum': 'pos_jou',
                                    'negative_score_sum': 'neg_jou'})
                   )

daily_score = pd.merge(daily_ant_score, daily_jou_score, on='date')

daily_score['sum_ant'] = daily_score['pos_ant'] + daily_score['neg_ant']
daily_score['sum_jou'] = daily_score['pos_jou'] + daily_score['neg_jou']
  
#%% 月分數

monthly_ant_score = aggregate_scores(antusd_score_dict, anue_data, 'monthly')
monthly_ant_score = (monthly_ant_score
                     .rename(columns={'positive_score_sum': 'pos_ant',
                                      'negative_score_sum': 'neg_ant'})
                     )

monthly_jou_score = aggregate_scores(journal_score_dict, anue_data, 'monthly')
monthly_jou_score = (monthly_jou_score
                     .rename(columns={'positive_score_sum': 'pos_jou',
                                      'negative_score_sum': 'neg_jou'})
                     )

monthly_score = pd.merge(monthly_ant_score, monthly_jou_score, on='month')

monthly_score['sum_ant'] = monthly_score['pos_ant'] + monthly_score['neg_ant']
monthly_score['sum_jou'] = monthly_score['pos_jou'] + monthly_score['neg_jou']

#%% 資料標準化

from standardize_column import standardize_column

std_columns = ['pos_ant', 'neg_ant',
               'pos_jou', 'neg_jou',
               'sum_ant', 'sum_jou']

for column in std_columns:
    daily_score = standardize_column(daily_score, column)

for column in std_columns:
    monthly_score = standardize_column(monthly_score, column)

monthly_score = (monthly_score
                 .rename(columns={'month': 'date'})
                 )

# daily_score.to_csv('daily_journal_score.csv', index = False)
# monthly_score.to_csv('monthly_journal_score.csv', index = False)

#%%

# # 新增星期幾的 column
# daily_score['date'] = pd.to_datetime(daily_score['date'])
# daily_score['day_of_week'] = daily_score['date'].dt.day_name()

# # 分割 DataFrame 為平日和周末
# weekday = daily_score[daily_score['date'].dt.weekday < 5]   # 周一至周五
# weekend = daily_score[daily_score['date'].dt.weekday >= 5]  # 周六至周日

# des_weekday = weekday.describe()
# des_weekend = weekend.describe()

#%% 05/14 更新，將分數儲存為日與月分數 (與上面相同，舊程式碼，已棄用)

# def daily_journal_score(score_dict, period):
#     # 將字典轉換成 DataFrame
#     df = pd.DataFrame.from_dict(score_dict, orient='index')
#     df = pd.concat([df, anue_data], axis=1) # 水平合併
#     df['date'] = (pd
#                   .to_datetime(df['date'])
#                   .dt.date # 只留下日
#                   )
#     # 根據日分組，計算每日的正負分數總和
#     pos_daily = (df
#                  .groupby('date')['positive_score_sum']
#                  .sum()
#                  .reset_index()
#                  )
    
#     neg_daily = (df
#                  .groupby('date')['negative_score_sum']
#                  .sum()
#                  .reset_index()
#                  )
    
#     df_daily = pd.merge(pos_daily, neg_daily, on='date')
    
#     df_daily['date'] = pd.to_datetime(df_daily['date'])
    
#     # 沒新聞的日期 2019-10-11 與 2021-06-14，填充為 0
#     # 確定資料日期範圍
#     start_date = df_daily['date'].min()
#     end_date   = df_daily['date'].max()
#     date_range = pd.date_range(start=start_date, end=end_date, freq='D')

#     # 將 'date' 列設置為索引
#     df_daily.set_index('date', inplace=True)
#     # 重新索引 DataFrame，將缺失的日期用 0 填充
#     df_daily = df_daily.reindex(date_range, fill_value=0)

#     # 將索引列重新變回一個普通列
#     df_daily.reset_index(inplace=True)
#     df_daily.rename(columns={'index': 'date'}, inplace=True)
    
#     if period == 'daily':  
#         return df_daily 
    
#     elif period == 'monthly':   
#         # 根據月分組，計算每月的正負分數總和
#         df_daily['month'] = df_daily['date'].dt.to_period('M')
#         pos_monthly = (df_daily
#                        .groupby('month')['positive_score_sum']
#                        .sum()
#                        .reset_index()
#                        )
#         neg_monthly = (df_daily
#                        .groupby('month')['negative_score_sum']
#                        .sum()
#                        .reset_index()
#                        )
        
#         # 合併每月的正負分數總和
#         df_monthly = pd.merge(pos_monthly, neg_monthly, on='month')
    
#         return df_monthly

# #%% 日分數

# daily_ant_score = daily_journal_score(antusd_score_dict, 'daily')
# daily_ant_score = (daily_ant_score
#                    .rename(columns={'positive_score_sum': 'pos_ant',
#                                     'negative_score_sum': 'neg_ant'})
#                    )

# daily_jou_score = daily_journal_score(journal_score_dict, 'daily')
# daily_jou_score = (daily_jou_score
#                    .rename(columns={'positive_score_sum': 'pos_jou',
#                                     'negative_score_sum': 'neg_jou'})
#                    )

# daily_score = pd.merge(daily_ant_score, daily_jou_score, on='date')

# daily_score['sum_ant'] = daily_score['pos_ant'] + daily_score['neg_ant']
# daily_score['sum_jou'] = daily_score['pos_jou'] + daily_score['neg_jou']

# #%% 月分數

# monthly_ant_score = daily_journal_score(antusd_score_dict, 'monthly')
# monthly_ant_score = (monthly_ant_score
#                      .rename(columns={'positive_score_sum': 'pos_ant',
#                                       'negative_score_sum': 'neg_ant'})
#                      )

# monthly_jou_score = daily_journal_score(journal_score_dict, 'monthly')
# monthly_jou_score = (monthly_jou_score
#                      .rename(columns={'positive_score_sum': 'pos_jou',
#                                       'negative_score_sum': 'neg_jou'})
#                      )

# monthly_score = pd.merge(monthly_ant_score, monthly_jou_score, on='month')

# monthly_score['sum_ant'] = monthly_score['pos_ant'] + monthly_score['neg_ant']
# monthly_score['sum_jou'] = monthly_score['pos_jou'] + monthly_score['neg_jou']

