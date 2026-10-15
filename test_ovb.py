import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Load data
columns = [
    'checking_status', 'duration', 'credit_history', 'purpose', 'credit_amount',
    'savings_status', 'employment', 'installment_commitment', 'personal_status_sex',
    'other_parties', 'residence_since', 'property_magnitude', 'age',
    'other_payment_plans', 'housing', 'existing_credits', 'job',
    'num_dependents', 'own_telephone', 'foreign_worker', 'class'
]

df = pd.read_csv('german.data', sep=' ', header=None, names=columns)
df['approval'] = (df['class'] == 1).astype(int)

# Train-test split (70% train, 30% test) with random_state=154
train_df, test_df = train_test_split(df, test_size=0.30, random_state=154)

num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']
cat_cols = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment', 'personal_status_sex', 'other_parties', 'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone', 'foreign_worker']

# Standardize numerical features
scaler = StandardScaler()
X_train_num = pd.DataFrame(scaler.fit_transform(train_df[num_cols]), columns=num_cols, index=train_df.index)
X_train_cat = pd.get_dummies(train_df[cat_cols], drop_first=True)
X_train_full = pd.concat([X_train_num, X_train_cat], axis=1)
y_train = train_df['approval']

# Full model
clf_full = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf_full.fit(X_train_full, y_train)

# Identify checking_status dummy columns
checking_cols = [c for c in X_train_cat.columns if c.startswith('checking_status_')]
print("Checking status dummy cols:", checking_cols)

# Reduced model: drop checking_status
X_train_reduced = X_train_full.drop(columns=checking_cols)
clf_reduced = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf_reduced.fit(X_train_reduced, y_train)

# Compare coefficients of shared predictors
coef_full = pd.Series(clf_full.coef_[0], index=X_train_full.columns)
coef_reduced = pd.Series(clf_reduced.coef_[0], index=X_train_reduced.columns)

common_cols = [c for c in X_train_reduced.columns]
shift_df = pd.DataFrame({
    'Feature': common_cols,
    'Full_Coef': [coef_full[c] for c in common_cols],
    'Reduced_Coef': [coef_reduced[c] for c in common_cols]
})
shift_df['Abs_Change'] = shift_df['Reduced_Coef'] - shift_df['Full_Coef']
shift_df['Pct_Change'] = ((shift_df['Reduced_Coef'] - shift_df['Full_Coef']) / shift_df['Full_Coef'].abs()) * 100
shift_df['Abs_Pct_Change'] = shift_df['Pct_Change'].abs()

print("\nTop 15 shifted features when omitting checking_status:")
print(shift_df.sort_values(by='Abs_Pct_Change', ascending=False)[['Feature', 'Full_Coef', 'Reduced_Coef', 'Abs_Change', 'Pct_Change']].head(15).to_string(index=False))

# Check specifically core predictors: duration, credit_amount, savings_status_A65, credit_history_A34, age, installment_commitment
core = ['duration', 'credit_amount', 'installment_commitment', 'age', 'existing_credits']
print("\nCore numerical predictors shift:")
print(shift_df[shift_df['Feature'].isin(core)][['Feature', 'Full_Coef', 'Reduced_Coef', 'Abs_Change', 'Pct_Change']].to_string(index=False))

