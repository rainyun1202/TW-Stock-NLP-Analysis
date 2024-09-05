import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from xgboost import XGBClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

import os
import sys
from pathlib import Path
current_working_directory = Path(os.getcwd())
project_root = current_working_directory.parents[1]
sys.path.append(str(project_root / 'src'))
from data_processing import add_djia_in_df
from utils import calculate_ml_aic_bic, ml_train_test_split

#%% 讀取整理好的所有模型變數 Dataframe

data_dir = project_root / 'data'

with pd.HDFStore(data_dir / 'ml_vars_dict.h5') as store:
    ml_vars_dict = {key.strip('/'): store[key] for key in store.keys()}
# 加入 DJIA 報酬率
ml_vars_djia_dict = add_djia_in_df(ml_vars_dict,
                                   data_dir / 'daily_reg_data.csv',
                                   data_dir / 'taiwan_time_DJIA.csv')

#%% 全部猜漲 (長期看漲並持有)
from sklearn.base import BaseEstimator, ClassifierMixin

class AlwaysRiseClassifier(BaseEstimator, ClassifierMixin):
    def fit(self, X, y=None):
        return self

    def predict(self, X):
        return [1] * len(X)

    def predict_proba(self, X):
        return [[0, 1] for _ in range(len(X))]

# df = ml_vars_dict['base_vars']
# X_train, X_test, y_train, y_test =  ml_train_test_split(df,
#                                                         'daily_return',
#                                                         train_size=0.7)
# smote = SMOTE()
# X_res, y_res = smote.fit_resample(X_train, y_train)

# rise = AlwaysRiseClassifier()
# rise.fit(X_res, y_res)

# y_pred = rise.predict(X_test)
# cm = confusion_matrix(y_test, y_pred)
# print(pd.DataFrame(cm, index=['實際跌', '實際漲'],
#                    columns=['預測跌', '預測漲']))

# print()
# # 計算整體正確率
# accuracy = accuracy_score(y_test, y_pred)
# # 使用 round 函數進行四捨五入
# print('測試集正確率:', round(accuracy, 4))
# print('綜合報告')
# print(classification_report(y_test, y_pred, digits=4))
# train_size 0.9：117/246 = 47.56%
# train_size 0.8：248/491 = 50.51%
# train_size 0.7：388/736 = 52.72%

#%% 執行並輸出 ML EXCEL 結果
def get_classification_report(y_test, y_pred):
    report = classification_report(y_test, y_pred, digits=4,
                                   output_dict=True, zero_division=0)
    df_classification_report = pd.DataFrame(report).transpose()
    df_classification_report.rename(index={'0': '跌',
                                           '1': '漲',
                                           'weighted avg': 'F1-Score (w_avg)'},
                                    inplace=True)
    return df_classification_report

class_report_dict = {}
y_pred_dict = {}

def output_ml_result(modelname, train_size, input_df, senti):
    accuracies = []
    classification_reports = []
    y_pred_list = []

    for i in range(10): # 執行 10 次訓練來計算平均結果
        X_train, X_test, y_train, y_test = ml_train_test_split(input_df, 
                                                               'daily_return', 
                                                               train_size,
                                                               True)

        column_exists = 'lag1_djia_daily_return' in input_df.columns
        smote = SMOTE()
        X_res, y_res = smote.fit_resample(X_train, y_train)
        
        if modelname == 'rise':
            model = AlwaysRiseClassifier()
        elif modelname == 'lr':
            model = LogisticRegression(max_iter=1000)
        elif modelname == 'svc':
            model = SVC(probability=True)
        elif modelname == 'rfc':
            model = RandomForestClassifier(max_depth=2)
        elif modelname == 'xgb':
            model = XGBClassifier(n_estimators=100,
                                  max_depth=2,
                                  learning_rate=0.03,
                                  objective='binary:logistic')
        elif modelname == 'sv':
            model_lr  = LogisticRegression(max_iter=1000)
            model_svc = SVC(probability=True)
            model_rfc = RandomForestClassifier(max_depth=2)
            model = VotingClassifier([
                ('lr', model_lr),
                ('svc', model_svc),
                ('rfc', model_rfc)],
                voting='soft')
        elif modelname == 'lstm':
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_res)
            X_test_scaled  = scaler.transform(X_test)
            # LSTM 需要資料為三維格式 [樣本, 時間步, 特徵]
            X_train_scaled = X_train_scaled.reshape(X_train_scaled.shape[0], 1, X_train_scaled.shape[1])
            X_test_scaled  = X_test_scaled.reshape(X_test_scaled.shape[0], 1, X_test_scaled.shape[1])
            # 建立模型
            model = Sequential()
            model.add(LSTM(50, return_sequences=True, input_shape=(1, X_train_scaled.shape[2])))
            model.add(LSTM(50))
            model.add(Dropout(0.2))
            model.add(Dense(1, activation='sigmoid'))         
            # 編譯模型
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        if modelname == 'lstm':
            # 訓練模型
            model.fit(X_train_scaled, y_res, epochs=10, batch_size=32, validation_split=0.2)
            y_pred = model.predict(X_test_scaled)
            y_pred = (y_pred > 0.5).astype(int)
        
        else:
            model.fit(X_res, y_res)
            y_pred = model.predict(X_test)

        # 計算整體正確率
        current_accuracy = accuracy_score(y_test, y_pred)
        accuracies.append(current_accuracy)
        classification_reports.append(get_classification_report(y_test, y_pred))
        y_pred_list.append(y_pred)
    # 計算平均正確率
    avg_accuracy = np.mean(accuracies)
    print(f'{modelname}平均正確率：{avg_accuracy:.4f}，訓練集大小：{train_size}，情緒指標：{senti}')

    # 計算平均綜合報告
    avg_classification_report = sum(classification_reports) / len(classification_reports)
    avg_classification_report = avg_classification_report.round(4)
    print('平均綜合報告')
    print(avg_classification_report)
    
    # 確保目標目錄存在
    output_dir = data_dir / 'try_new_all_ml_result'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 根據 column_exists 的值寫入文件
    if column_exists:
        output_path = output_dir / f'{train_size}_{modelname}_{senti}_tw_djia.xlsx'
    else:
        output_path = output_dir / f'{train_size}_{modelname}_{senti}_tw.xlsx'
    
    avg_classification_report.to_excel(output_path, float_format='%.4f')
        
    return classification_reports, y_pred_list

