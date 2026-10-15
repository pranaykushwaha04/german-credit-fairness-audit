import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
import statsmodels.api as sm

# 1. Load data
columns = [
    'checking_status', 'duration', 'credit_history', 'purpose', 'credit_amount',
    'savings_status', 'employment', 'installment_commitment', 'personal_status_sex',
    'other_parties', 'residence_since', 'property_magnitude', 'age',
    'other_payment_plans', 'housing', 'existing_credits', 'job',
    'num_dependents', 'own_telephone', 'foreign_worker', 'class'
]

df = pd.read_csv('german.data', sep=' ', header=None, names=columns)
print(f"Dataset shape: {df.shape}")
print(f"Missing values:\n{df.isnull().sum().sum()}")

# Target encoding: 1=approve (good, original 1), 0=reject (bad, original 2)
df['approval'] = (df['class'] == 1).astype(int)
print("Approval distribution:\n", df['approval'].value_counts(normalize=True))

# Extract gender from personal_status_sex
# A91 : male : divorced/separated
# A92 : female : divorced/separated/married
# A93 : male : single
# A94 : male : married/widowed
# A95 : female : single
df['gender'] = df['personal_status_sex'].apply(lambda x: 'Female' if x in ['A92', 'A95'] else 'Male')
print("Gender distribution:\n", df['gender'].value_counts())

# Numerical and categorical features
num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']
cat_cols = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment', 'personal_status_sex', 'other_parties', 'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone', 'foreign_worker']

# Outlier check on numerical features
for col in ['duration', 'credit_amount', 'age']:
    q25, q75 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q75 - q25
    outliers = df[(df[col] < q25 - 1.5 * iqr) | (df[col] > q75 + 1.5 * iqr)]
    print(f"{col} outliers: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

