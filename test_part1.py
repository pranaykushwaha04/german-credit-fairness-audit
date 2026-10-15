import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
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
df['approval'] = (df['class'] == 1).astype(int)
df['gender'] = df['personal_status_sex'].apply(lambda x: 'Female' if x in ['A92', 'A95'] else 'Male')

# Define numerical and categorical columns
num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']
cat_cols = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment', 'personal_status_sex', 'other_parties', 'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone', 'foreign_worker']

# Train-test split (70% train, 30% test) with random_state=154
train_df, test_df = train_test_split(df, test_size=0.30, random_state=154, stratify=None)
print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
print(f"Train approval rate: {train_df['approval'].mean():.4f}, Test approval rate: {test_df['approval'].mean():.4f}")

# Preprocessing: One-hot encode categorical variables with drop_first=True
# Fit scaler on train numerical features, transform both
scaler = StandardScaler()
X_train_num = pd.DataFrame(scaler.fit_transform(train_df[num_cols]), columns=num_cols, index=train_df.index)
X_test_num = pd.DataFrame(scaler.transform(test_df[num_cols]), columns=num_cols, index=test_df.index)

X_train_cat = pd.get_dummies(train_df[cat_cols], drop_first=True)
X_test_cat = pd.get_dummies(test_df[cat_cols], drop_first=True)

# Align columns
X_train_cat, X_test_cat = X_train_cat.align(X_test_cat, join='left', axis=1, fill_value=0)

X_train = pd.concat([X_train_num, X_train_cat], axis=1)
X_test = pd.concat([X_test_num, X_test_cat], axis=1)
y_train = train_df['approval']
y_test = test_df['approval']

print(f"Number of features: {X_train.shape[1]}")

# PART 1: FIT MODEL A (Linear Regression) and MODEL B (Logistic Regression)
model_a = LinearRegression()
model_a.fit(X_train, y_train)
pred_a_test = model_a.predict(X_test)
median_a = np.median(pred_a_test)

# Model A threshold at median: >= median -> 1, else 0
class_a_test = (pred_a_test >= median_a).astype(int)

# Model B (Logistic Regression)
model_b = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
model_b.fit(X_train, y_train)
prob_b_test = model_b.predict_proba(X_test)[:, 1]

# Model B threshold at 0.5: >= 0.5 -> 1, else 0
class_b_test = (prob_b_test >= 0.5).astype(int)

# Agreement/disagreement
cm_ab = confusion_matrix(class_b_test, class_a_test) # rows: Model B, cols: Model A
mismatches = np.sum(class_a_test != class_b_test)
mismatch_pct = mismatches / len(test_df) * 100

print("\n--- PART 1 RESULTS ---")
print(f"Model A median predicted value: {median_a:.4f}")
print(f"Model A predictions range: [{pred_a_test.min():.4f}, {pred_a_test.max():.4f}]")
print(f"Model B probabilities range: [{prob_b_test.min():.4f}, prob_b_test.max(): {prob_b_test.max():.4f}]")
print(f"Model A positive count: {np.sum(class_a_test == 1)} ({np.mean(class_a_test)*100:.1f}%)")
print(f"Model B positive count: {np.sum(class_b_test == 1)} ({np.mean(class_b_test)*100:.1f}%)")
print(f"Confusion Matrix (Rows: Model B, Cols: Model A):\n{cm_ab}")
print(f"Mismatched cases: {mismatches} / {len(test_df)} ({mismatch_pct:.2f}%)")

acc_a = accuracy_score(y_test, class_a_test)
acc_b = accuracy_score(y_test, class_b_test)
print(f"Model A test accuracy: {acc_a:.4f}, Model B test accuracy: {acc_b:.4f}")

