import os
import joblib
import numpy as np
import pandas as pd
import math
from services.extraction_service import lx_classes
import math

def truncate_float(value, places):
    factor = 10 ** places
    return math.trunc(value * factor) / factor

# 1. Dynamically discover the root path of the code workspace
# This file is inside 'src/services/', so going up two directories hits the 'src/' root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(sub_path):
    """Helper to join paths cleanly across OS platforms"""
    return os.path.join(BASE_DIR, sub_path)

# 2. Load ML Prediction Classifiers with dynamic path resolution
financial_state_model = joblib.load(get_path("models/financial_state_model.pkl"))
income_sufficiency_model = joblib.load(get_path("models/income_sufficiency_model.pkl"))
expenditure_worth_model = joblib.load(get_path("models/expenditure_worth_model.pkl"))
budget_model_cost_of_living = joblib.load(get_path("models/budget_model_cost_of_living.pkl"))
budget_model_other_investments = joblib.load(get_path("models/budget_model_other_investments.pkl"))
budget_model_consumerist_expenditure = joblib.load(get_path("models/budget_model_consumerist_expenditure.pkl"))
budget_model_crisis_shocks = joblib.load(get_path("models/budget_model_crisis_shocks.pkl"))

# 3. Load State 1 Encoders & Scalers
preprocessor_X = joblib.load(get_path("encoders/preprocessor_X.pkl"))
numeric_transformer_X = preprocessor_X.named_transformers_['X_num'].named_steps['X_scaler']
categorical_transformer_X = preprocessor_X.named_transformers_['X_cat'].named_steps['X_onehot']
categorical_transformer_y = joblib.load(get_path("encoders/categorical_transformer_y.pkl"))

# 4. Load State 2 Encoders & Scalers
preprocessor_X2 = joblib.load(get_path("encoders/preprocessor_X2.pkl"))
numeric_transformer_X2 = preprocessor_X2.named_transformers_['X2_num'].named_steps['X2_scaler']
categorical_transformer_X2_debt = preprocessor_X2.named_transformers_['X2_cat_debt'].named_steps['X2_debt_onehot']
categorical_transformer_X2_financial_state = preprocessor_X2.named_transformers_['X2_cat_financial_state'].named_steps['X2_financial_state_onehot']
income_sufficiency_encoder = joblib.load(get_path("encoders/y1_encoder.pkl"))
expenditure_worth_encoder = joblib.load(get_path("encoders/y2_encoder.pkl"))

# 5. Load State 3 Encoders & Scalers
numeric_transformer_X3 = joblib.load(get_path("encoders/preprocessor_X3.pkl")).named_transformers_['X3_num'].named_steps['X3_scaler']

def predict_financial_state(extracted_features):
    cols = lx_classes
    X_test= pd.DataFrame({col: [extracted_features[i]]for i, col in enumerate(cols) })
    X_final=preprocessor_X.transform(X_test)
    y_pred_cat = financial_state_model.predict(X_final)
    financial_state_category = categorical_transformer_y.inverse_transform(y_pred_cat)[0]
    return financial_state_category


def predict_income_sufficiency_and_expenditure_worth(extracted_features, financial_state_category):
    cols = lx_classes + ["Financial State Category"]
    X2_test= pd.DataFrame({col: [float(extracted_features[i])] if (col !="Financial State Category" and col != "Debt Status") else str(financial_state_category) for i, col in enumerate(cols)})
    X2_final=preprocessor_X2.transform(X2_test)
    y_pred1 = income_sufficiency_model.predict(X2_final)
    y_pred2 = expenditure_worth_model.predict(X2_final)
    current_monthly_income_enough = income_sufficiency_encoder.inverse_transform(y_pred1)[0]
    current_expenditure_worth_it = expenditure_worth_encoder.inverse_transform(y_pred2)[0]
    return (current_monthly_income_enough, current_expenditure_worth_it)


def predict_budget_suggestions(extracted_features):
    num_cols = lx_classes[:-1]
    X3_validation_df = pd.DataFrame({col: [float(extracted_features[i])] for i, col in enumerate(num_cols)}, columns=num_cols)
    
    _income = extracted_features[0]
    _total_exp = extracted_features[5]

    # Calculate Feature Ratios safely
    X3_validation_df['Savings_Margin_Ratio'] = ((_income - _total_exp) / _income if _income > 0 else 0.0)
    X3_validation_df['Essential_Cost_Ratio'] = (X3_validation_df['Cost of Living Expenditure (INR)'].iloc[0] / _total_exp if _total_exp > 0 else 0.0)
    X3_validation_df['Current_Investment_Allocation_Rate'] = (X3_validation_df['Other Important Investments (INR)'].iloc[0] / _income if _income > 0 else 0.0)
    X3_validation_df['Current_Crisis_Allocation_Rate'] = (X3_validation_df['Crisis Shock Expenditure (INR)'].iloc[0] / _income if _income > 0 else 0.0)

    # Clean extreme boundaries or infinity values
    X3_validation_df.replace([np.inf, -np.inf], 0.0, inplace=True)
    X3_validation_df.fillna(0.0, inplace=True)

    # Transform numerical attributes safely
    X3_transformed_val = numeric_transformer_X3.transform(X3_validation_df)

    # Calculate dynamic percentages (Cast scalars into standard floats)
    suggested_cost_of_living = float(budget_model_cost_of_living.predict(X3_transformed_val)[0])
    suggested_other_investments = float(budget_model_other_investments.predict(X3_transformed_val)[0])
    suggested_consumerist_expenditure = float(budget_model_consumerist_expenditure.predict(X3_transformed_val)[0])
    suggested_crisis_shocks = float(budget_model_crisis_shocks.predict(X3_transformed_val)[0])

    suggested_cost_of_living_value = suggested_cost_of_living * extracted_features[0]
    suggested_other_investments_value = suggested_other_investments * extracted_features[0]
    suggested_consumerist_expenditure_value = suggested_consumerist_expenditure * extracted_features[0]
    suggested_crisis_shocks_value = suggested_crisis_shocks * extracted_features[0]

    suggested_cost_of_living_value=truncate_float(suggested_cost_of_living_value, 2)
    suggested_other_investments_value=truncate_float(suggested_other_investments_value, 2)
    suggested_consumerist_expenditure_value=truncate_float(suggested_consumerist_expenditure_value, 2)
    suggested_crisis_shocks_value=truncate_float(suggested_crisis_shocks_value, 2)
    
    return (suggested_cost_of_living_value, suggested_other_investments_value, suggested_consumerist_expenditure_value, suggested_crisis_shocks_value)