def format_significance(p_value):
    """
    根據 p value 返回相應的統計顯著性標記。

    Parameters
    ----------
        p_value : float
            模型中變數的 p 值。

    Returns
    -------
        str
            返回統計顯著性標記 ('***', '**', '*', '')。
    """
    if float(p_value) < 0.001:
        return '***'
    elif float(p_value) < 0.01:
        return '**'
    elif float(p_value) < 0.05:
        return '*'
    else:
        return ''
