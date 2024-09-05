import numpy as np
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential, Model

def calculate_ml_aic_bic(model, X_train, y_train, y_pred):
    """
    Calculate AIC (Akaike Information Criterion) and BIC (Bayesian Information Criterion)
    for a given machine learning model.

    Parameters
    ----------
    model : object
        A fitted machine learning model with `predict` method.
    X_train : array-like, shape (n_samples, n_features) or (n_samples, timesteps, n_features)
        The training input samples.
    y_train : array-like, shape (n_samples,)
        The true values for X_train.
    y_pred : array-like, shape (n_samples,)
        The predicted values by the model for X_train.

    Returns
    -------
    AIC : float
        The Akaike Information Criterion value.
    BIC : float
        The Bayesian Information Criterion value.
    """

    # Determine the number of parameters based on model type
    if isinstance(model, (RandomForestRegressor, VotingRegressor)):
        num_params = 0
        for estimator in model.estimators_:
            if hasattr(estimator, 'tree_'):
                num_params += estimator.tree_.node_count
            else:
                num_params += X_train.shape[1]  # Use feature count if tree node count is not available
    elif isinstance(model, SVR):
        num_params = X_train.shape[1]  # Use feature count for SVM
    elif isinstance(model, XGBRegressor):
        num_params = model.n_features_in_ * model.n_estimators  # Use number of features and estimators for XGBoost
    elif isinstance(model, (Sequential, Model)):
        # Calculate number of trainable parameters for Keras models, including LSTM
        num_params = np.sum([np.prod(v.get_shape().as_list()) for v in model.trainable_variables])
    else:
        # Default to feature count for other models
        num_params = X_train.shape[1]

    # Calculate the mean squared error of the residuals
    sigma2 = np.mean(np.square(y_train - y_pred))

    # Calculate the likelihood
    L = np.exp(-0.5 * X_train.shape[0] * np.log(2 * np.pi * sigma2) - 
               0.5 * np.sum(np.square(y_train - y_pred)) / sigma2)

    # Calculate AIC
    AIC = 2 * num_params - 2 * np.log(L)

    # Calculate the number of samples
    n = X_train.shape[0]

    # Calculate BIC
    BIC = np.log(n) * num_params - 2 * np.log(L)

    return AIC, BIC
