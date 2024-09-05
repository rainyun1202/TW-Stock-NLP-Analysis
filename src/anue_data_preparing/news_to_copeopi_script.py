# 寫出資料 (符合CopeOpi腳本要求)
import os
from tqdm import tqdm

# 讀入 txt 寫為 list
with open('full_ckip_list.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    news_list = [line.rstrip('\n') for line in lines]
    
# 設定儲存檔案的資料夾路徑 (在目前 py檔相對路徑下新增)
folder_path = '.\copeopi_counting'

# 建立資料夾
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

# 建立.lst檔案，會在當前路徑下，在手動移至 copeopi_counting 中
with open('full_ckip_list.lst', 'w', encoding='utf-8') as f:
    # 輸出每個.txt檔案
    for i, text in tqdm(enumerate(news_list)):
        # 設定檔案名稱
        file_name = f'{i}.txt'
        # 設定檔案完整路徑
        file_path = os.path.join(folder_path, file_name)
        # 寫入.txt檔案
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        # 寫入.lst檔案
        f.write(f'{file_name} {i}\n')

# 在當前目錄下建立一個名為 copeopi_counting 的資料夾
# 以及一個名為 full_ckip_list.lst 的檔案。
# copeopi_counting 中會包含256662個 .txt 檔案，檔名依照索引編號順序排列。
# full_ckip_list.lst 中包含每個檔案的檔名和索引編號，以空格分隔，每個檔案一行。