import statsmodels.api as sm
from .format_reg_model import format_reg_model

def run_ols_and_format(df, response_var, model_name):
    """
    執行 OLS 迴歸分析，並對結果進行格式化處理。

    Parameters
    ----------
        df : DataFrame
            要進行迴歸分析的 pandas DataFrame，其中包含應變數和所有解釋變數。
        response_var : str
            指定用作應變數的 DataFrame column name。
        model_name : str
            輸出後模型的名稱 (顯示於 DataFrame column)

    Returns
    -------
        DataFrame
            處理後的迴歸模型結果。
    """
    y = df[response_var]
    X = df.drop(response_var, axis=1)
    X = sm.add_constant(X)
    
    # 執行 OLS 回歸
    model = sm.OLS(y, X).fit()
    
    # 格式化迴歸模型輸出
    format_df = format_reg_model(model, model_name)
    format_df = format_df.rename(index={'const': 'Intercept',
                                        'const_stderr': 'Intercept_stderr'})
    # 重命名索引：移除包含 'stderr' 的 row
    # index_map = {idx: '' if 'stderr' in idx else idx for idx in format_df.index}
    # format_df = format_df.rename(index=index_map)
    
    # 將變量名映射到中文
    # format_df = format_df.rename(index=vars_to_chinese_dict)
    
    return format_df
