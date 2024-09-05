def ml_train_test_split(df, response_var, train_size, binary=False):
    """
    Split the DataFrame for machine learning.

    Parameters
    ----------
        df : DataFrame
            The DataFrame to be used for ML,
            containing the response variable and all explanatory variables.
        response_var : str
            The column name in the DataFrame to be used as the response variable.
        train_size : float
            The proportion of data to be used as the training set.
            The value should be between 0 and 1.
        binary : bool, optional
            If True, convert the response variable to binary (1 if greater than 0, else 0).
            Default is False.

    Returns
    -------
        X_train : DataFrame
            Training set features.
        X_test : DataFrame
            Test set features.
        y_train : Series
            Training set response variable.
        y_test : Series
            Test set response variable.
    """

    if binary:
        y = df[response_var].apply(lambda x: 1 if x > 0 else 0)
    else:
        y = df[response_var]
        
    X = df.drop(response_var, axis=1)
    split_index = int(len(X) * train_size)
    
    X_train = X.iloc[:split_index]
    X_test  = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test  = y.iloc[split_index:]
    
    return X_train, X_test, y_train, y_test
