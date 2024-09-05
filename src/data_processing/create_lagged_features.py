def create_lagged_features(df, columns, lag, drop_columns):
    """
    為指定的 DataFrame 創建 lag 期並移除不需要的列。

    Parameters
    ----------
        df : DataFrame
            原始的 pandas DataFrame，包含需要創建 lag 期的數據。
        columns : list of str
            需要創建 lag 期的列名列表。
        lag : int
            lag 期數。
        drop_columns : list of str
            從 DataFrame 中挑選需要刪除的列名列表。

    Returns
    -------
        DataFrame
            已創建 lag 期並刪除了指定列的 DataFrame。
    """
    for column in columns:
        df[f'lag{lag}_{column}'] = df[column].shift(lag)

    # 移除不需要的列
    df.drop(columns=drop_columns, inplace=True)

    # 移除任何因為創建 lag 而產生含有 NaN 的行
    df.dropna(inplace=True)

    return df
