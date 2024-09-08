# Booking 飯店評論資料清洗 (已完成並放在 conda HANLP_DATA_PATH 中)
import os
from tqdm import tqdm
def is_meaningful(text: str) -> bool:
    """
    刪除無意義評論文本。
    """
    meaningless_texts = ["無", "沒有", "沒", "", "NA", "Na", "na"]
    return text.strip() not in meaningless_texts and text.strip() != ""

def load_folder_to_dataset(folder_path: str) -> dict:
    """
    加載指定資料夾中的文本文件到數據集。
    """
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    data  = {}
    for filename in tqdm(files):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip() # strip 移除文本前後可能出現的 /t /n
            if is_meaningful(text):
                data[f'{filename}'] = text
                # 將文本加載進內存中向量文本分類器
    return data

# 請先自行解壓縮 booking_dataset_original.7z 取得原始檔案
data_path = os.path.join('..', '..', 'data', 'HanLP_dataset', 'BookingDatabase')
clean_pos_data = load_folder_to_dataset('positive')
clean_neg_data = load_folder_to_dataset('negative')

def save_texts_to_files(data: dict, folder_path: str):
    os.makedirs(folder_path, exist_ok=True)

    for file_name, content in tqdm(data.items()):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(content))
    
    return f"Files have been successfully saved to {folder_path}"

save_texts_to_files(clean_pos_data, os.path.join(data_path, 'clean_pos_data'))
save_texts_to_files(clean_neg_data, os.path.join(data_path, 'clean_neg_data'))
