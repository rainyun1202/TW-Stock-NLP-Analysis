from pyhanlp import *
from tqdm import tqdm
import os
import json
import pandas as pd

#%%
data_path = os.path.join('..', '..', 'data')
with open(os.path.join(data_path, 'anue_news_data', 'clean_news_list.txt'),
          'r', encoding='utf-8') as file:
    lines = file.readlines()
    news_list = [line.rstrip('\n') for line in lines]

def trad_to_simp(trad_news):
    simp_news = []
    for new in tqdm(trad_news):
        simp_new = HanLP.tw2s(new) # 文本台灣正體轉簡體
        simp_news.append(simp_new)
    return simp_news

simp_news = trad_to_simp(news_list)

# with open('simp_news_list.txt', 'w', encoding='utf-8') as file:
#     for item in simp_news:
#         file.write(str(item) + '\n')

#%% HanLP 提供之數據測試
# 下載資料庫，如果資料庫已經存在，則直接加載路徑
import zipfile
from pyhanlp.static import download, remove_file, HANLP_DATA_PATH

def test_data_path():
    """
    獲取測試目錄路徑，位於 $pyhanlp/static/data/test，根目錄由配置文件指定。
    """
    data_path = os.path.join(HANLP_DATA_PATH, 'test')
    if not os.path.isdir(data_path): # 創建 test 資料夾保存訓練集文本
        os.mkdir(data_path)
    return data_path

def ensure_data(data_name, data_url):
    root_path = test_data_path()
    dest_path = os.path.join(root_path, data_name)
    if os.path.exists(dest_path):
        return dest_path
    if data_url.endswith('.zip'):
        dest_path += '.zip'
    download(data_url, dest_path)
    if data_url.endswith('.zip'):
        with zipfile.ZipFile(dest_path, "r") as archive:
            archive.extractall(root_path)
        remove_file(dest_path)
        dest_path = dest_path[:-len('.zip')]
    return dest_path

sogou_corpus_path = ensure_data('搜狗文本分類語料庫迷你版',
                                'http://file.hankcs.com/corpus/sogou-text-classification-corpus-mini.zip')

# 中文情感挖掘語料-ChnSentiCorp 譚松波
chn_senti_corp = ensure_data("ChnSentiCorp情感分析酒店評論 (譚松波)",
                             "http://file.hankcs.com/corpus/ChnSentiCorp.zip")

#%% 自訂義向量化與分類器函數實現

FileDataSet = JClass('com.hankcs.hanlp.classification.corpus.FileDataSet')
MemoryDataSet = JClass('com.hankcs.hanlp.classification.corpus.MemoryDataSet')

BigramTokenizer = JClass('com.hankcs.hanlp.classification.tokenizers.BigramTokenizer')
HanLPTokenizer = JClass('com.hankcs.hanlp.classification.tokenizers.HanLPTokenizer')

NaiveBayesClassifier = JClass('com.hankcs.hanlp.classification.classifiers.NaiveBayesClassifier')
Evaluator = JClass('com.hankcs.hanlp.classification.statistics.evaluations.Evaluator')

my_data_path = os.path.join(HANLP_DATA_PATH, 'test', 'booking_sentiment_dataset')

def pipeline(
    classifier, tokenizer, data_path,
    training_size, testing_size, predict_data
):
    training_corpus = FileDataSet().setTokenizer(tokenizer).load(
        data_path, "UTF-8", training_size)

    classifier.train(training_corpus)

    testing_corpus = MemoryDataSet(classifier.getModel()).load(
        data_path, "UTF-8", testing_size)
    
    result = Evaluator.evaluate(classifier, testing_corpus)

    senti_list = []

    for new in tqdm(predict_data):
        senti = classifier.classify(new)
        senti_list.append(senti)
        
    return senti_list, result

#%% 不同資料集情緒分析 (2024/09/08 配合重新爬取的新聞資料重新計算分析)

# 譚松波 90% 訓練集 10% 測試集，197268 篇負面 (總篇數 255771 篇，使用簡體新聞)
chn_senti, chn_result = pipeline(NaiveBayesClassifier(),
                                 BigramTokenizer(),
                                 chn_senti_corp,
                                 0.9, -0.1, simp_news)
