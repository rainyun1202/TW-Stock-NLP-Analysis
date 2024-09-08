import pandas as pd
import html
import re
import os

data_path = os.path.join('..', '..', 'data', 'anue_news_data')
news_data = pd.read_csv(
    os.path.join(data_path, 'anue_raw_data(305577).csv')
)

# 處理爬蟲新聞資料含有 HTML 亂碼字符問題
# 將 HTML 部分字符解碼，但解法不夠完全 (<p>、照片影片等等仍有殘留)
news_data['content'] = news_data['content'].apply(lambda x : html.unescape(x))

# 範例：
# html_content = "&lt;p&gt;集團生產高爾夫小白球、球具及複合材料的明安國際(8938-TW)受惠市場需求回升...&lt;/p&gt;"
# 解碼 HTML 實體字符
# decoded_content = html.unescape(html_content)
# print(decoded_content)

#%% 刪除 HTML 中所有的 <...>
def remove_html_tags_1(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

news_data['content'] = news_data['content'].apply(remove_html_tags_1)

# 範例：
# text = "<p>綠能科技(3519-TW)今(9)日公佈101年12月銷貨收入新台幣7.39億元，較上月減少3.7%。公司說明，市場對綠能高階晶片需求仍上揚，就訂單能見度客戶已排隊到農曆年後。</p>"
# pattern = r"<[^>]+>"
# text = re.sub(pattern, "", text)
# print(text)

#%% 刪除所有 HTML 相關的字符 (不包含在<>之中也未被解碼出的)
# HTML 亂碼具有 "&....;" 的規律
def remove_html_tags_2(text):
    clean_str = re.sub('&[a-z]+;', '', text)
    return clean_str

news_data['content'] = news_data['content'].apply(remove_html_tags_2)

# 仍有 more... 與 [NT:PAGE=$] 需要清除 (下一頁)
def remove_chars(text):
    text = re.sub(r'more\.\.\.', '', text)
    text = re.sub(r'\[NT:PAGE=\$\]', '', text)
    return text

news_data['content'] = news_data['content'].apply(remove_chars)

# 刪除 column content 中的重複值，並保留第一筆資料，共剩下 256721 篇新聞 (2024/09/07)
# 有的新聞內容一樣但重複發佈 (newsID 不同)，從而造成 HTML 裡面的編碼有些許差異
# 因此要先進行資料清洗再來刪除重複的新聞內容
news_data = news_data.drop_duplicates(subset=['content'], keep='first')

#%%
# 刪去原始新聞稿內所有換行符與空格，確保斷詞過程單純且使格式符合 CopeOpi 要求
news_data['content'] = news_data['content'].apply(
    lambda x : "".join(x.split())
)
news_data = news_data[['title', 'content', 'publishAt']]
save_path = os.path.join('..', '..', 'data', 'anue_news_data', 'anue_clear(256721).csv')
news_data.to_csv(save_path, index=False)

