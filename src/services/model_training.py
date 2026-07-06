import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestRegressor
import joblib

DATA_PATH = "src/data/indian_finance_ml_dataset_balanced_final.csv"

df = pd.read_csv(DATA_PATH)

classes_X1 = ['Monthly Income (INR)', 'Cost of Living Expenditure (INR)',
               'Other Important Investments (INR)', 'Consumerist Expenditure (INR)',
               'Crisis Shock Expenditure (INR)', 'Total Monthly Expenditure (INR)',
               'Debt Status']
X = df[classes_X1].copy()
y = df['Financial State Category']

numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
categorical_features = ['Debt Status']

numeric_transformer_X = Pipeline(steps=[
    ('X_imputer', SimpleImputer(strategy='median')),
    ('X_scaler', StandardScaler())
])
categorical_transformer_X = Pipeline(steps=[
    ('X_onehot', OneHotEncoder(handle_unknown='ignore'))
])
categorical_transformer_y = LabelEncoder()

preprocessor_X = ColumnTransformer(
    transformers=[
        ("X_num", numeric_transformer_X, numeric_features),
        ("X_cat", categorical_transformer_X, categorical_features),
    ]
)

preprocessor_X.fit(X)
X_transformed = preprocessor_X.transform(X)
y_transformed = categorical_transformer_y.fit_transform(y.values.reshape(-1, 1))

joblib.dump(preprocessor_X, "src/encoders/preprocessor_X.pkl")
print("X preprocessor saved to 'src/encoders/preprocessor_X.pkl'.")
joblib.dump(categorical_transformer_y, "src/encoders/categorical_transformer_y.pkl")
print("y encoder saved to 'src/encoders/categorical_transformer_y.pkl'.")

