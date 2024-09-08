import pandas as pd
from ckiptagger import WS, POS, construct_dictionary
import logging
from typing import List, Tuple
from tqdm import tqdm
import os

# CkipTagger data 路徑
ws  = WS('./ckip_data')
pos = POS('./ckip_data')

data_path = os.path.join('..', '..', 'data', 'anue_news_data')
news_data = pd.read_csv(os.path.join(data_path, 'anue_clear(256721).csv'))
news_list = list(news_data['content'])
# 使用列表解析式移除 None、NaN 和空字串 (共三篇)
clean_list = [x for x in news_list if not (pd.isnull(x) or x == '')]
# 刪除無意義大量文本 (10 萬字基金名稱整理、當日重點新聞整理等等，共 947 篇)
clean_list = [x for x in clean_list if not (len(x) > 4000)]

#%% 自製股票名稱的專屬字典新增至預設 ANTUSD 中，以正確識別股票名稱並更精準的斷詞
def get_stock_dict():
    stock_id_df_1 = pd.read_csv(
        os.path.join(data_path, '上市股票代碼.csv')
    )
    stock_id_df_2 = pd.read_csv(
        os.path.join(data_path, '上櫃股票代碼.csv')
    )
    stock_df = pd.concat([stock_id_df_1, stock_id_df_2])
    stock_df[['id', 'name']] = (
        stock_df['id_name'].str.split('　', n = 1, expand = True)
    )
    stock_list = list(stock_df['name'])
    stock_weight_dict = dict((name, 1) for name in stock_list)
    
    return stock_weight_dict

stock_dict = get_stock_dict()
dict_for_CKIP = construct_dictionary(stock_dict)

#%%
# 設定 logging 格式與日誌輸出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("split_news.log"),
        logging.StreamHandler()
    ]
)

class NewsAnalyzer:
    """
    分析新聞文本數據，使用 CkipTagger 進行新聞斷詞與詞性標注，
    並生成符合 CopeOpi 要求的新聞文本，以利進行後續情緒分數之計算。

    Attributes
    ----------
    news_list : list
        新聞文本列表。
    dictionary : List
        斷詞所使用的自定義詞典，排除股票名稱可能產生的情緒。
    """

    def __init__(self, news_list: List[str], dictionary: List[Tuple]):
        """
        初始化 NewsAnalyzer 類的實例。

        Parameters
        ----------
        news_list : list
            新聞文本列表。
        dictionary : dict
            斷詞所使用的自定義詞典。
        """
        self.news_list = news_list
        self.dictionary = dictionary

    def ckiptagger(
        self,
        list_size: int = 100
    ) -> Tuple[List[List[str]], List[List[str]], List[List[str]]]:
        """
        使用 CkipTagger 對新聞列表進行斷詞和詞性標注。

        Parameters
        ----------
        list_size : int, optional
            每批處理的新聞數量，預設值為 100。

        Returns
        -------
        tuple
            包含斷詞結果、詞性標注結果和處理錯誤的新聞列表。
        """
        merged_s, merged_p, error_news = [], [], []
        count = 0

        for i in tqdm(range(0, len(self.news_list), list_size)):
            small_list = self.news_list[i:i + list_size]
            try:
                word_s = ws(
                    small_list,
                    sentence_segmentation=True,
                    segment_delimiter_set={
                        '?', '？', '!', '！', '。', ',', '，', ';', ':', '、'
                    },
                    coerce_dictionary=self.dictionary
                )
                word_p = pos(word_s)
                merged_s.extend(word_s)
                merged_p.extend(word_p)
                count += len(small_list)
                logging.info(f'前 {count} 篇新聞斷詞成功!')
            except Exception as e:
                error_news.append(small_list)
                logging.error(f'處理第 {count + 1} ~ {count + len(small_list)} 篇新聞時發生錯誤: {e}')
                count += len(small_list)

        return merged_s, merged_p, error_news

    def gen_result(self) -> Tuple[List[str], List[List[str]]]:
        """
        生成整理好的新聞斷詞和詞性標注結果。

        Returns
        -------
        tuple
            包含整理好的新聞斷詞結果列表和處理過程中遇到錯誤的新聞列表。
        """
        tidy_news = []
        result = self.ckiptagger()

        for news, news_pos in zip(result[0], result[1]):
            combine_word = ' '.join(
                f'{"".join(word.split())}({pos})' # 一行清除 word 所有空格 (包括\n \t)
                for word, pos in zip(news, news_pos) if pos != 'WHITESPACE'
            )
            tidy_news.append(combine_word)

        return tidy_news, result[2]

# 約 1 秒可以處理 10 篇新聞斷詞，執行該程式碼約需 8 小時 (i7-12700, 64GB 記憶體)
processor = NewsAnalyzer(clean_list, dict_for_CKIP)
ckip_list, error_news = processor.gen_result()

#%% 將結果儲存為 txt
with open(os.path.join(data_path, 'ckip_news_list.txt'),
          'w', encoding='utf-8') as file:
    for item in ckip_list:
        file.write(f'{item}\n')

with open(os.path.join(data_path, 'clean_news_list.txt'),
          'w', encoding='utf-8') as file:
    for item in clean_list:
        file.write(f'{item}\n')

# 讀入 txt 寫為 list
# with open(os.path.join(data_path, 'ckip_list.txt'),
#           'r', encoding='utf-8') as file:
#     lines = file.readlines()
#     ckip_list = [line.rstrip('\n') for line in lines]

