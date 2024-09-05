import pandas as pd
from .format_significance import format_significance

def format_reg_model(model, model_name='base_model'):
    """
    處理統計模型的輸出，提取係數、標準誤、p 值與樣本數，
    並將它們格式化為一個符合論文格式的 DataFrame。

    Parameters
    ----------
        model : RegressionResults
            從 statsmodels 得到的迴歸分析結果物件。
        model_name : str
            使用者輸入 model 的名稱，預設為 base_model

    Returns
    -------
        DataFrame
            包含論文所需所有資訊與完整格式的 DataFrame。
    """
    summary = model.summary()

    results_df = pd.DataFrame(summary.tables[1].data) # 將模型結果儲存為可以輸出的 Dataframe 格式
    results_df.columns = results_df.iloc[0] # 設定 columns name
    results_df = results_df.drop(0) # 刪除變成其中一個 row 的多餘原始 columns
    results_df.set_index(results_df.columns[0], inplace=True) # 將 vars 設為 index

    # 提取樣本數、AIC、R² 和 Adj R²
    stats = {
        'Observations': summary.tables[0].data[5][1],
        'AIC': summary.tables[0].data[5][3].replace(".", ""),
        'BIC': summary.tables[0].data[6][3].replace(".", ""),
        'R-squared': summary.tables[0].data[0][3],
        'Adj R-squared': summary.tables[0].data[1][3]
    }

    # 為結果 DataFrame 添加顯著性和格式化係數
    results_df['sig']     = results_df['P>|t|'].apply(format_significance)

    results_df['coef']    = (results_df['coef']
                             .astype(float)
                             .map('{:.3f}'.format)
                             + results_df['sig']                         
                             )

    results_df['std err'] = (results_df['std err']
                             .astype(float)
                             .map('({:.3f})'.format)
                             )

    # 將統計量轉化為 DataFrame
    stats_df = pd.DataFrame(stats.items(), columns=['', 'coef'])
    stats_df.set_index(stats_df.columns[0], inplace=True)

    # 組合 coef 和 std err
    formatted_rows = []
    new_index = []
    for idx, row in results_df.iterrows():
        formatted_rows.append({'coef': row['coef']})
        formatted_rows.append({'coef': row['std err']})
        new_index.append(idx)
        new_index.append(f'{idx}_stderr')

    formatted_df = pd.DataFrame(formatted_rows, index=new_index)

    # 合併統計量和格式化後的 DataFrame
    df_combined = pd.concat([formatted_df, stats_df], axis=0)
    df_combined.rename(columns = {'coef':f'{model_name}'}, inplace = True)
    
    return df_combined
