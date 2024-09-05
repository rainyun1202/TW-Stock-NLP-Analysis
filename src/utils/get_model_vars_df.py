import pandas as pd

# 定義 index 順序，依此得到所有使用前進選擇法會用到的變數；或者基本模型變數
# sfs_vars_dict = {}
# for df in all_model_result.values():
#     for index in df.index:
#         sfs_vars_dict[index] = ''
# sfs_vars_dict.keys()
# 此僅列出所有經前進選擇法挑選後有留下的模型變數

def get_model_vars_df(model):
    """
    輸出排序整齊的所有模型變數 index DataFrame。
    包含 Observations, AIC, BIC, R-squared, Adj R-squared

    Parameters
    ----------
        model : str
            sfs 為所有使用前進選擇法會用到的變數
            base 為所有使用 OLS 會用到的變數

    Returns
    -------
        DataFrame
            包含論文所需變數排序整齊的 index DataFrame。
    """
    if model == 'sfs':
        sfs_vars = pd.DataFrame(
            index = ['Intercept', 'Intercept_stderr',
                     'lag1_daily_return', 'lag1_daily_return_stderr',
                     'lag1_cpi_grate', 'lag1_cpi_grate_stderr',
                     'lag1_M1B_grate', 'lag1_M1B_grate_stderr',
                     'lag1_un_rate', 'lag1_un_rate_stderr',
                     'lag1_ipi_grate', 'lag1_ipi_grate_stderr',
                     'lag1_shtmrg', 'lag1_shtmrg_stderr',
                     'lag1_market_turn', 'lag1_market_turn_stderr',
                     'std_lag1_volume', 'std_lag1_volume_stderr',
                     'booking_senti', 'booking_senti_stderr',
                     'cope_senti_score', 'cope_senti_score_stderr',
                     'std_pos_ant', 'std_pos_ant_stderr',
                     'std_neg_ant', 'std_neg_ant_stderr',
                     'std_sum_ant', 'std_sum_ant_stderr',
                     'std_pos_jou', 'std_pos_jou_stderr',
                     'std_neg_jou', 'std_neg_jou_stderr',
                     'std_sum_jou', 'std_sum_jou_stderr',
                     'lag1_cope_senti_score', 'lag1_cope_senti_score_stderr',
                     'lag1_std_pos_ant', 'lag1_std_pos_ant_stderr',
                     'lag1_std_neg_ant', 'lag1_std_neg_ant_stderr',
                     'lag1_std_sum_ant', 'lag1_std_sum_ant_stderr',
                     'lag1_std_pos_jou', 'lag1_std_pos_jou_stderr',
                     'lag1_std_neg_jou', 'lag1_std_neg_jou_stderr',
                     'lag1_std_sum_jou', 'lag1_std_sum_jou_stderr',
                     'Observations', 'AIC', 'BIC', 'R-squared', 'Adj R-squared'])
        return sfs_vars
    
    elif model == 'base':
        base_vars = pd.DataFrame(
            index = ['Intercept', 'Intercept_stderr',
                     'lag1_daily_return', 'lag1_daily_return_stderr',
                     'lag1_cpi_grate', 'lag1_cpi_grate_stderr',
                     'lag1_M1B_grate', 'lag1_M1B_grate_stderr',
                     'lag1_un_rate', 'lag1_un_rate_stderr',
                     'lag1_ipi_grate', 'lag1_ipi_grate_stderr',
                     'lag1_shtmrg', 'lag1_shtmrg_stderr',
                     'lag1_market_turn', 'lag1_market_turn_stderr',
                     'lag1_new_issue_stock_ratio',
                     'lag1_new_issue_stock_ratio_stderr',
                     'lag1_new_num', 'lag1_new_num_stderr',
                     'std_lag1_volume', 'std_lag1_volume_stderr',
                     'chn_senti', 'chn_senti_stderr',
                     'booking_senti', 'booking_senti_stderr',
                     'cope_senti_score', 'cope_senti_score_stderr',
                     'std_pos_ant', 'std_pos_ant_stderr',
                     'std_neg_ant', 'std_neg_ant_stderr',
                     'std_sum_ant', 'std_sum_ant_stderr',
                     'std_pos_jou', 'std_pos_jou_stderr',
                     'std_neg_jou', 'std_neg_jou_stderr',
                     'std_sum_jou', 'std_sum_jou_stderr',
                     'lag1_chn_senti', 'lag1_chn_senti_stderr',
                     'lag1_booking_senti', 'lag1_booking_senti_stderr',
                     'lag1_cope_senti_score', 'lag1_cope_senti_score_stderr',
                     'lag1_std_pos_ant', 'lag1_std_pos_ant_stderr',
                     'lag1_std_neg_ant', 'lag1_std_neg_ant_stderr',
                     'lag1_std_sum_ant', 'lag1_std_sum_ant_stderr',
                     'lag1_std_pos_jou', 'lag1_std_pos_jou_stderr',
                     'lag1_std_neg_jou', 'lag1_std_neg_jou_stderr',
                     'lag1_std_sum_jou', 'lag1_std_sum_jou_stderr',
                     'Observations', 'AIC', 'BIC', 'R-squared', 'Adj R-squared'])
        return base_vars
