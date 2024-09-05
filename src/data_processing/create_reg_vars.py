def create_reg_vars(data, base_vars, add_vars=None):
    """
    創建迴歸變數之數據集。
    
    Parameters
    ----------
        data : DataFrame
            包含所有數據的 DataFrame。
        base_vars : list
            基本迴歸變數列表。
        add_vars : list
            需要額外添加的迴歸變數列表。
    
    Returns
    -------
        DataFrame
            包含選定迴歸變數 DataFrame。
    """
    if add_vars is not None:
        vars_list = base_vars + add_vars
    else:
        vars_list = base_vars
    
    return data[vars_list]