keys = ['base_vars', 'lag1_booking_senti', 'lag1_chn_senti',
        'lag1_cope_senti', 'lag1_pos_neg_ant', 'lag1_pos_neg_jou']

ml_df_dict = {key: ml_vars_dict[key] for key in keys if key in ml_vars_dict}
ml_djia_df_dict = {key: ml_vars_djia_dict[key] for key in keys if key in ml_vars_djia_dict}

train_sizes = [0.9, 0.8, 0.7]
models = ['rise', 'lr', 'svc', 'rfc', 'xgb', 'sv', 'lstm']

for modelname in models:
    for train_size in train_sizes:
        for key, df in ml_df_dict.items():
            class_report_dict[f'{key}_{modelname}_{train_size}'] = (
                output_ml_result(modelname, train_size, df, key)[0])
            y_pred_dict[f'{key}_{modelname}_{train_size}'] = (
                output_ml_result(modelname, train_size, df, key)[1])

for modelname in models:
    for train_size in train_sizes:
        for key, df in ml_djia_df_dict.items():
            class_report_dict[f'{key}_{modelname}_{train_size}_djia'] = (
                output_ml_result(modelname, train_size, df, key)[0])
            y_pred_dict[f'{key}_{modelname}_{train_size}_djia'] = (
                output_ml_result(modelname, train_size, df, key)[1])

#%% 暫時使用 pickle 儲存資料 (資料暫時放在 scripts 中)
# import pickle

# with open(data_dir / 'binary_class_report_dict.pkl', 'wb') as f:
#     pickle.dump(class_report_dict, f)

# with open(data_dir / 'binary_y_pred_dict.pkl', 'wb') as f:
#     pickle.dump(y_pred_dict, f)

# 讀取 pkl 檔案
# with open(data_dir / 'binary_class_report_dict.pkl', 'rb') as f:
#     class_report_dict = pickle.load(f)

# with open(data_dir / 'binary_y_pred_dict.pkl', 'rb') as f:
#     y_pred_dict = pickle.load(f)

#%% 合併相同測試集大小與情緒指標的 ML 結果至同一個 EXCEL 檔案中
def read_and_combine(directory, train_sizes, keys, models, djia=False):
    # 預定義數據結構來儲存整合後的結果
    final_results = {}
    
    for train_size in train_sizes:
        for key in keys:
            # 準備儲存各模型結果的 DataFrame
            data = {
                'accuracy': [],
                'precision (1)': [],
                'precision (-1)': [],
                'recall (1)': [],
                'recall (-1)': [],
                'F1-Score (1)': [],
                'F1-Score (-1)': [],
                'F1-Score (w_avg)': []
            }

            for model in models:
                suffix = "TW+DJIA" if djia else "TW"
                filename = f"{train_size}_{model}_{key}_tw{'_djia' if djia else ''}.xlsx"
                
                file_path = os.path.join(directory, filename)
                
                if os.path.exists(file_path):
                    # 確保正確讀取 index
                    df = pd.read_excel(file_path, index_col=0)
                    data['accuracy'].append(df.loc['accuracy', 'f1-score'])
                    data['precision (1)'].append(df.loc['漲', 'precision'])
                    data['precision (-1)'].append(df.loc['跌', 'precision'])
                    data['recall (1)'].append(df.loc['漲', 'recall'])
                    data['recall (-1)'].append(df.loc['跌', 'recall'])
                    data['F1-Score (1)'].append(df.loc['漲', 'f1-score'])
                    data['F1-Score (-1)'].append(df.loc['跌', 'f1-score'])
                    data['F1-Score (w_avg)'].append(df.loc['F1-Score (w_avg)', 'f1-score'])
                else:
                    # 文件不存在時填充空值或預設值
                    for metric in data:
                        data[metric].append(None)
            
            # 將當前 key 的結果保存到 final_results
            results_df = pd.DataFrame(data, index=[f"{model} {suffix}" for model in models])
            final_results[f"{train_size} ({key})"] = results_df.T  # Transpose for desired format
    
    return final_results

directory = data_dir / 'binary_ml_result'
train_sizes = [0.9, 0.8, 0.7]
keys = ['base_vars', 'lag1_booking_senti', 'lag1_chn_senti', 'lag1_cope_senti', 'lag1_pos_neg_ant', 'lag1_pos_neg_jou']
models = ['rise', 'lr', 'svc', 'rfc', 'xgb', 'sv', 'lstm']

tw_results   = read_and_combine(directory, train_sizes, keys, models)
djia_results = read_and_combine(directory, train_sizes, keys, models, True)

# 將結果保存到 Excel
with pd.ExcelWriter(data_dir / 'combined_results.xlsx') as writer:
    for name, df in tw_results.items():
        df.to_excel(writer, sheet_name=f"{name} TW")
    for name, df in djia_results.items():
        df.to_excel(writer, sheet_name=f"{name} TW+DJIA")