print(chn_result) # 90% - 10% 比 80% - 20% 正確率更高

# 譚松波 90% 訓練集 10% 測試集，197136 篇負面 (總篇數 255771 篇，使用繁體新聞)
chn_trad_senti, chn_trad_result = pipeline(NaiveBayesClassifier(),
                                           BigramTokenizer(),
                                           chn_senti_corp,
                                           0.9, -0.1, news_list)
print(chn_trad_result) # 模型準確率與召回率與簡體結果一致

# booking 80% 訓練集 20% 測試集，239715 篇負面 (總篇數 255771 篇，使用簡體新聞)
booking_senti, booking_result = pipeline(NaiveBayesClassifier(),
                                         BigramTokenizer(),
                                         my_data_path,
                                         0.8, -0.2, simp_news)
print(booking_result) # 準確率召回率更高了 (執行時間較長)

#%% 簡易確認負面新聞頻率
def check_negative(sentiment_list):
    i = 0
    for senti in sentiment_list:
        if senti == '负面' or senti == 'negative':
            i += 1
    print(f'共有 {i} 篇負面情緒新聞文本')

check_negative(chn_senti)
check_negative(chn_trad_senti)
check_negative(booking_senti)

#%% 將所有情緒分數資訊彙整成一個 DataFrame

column_names = ['new_index', 'score', 'sentiment']
copeopi_score = pd.read_csv(
    os.path.join(data_path, 'copeopi_senti_score.csv'),
    names=column_names
)
copeopi_score = copeopi_score.rename(
    columns={'score': 'cope_senti_score',
             'sentiment': 'cope_senti'}
)
copeopi_score = copeopi_score[['cope_senti_score', 'cope_senti']]

copeopi_score['chn_senti'] = chn_senti
copeopi_score['booking_senti'] = booking_senti

def encoded_sentiment(senti):
    if senti == 'Positive' or senti == 'positive' or senti == '正面':
        return 1
    else:
        return -1
        
copeopi_score['cope_senti'] = (copeopi_score['cope_senti']
                               .apply(encoded_sentiment)
                               )
copeopi_score['chn_senti'] = (copeopi_score['chn_senti']
                               .apply(encoded_sentiment)
                               )
copeopi_score['booking_senti'] = (copeopi_score['booking_senti']
                               .apply(encoded_sentiment)
                               )

# copeopi_score.to_csv(os.path.join(data_path, 'all_senti_score.csv'), index=False)

#%% 搜狗文本分類語料庫迷你版書本讀取範例 (HanLP 為中國語料庫，因此使用的是簡體中文)

# MemoryDataSet = JClass('com.hankcs.hanlp.classification.corpus.MemoryDataSet')

# dataSet_sogou = MemoryDataSet() # ①將數據集加載到內存中
# dataSet_sogou.load(sogou_corpus_path) # ②加載data/test/搜狗文本分類語料庫迷你版
# dataSet_sogou.add("自然语言处理", "自然语言处理很有趣") # ③新增類別與樣本
# allClasses = dataSet_sogou.getCatalog().getCategories() # ④獲取類別資訊
# print("標註集：%s" % (allClasses))
# for document in dataSet_sogou.iterator():
#     print("第一篇文檔的類別：" + allClasses.get(document.category))
#     break

#%% 譚松波語料庫訓練範例 (HanLP 為中國語料庫，因此使用的是簡體中文)

# NaiveBayesClassifier = JClass('com.hankcs.hanlp.classification.classifiers.NaiveBayesClassifier')

# def predict(classifier, text):
#     print("《%s》 情感极性是 【%s】" % (text, classifier.classify(text)))

# classifier = NaiveBayesClassifier()
# # 创建分类器，更高级的功能请参考 IClassifier 的接口定义
# classifier.train(chn_senti_corp)
# # 训练后的模型支持持久化，下次就不必训练了
# predict(classifier, "前台客房服务态度非常好！早餐很丰富，房价很干净。再接再厉！")
# predict(classifier, "结果大失所望，灯光昏暗，空间极其狭小，床垫质量恶劣，房间还伴着一股霉味。")
# predict(classifier, "可利用文本分类实现情感分析，效果不是不行")
