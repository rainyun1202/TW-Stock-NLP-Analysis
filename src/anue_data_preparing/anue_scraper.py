import os
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
import logging
import time
taiwan_tz = timezone(timedelta(hours=8)) # 台灣時區為 UTC+8

# logging 配置
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 文件處理器 - 將日誌輸出到 'anue_scraper.log'
file_handler = logging.FileHandler('anue_scraper.log')
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
# 控制台處理器 - 將日誌顯示在控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

# 添加處理器到 logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 請求錯誤重試機制
def get_page(url: str, retries: int = 3):
    for i in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status() # 檢查請求是否成功
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            if i < retries - 1:
                time.sleep(2)
            else:
                logging.error("Max retries reached.")
                return None

def parse_page_content(response):
    if response:
        try:
            data = json.loads(response.text)
            return data['items']['data'] # 擷取所需新聞數據
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return []
    return []

# 生成起始日期和結束日期之間固定間隔的 time dict
def generate_dates(start_year: int, end_year: int, interval: int) -> list:
    """
    生成起始日期和結束日期之間固定間隔的 time dict

    Parameters
    ----------
    start_year : int
        起始年份
    end_year : int
        結束年份 (僅到輸入年份第一天，即 01/01)
    interval : int
        時間間隔 (天)

    Returns
    -------
    list :
        固定間格日期之時間資料 (Unix timestamp)。
    """
    start_date = datetime(start_year, 1, 1, tzinfo=taiwan_tz)
    end_date   = datetime(end_year, 1, 1, tzinfo=taiwan_tz)
    date_dict  = {}

    while start_date < end_date:
        date_int = int(datetime.timestamp(start_date))
        date_dict[start_date] = date_int
        start_date += timedelta(days=interval)
        
    if start_date != end_date:
        date_int = int(datetime.timestamp(end_date))
        date_dict[end_date] = date_int
    
    # 按日期順序排列字典的 key
    sorted_dates = sorted(date_dict.keys())

    # 生成相鄰的時間範圍 (Unix timestamp)
    time_ranges = [
        (date_dict[sorted_dates[i]], date_dict[sorted_dates[i + 1]])
        for i in range(len(sorted_dates) - 1)
    ]
    
    return time_ranges

def scrape_anue_news(start_year: int, end_year: int, interval: int):
    """
    根據生成的日期範圍，批量抓取新聞資料。

    Parameters
    ----------
    start_year : int
        起始年份
    end_year : int
        結束年份
    interval : int
        每次請求的時間區間長度（天）

    Returns
    -------
    dict :
        指定期間的所有新聞抓取結果。
    """
    # 取得固定日期間隔的 Unix 時間範圍
    time_ranges = generate_dates(start_year, end_year, interval)
    
    # 存儲所有新聞資料的字典
    all_anue = {}

    # 依據日期範圍批次抓取新聞資料
    for start_unix, end_unix in time_ranges:
        end_unix   = end_unix - 1 # 避免重複抓取到 end_date 0 點整的新聞
        
        start_date = (datetime
                      .fromtimestamp(start_unix, tz=taiwan_tz)
                      .strftime('%Y-%m-%d') # %H:%M:%S 確認時間時區正確
                      )
        end_date   = (datetime
                      .fromtimestamp(end_unix, tz=taiwan_tz)
                      .strftime('%Y-%m-%d')
                      )
        
        logging.info(f'正在獲取 {start_date} ~ {end_date} 的資料')

        # 先爬取第一頁同時獲取總頁數
        url = f'https://news.cnyes.com/api/v3/news/category/tw_stock?startAt={start_unix}&endAt={end_unix}&limit=30'
        first_page = get_page(url)
        if not first_page:
            logging.error(f"無法獲取 {start_date} ~ {end_date} 的數據，跳過...")
            continue
        
        news_data = parse_page_content(first_page)
        if not news_data:
            logging.error(f"{start_date} ~ {end_date} 無法解析新聞資料，跳過...")
            continue

        all_anue[f'{start_date}~{end_date}'] = news_data # 第一頁的新聞數據

        # 獲取總頁數
        try:
            last_page = json.loads(first_page.text)['items']['last_page']
            logging.info(f'總共 {last_page} 頁')
        except KeyError:
            logging.error(f"無法解析總頁數，跳過 {start_date} ~ {end_date} 的數據")
            continue

        # 爬取剩餘頁數的新聞
        for page_num in range(2, last_page + 1):
            logging.info(f'正在獲取第 {page_num} 頁的新聞資料')
            page_url = f'https://news.cnyes.com/api/v3/news/category/tw_stock?startAt={start_unix}&endAt={end_unix}&limit=30&page={page_num}'
            response = get_page(page_url)
            page_news_data = parse_page_content(response)
            if page_news_data:
                all_anue[f'{start_date}~{end_date}'].extend(page_news_data)
    return all_anue

# 爬取新聞資料，執行時間約 150 分鐘。
all_anue = scrape_anue_news(2013, 2023, 9)

#%% 將資料整理儲存為 DataFrame
# 2024/09/06 更新，最終 2013-01-01 ~ 2023-01-01，共 305577 篇
def extract_news_data(news_dict: dict, timezone: str) -> pd.DataFrame:
    data = [
        {
            'publishAt': (datetime
                          .fromtimestamp(news['publishAt'], tz=timezone)
                          .strftime('%Y-%m-%d')
                          ),
            'newsID': news['newsId'],
            'title': news['title'],
            'content': news['content'],
            'summary': news['summary'],
            'cor_stock': news['market']
        }
        for news_list in news_dict.values()
        for news in news_list
    ]
    
    return pd.DataFrame(data)

save_path = os.path.join('..', '..', 'data', 'Anue_raw_data(305577).csv')
# all_anue_df.to_csv(save_path, index=False)
