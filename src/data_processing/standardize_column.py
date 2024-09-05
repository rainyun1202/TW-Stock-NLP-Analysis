def standardize_column(df, column_name):
    """
    計算指定 DataFrame 中指定列的標準化值，並將其添加為新列。

    Parameters
    ----------
        df : DataFrame
            原始的 pandas DataFrame，包含需要進行標準化處理的數據。
        column_name : str
            需要進行標準化處理的列名。

    Returns
    -------
        DataFrame
            在原始 DataFrame 中新增列名稱為 'std_' 加上原列名，為標準化後數據。

    """
    # 計算標準差和平均值
    std  = df[column_name].std()
    mean = df[column_name].mean()

    # 定義標準化函數
    standardize = lambda x: (x - mean) / std

    # 應用標準化並創建新列
    new_column_name = f'std_{column_name}'
    df[new_column_name] = df[column_name].apply(standardize)

    return df