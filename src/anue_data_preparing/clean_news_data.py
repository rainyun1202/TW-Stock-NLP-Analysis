import pandas as pd
import html
import re
import os

data_path = os.path.join('..', '..', 'data', 'Anue_raw_data(305577).csv')
news_data = pd.read_csv(data_path)

# 該程式碼直接沿用 API 裡的 dirty content (HTML格式)，已經找到方法處理這個問題
# 處理爬蟲新聞資料含有亂碼 HTML 字符問題
# 將 HTML 部分字符解碼，但這個解法不夠完全

news_data['content'] = news_data['content'].apply(lambda x : html.unescape(x))

# 原始的 HTML 內容
# html_content = "&lt;p&gt;集團生產高爾夫小白球、球具及複合材料的明安國際(8938-TW)受惠市場需求回升...&lt;/p&gt;"
# 解碼 HTML 實體字符
# decoded_content = html.unescape(html_content)
# 輸出解碼後的結果
# print(decoded_content)

#%% 刪除 HTML 中所有的<...>

def remove_html_tags_1(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

news_data['content'] = news_data['content'].apply(remove_html_tags_1)

# 範例：刪除所有<...>
# text = "<p>綠能科技(3519-TW)今(9)日公佈101年12月銷貨收入新台幣7.39億元，較上月減少3.7%。公司說明，市場對綠能高階晶片需求仍上揚，就訂單能見度客戶已排隊到農曆年後。</p>"
# pattern = r"<[^>]+>"
# text = re.sub(pattern, "", text)

# print(text)

#%%

# 刪除所有 HTML 相關的字符 (不包含在<>之中也未被解碼出的)
# 定義函數來應用正則表達式 (HTML 亂碼都具有"&....;"的規律)
# clean_str = re.sub('&[a-z]+;', '', example_str)
def remove_html_tags_2(text):
    clean_str = re.sub('&[a-z]+;', '', text)
    return clean_str

news_data['content'] = news_data['content'].apply(remove_html_tags_2)

# 仍有 more... 與 [NT:PAGE=$] 需要清除 (下一頁)
def remove_chars(s):
    s = re.sub(r'more\.\.\.', '', s)
    s = re.sub(r'\[NT:PAGE=\$\]', '', s)
    return s

news_data['content'] = news_data['content'].apply(remove_chars)

# 刪除第一個多餘的 index column (原始資料 to_csv 時未設置 index = False)
news_data = news_data.drop(news_data.columns[0], axis=1)

# 刪除 column content 中的重複值，並保留第一筆資料，共剩下256666篇新聞
# 有的新聞內容一樣，但重複發佈 (newsID不同)，從而造成 HTML 裡面的編碼有些許差異
# 因此要先把資料處理乾淨再來刪除重複的新聞內容
news_data = news_data.drop_duplicates(subset=['content'], keep='first')

#%% 2024/04/09 新增，根據斷詞失敗問題回來刪除多餘、錯誤與無意義文本

news_data = news_data.reset_index(drop=True) # 重新排序 index

news_data = news_data.drop(index = 111441)
news_data = news_data.drop(index = 69974)
news_data = news_data.drop(index = 23271)
news_data = news_data.drop(index = 185722) # drop df 不會改變 index 順序

news_data = news_data.reset_index(drop=True) # 再次重新排序 index

news_data = news_data[['title', 'cor_stock', 'content', 'publishAt']]

# 參考 split_news.py ，直接刪去原始新聞稿內所有換行符與空格，方便輸出成乾淨 .txt
# 執行該操作後的 content 內容與 clean_news_list 相同
news_data['content'] = news_data['content'].apply(
    lambda x : "".join(x.split())
    )

news_data.to_csv('anue_clear(256662).csv', index = False)

#%% 該步驟已更新，移至 split_news.py 處理，新增了股票代碼的自訂義字典

# 資料處理完畢，取出content list做斷詞處理
# news_list = news_data['content'].to_list()

# class NewsAnalyzer:
#     def __init__(self, news_list):
#         self.news_list = news_list
    
#     def SplitList(self):
#         list_size = 100
#         n_lists = len(self.news_list) // list_size + 1
#         BigList = [self.news_list[i*list_size:(i+1)*list_size] for i in range(n_lists)]
#         return BigList
  
#     def process(self):
#         merged_s = []
#         merged_p = []
#         for SmallList in tqdm(self.SplitList()):
#             word_s = ws(SmallList,
#                         sentence_segmentation = True,
#                         segment_delimiter_set = {'?', '？', '!', '！', '。',
#                                                   ',', '，', ';', ':', '、'})
#             word_p = pos(word_s)
#             merged_s.extend(word_s)
#             merged_p.extend(word_p)
#         #word_n = ner(word_s, word_p)
#         return merged_s, merged_p
    
#     def GenResult(self):
#         TidyNews = []
#         result = self.process()
#         for news, news_pos in zip(result[0], result[1]):
#             combine_word = ''
#             for new, new_pos in zip(news, news_pos):
#                 #一行清除所有空格(包括\n \t)
#                 new = ''.join(new.split())
#                 if new_pos != 'WHITESPACE':
#                     combine_word += f'{new}({new_pos}) '
#             combine_word = combine_word[:-1]
#             TidyNews.append(combine_word)
#         return TidyNews
    

# processor = NewsAnalyzer(news_list)
# result = processor.GenResult()

# 將完成的結果存入整理好的DataFrame
# news_data['ckiptagger_content'] = result
# news_data.to_csv('Anue_all_data_clear.csv', index = False)
