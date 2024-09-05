from statsmodels.formula.api import ols

def stepwise_forward_selection(df, response_var, default_vars, aic_bic):
    """
    Forward Selection Procedure 根據 AIC 或 BIC 選擇有效資訊

    Parameters
    ----------
        df : pd.DataFrame
            包含所有變數的 DataFrame
        response_var : str
            作為因變數的列名
        default_vars : list
            預設模型要放入的自變數，不預設則輸入 []
            (AR (1) 預設放入 lag 一期報酬率)
        aic_bic : str
            選擇 AIC 或 BIC 方法
    
    Returns
    -------
        最終模型的統計摘要。
    """
    
    y = response_var
    x_vars = df.columns.drop(y)
    x_vars = [x for x in x_vars if x not in default_vars]
    selected_vars = default_vars.copy()
    
    current_aic_bic = float('inf')

    # 前進選擇法
    while True:
        aic_bic_with_candidates = []
        
        for candidate in x_vars:
            formula = f'{y} ~ ' + ' + '.join(selected_vars + [candidate])
            print(f"Testing formula: {formula}")  # 打印公式以便調試
            candidate_model = ols(formula, data=df).fit()
            if aic_bic == 'aic':
                aic_bic_with_candidates.append((candidate_model.aic,
                                                    candidate))
            else:
                aic_bic_with_candidates.append((candidate_model.bic,
                                                    candidate))        
        # 選擇最小 AIC BIC
        min_aic_bic, best_candidate = min(aic_bic_with_candidates,
                                          default=(float('inf'), None))
        
        # 如果新模型的 AIC BIC 比當前的小，則更新模型
        if min_aic_bic < current_aic_bic:
            current_aic_bic = min_aic_bic
            x_vars.remove(best_candidate)
            selected_vars.append(best_candidate)
        else:
            break

    # 最終模型
    final_formula = f'{y} ~ ' + ' + '.join(selected_vars)
    final_model = ols(final_formula, data=df).fit()
    
    return final_model, aic_bic_with_candidates
