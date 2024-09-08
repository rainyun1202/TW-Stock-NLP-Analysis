# 寫出資料 (符合 CopeOpi 腳本要求)
import os
from tqdm import tqdm

# 讀入 txt 寫為 list
data_path = os.path.join('..', '..', 'data', 'anue_news_data')
with open(os.path.join(data_path, 'ckip_news_list.txt'),
          'r', encoding='utf-8') as file:
    lines = file.readlines()
    news_list = [line.rstrip('\n') for line in lines]
    
# 設定儲存檔案的資料夾路徑
folder_path = os.path.join(data_path, 'copeopi_counting')

if not os.path.exists(folder_path):
    os.mkdir(folder_path)

# 建立.lst檔案
with open(os.path.join(folder_path, 'ckip_to_cope_list.lst'),
          'w', encoding='utf-8') as f:
    # 輸出每個.txt檔案
    for i, text in tqdm(enumerate(news_list)):
        # 設定檔案名稱
        file_name = f'{i}.txt'
        file_path = os.path.join(folder_path, file_name)
        # 寫入.txt檔案
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        # 將檔名寫入.lst檔案
        f.write(f'{file_name} {i}\n')

# copeopi_counting 中會包含 255771 個 .txt 檔案，檔名依照索引編號順序排列。 (2024/09/07)
# ckip_to_cope_list.lst 中包含每個檔案的檔名和索引編號，以空格分隔，每個檔案一行。