X_train, X_test, y_train, y_test = train_test_split(X_transformed, y_transformed, test_size=0.2, random_state=42)
model = SVC(kernel='linear', C=1.0, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

print("Model (Financial State Category) training completed.")

X2 = df[['Monthly Income (INR)', 'Cost of Living Expenditure (INR)', 'Other Important Investments (INR)',
          'Consumerist Expenditure (INR)', 'Crisis Shock Expenditure (INR)',
          'Total Monthly Expenditure (INR)', 'Debt Status', 'Financial State Category']].copy()
y1 = df['Current Monthly Income Enough for Next Few Months']
y2 = df['Current Expenditure Worth It']

# Force these columns to be read as text strings, cleaning up pandas types
X2['Debt Status'] = X2['Debt Status'].astype(str)
X2['Financial State Category'] = X2['Financial State Category'].astype(str) # Assuming this is the name on line 26


numeric_features_X2 = X2.select_dtypes(include=['int64', 'float64']).columns
numeric_transformer_X2 = Pipeline(steps=[
    ('X2_imputer', SimpleImputer(strategy='median')),
    ('X2_scaler', StandardScaler())
])
categorical_transformer_X2_debt = Pipeline(steps=[
    ('X2_debt_onehot', OneHotEncoder(handle_unknown='ignore'))
])
categorical_transformer_X2_financial_state = Pipeline(steps=[
    ('X2_financial_state_onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor_X2 = ColumnTransformer(
    transformers=[
        ("X2_num", numeric_transformer_X2, numeric_features_X2),
        ("X2_cat_debt", categorical_transformer_X2_debt, ['Debt Status']),
        ("X2_cat_financial_state", categorical_transformer_X2_financial_state, ['Financial State Category']),
    ]
)

preprocessor_X2.fit(X2)
X2_transformed = preprocessor_X2.transform(X2)

le1 = LabelEncoder()
le2 = LabelEncoder()

y1_transformed = le1.fit_transform(y1)
y2_transformed = le2.fit_transform(y2)

joblib.dump(preprocessor_X2, "src/encoders/preprocessor_X2.pkl")
print("X2 preprocessor saved to 'src/encoders/preprocessor_X2.pkl'.")
joblib.dump(le1, "src/encoders/y1_encoder.pkl")
print("y1 encoder saved to 'src/encoders/y1_encoder.pkl'.")
joblib.dump(le2, "src/encoders/y2_encoder.pkl")
print("y2 encoder saved to 'src/encoders/y2_encoder.pkl'.")

X_train1, X_test1, y_train1, y_test1 = train_test_split(X2_transformed, y1_transformed, test_size=0.2, random_state=42)
X_train2, X_test2, y_train2, y_test2 = train_test_split(X2_transformed, y2_transformed, test_size=0.2, random_state=42)
model1 = SVC(kernel='linear', C=1.0, random_state=42, class_weight='balanced')
model2 = SVC(kernel='linear', C=1.0, random_state=42, class_weight='balanced')
model1.fit(X_train1, y_train1)
model2.fit(X_train2, y_train2)
print("Model 1 (Current Monthly Income Enough) and Model 2 (Current Expenditure Worth It) training completed.")

df_rf = pd.read_csv(DATA_PATH)
df_rf['Savings_Margin_Ratio'] = (df_rf['Monthly Income (INR)'] - df_rf['Total Monthly Expenditure (INR)']) / df_rf['Monthly Income (INR)']
df_rf['Essential_Cost_Ratio'] = df_rf['Cost of Living Expenditure (INR)'] / df_rf['Total Monthly Expenditure (INR)']
df_rf['Current_Investment_Allocation_Rate'] = df_rf['Other Important Investments (INR)'] / df_rf['Monthly Income (INR)']
df_rf['Current_Crisis_Allocation_Rate'] = df_rf['Crisis Shock Expenditure (INR)'] / df_rf['Monthly Income (INR)']

feature_names = [
    'Monthly Income (INR)', 'Cost of Living Expenditure (INR)', 'Other Important Investments (INR)',
    'Consumerist Expenditure (INR)', 'Crisis Shock Expenditure (INR)', 'Total Monthly Expenditure (INR)',
    'Savings_Margin_Ratio', 'Essential_Cost_Ratio', 'Current_Investment_Allocation_Rate', 'Current_Crisis_Allocation_Rate'
]

X3 = df_rf[feature_names]
y3 = df_rf['Suggested Budget - Cost of Living']
y4 = df_rf['Suggested Budget - Other Important Investments']
y5 = df_rf['Suggested Budget - Consumerist Expenditure']
y6 = df_rf['Suggested Budget - Crisis Shocks']

numeric_transformer_X3 = Pipeline(steps=[
    ('X3_scaler', StandardScaler())
])

preprocessor_X3 = ColumnTransformer(
    transformers=[
        ("X3_num", numeric_transformer_X3, feature_names)
    ]
)

preprocessor_X3.fit(X3)
X3_transformed = preprocessor_X3.transform(X3)

X_train3, X_test3, y_train3, y_test3 = train_test_split(X3_transformed, y3, test_size=0.2, random_state=42)
X_train4, X_test4, y_train4, y_test4 = train_test_split(X3_transformed, y4, test_size=0.2, random_state=42)
X_train5, X_test5, y_train5, y_test5 = train_test_split(X3_transformed, y5, test_size=0.2, random_state=42)
X_train6, X_test6, y_train6, y_test6 = train_test_split(X3_transformed, y6, test_size=0.2, random_state=42)

model3 = RandomForestRegressor(n_estimators=100, random_state=42)
model4 = RandomForestRegressor(n_estimators=100, random_state=42)
model5 = RandomForestRegressor(n_estimators=100, random_state=42)
model6 = RandomForestRegressor(n_estimators=100, random_state=42)
model3.fit(X_train3, y_train3)
model4.fit(X_train4, y_train4)
model5.fit(X_train5, y_train5)
model6.fit(X_train6, y_train6)

print("Models 3-6 (Budget Suggestions) training completed.")

joblib.dump(preprocessor_X3, "src/encoders/preprocessor_X3.pkl")
joblib.dump(model, "src/models/financial_state_model.pkl")
joblib.dump(model1, "src/models/income_sufficiency_model.pkl")
joblib.dump(model2, "src/models/expenditure_worth_model.pkl")
joblib.dump(model3, "src/models/budget_model_cost_of_living.pkl")
joblib.dump(model4, "src/models/budget_model_other_investments.pkl")
joblib.dump(model5, "src/models/budget_model_consumerist_expenditure.pkl")
joblib.dump(model6, "src/models/budget_model_crisis_shocks.pkl")

print("All models have been saved to the 'src/models/' directory.")
