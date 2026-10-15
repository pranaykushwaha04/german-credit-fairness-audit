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
df['gender'] = df['personal_status_sex'].apply(lambda x: 'Female' if x in ['A92', 'A95'] else 'Male')

# Train-test split
train_df, test_df = train_test_split(df, test_size=0.30, random_state=154)

num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']
cat_cols = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment', 'personal_status_sex', 'other_parties', 'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone', 'foreign_worker']

scaler = StandardScaler()
X_train_num = pd.DataFrame(scaler.fit_transform(train_df[num_cols]), columns=num_cols, index=train_df.index)
X_test_num = pd.DataFrame(scaler.transform(test_df[num_cols]), columns=num_cols, index=test_df.index)

X_train_cat = pd.get_dummies(train_df[cat_cols], drop_first=True)
X_test_cat = pd.get_dummies(test_df[cat_cols], drop_first=True)
X_train_cat, X_test_cat = X_train_cat.align(X_test_cat, join='left', axis=1, fill_value=0)

X_train = pd.concat([X_train_num, X_train_cat], axis=1)
X_test = pd.concat([X_test_num, X_test_cat], axis=1)
y_train = train_df['approval']
y_test = test_df['approval']

# Fit Model B
clf = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf.fit(X_train, y_train)

test_probs = clf.predict_proba(X_test)[:, 1]
test_res = test_df.copy()
test_res['prob_approval'] = test_probs
test_res['y_true'] = y_test

# Confident wrong:
# P >= 0.75 and y_true == 0 (False Positive with high confidence)
# P <= 0.25 and y_true == 1 (False Negative with high confidence)
fp_high = test_res[(test_res['prob_approval'] >= 0.75) & (test_res['y_true'] == 0)]
fn_high = test_res[(test_res['prob_approval'] <= 0.25) & (test_res['y_true'] == 1)]
adv_all = pd.concat([fp_high, fn_high])

print(f"Test set total: {len(test_res)}")
print(f"High-confidence false positives (P >= 0.75, y=0): {len(fp_high)}")
print(f"High-confidence false negatives (P <= 0.25, y=1): {len(fn_high)}")
print(f"Total adversarial instances: {len(adv_all)} ({len(adv_all)/len(test_res)*100:.2f}%)")

print("\nDemographics Comparison:")
print("Age Mean - Full Test:", test_res['age'].mean(), "Adversarial:", adv_all['age'].mean())
print("Gender % Female - Full Test:", (test_res['gender']=='Female').mean()*100, "Adversarial:", (adv_all['gender']=='Female').mean()*100)
print("Foreign Worker % - Full Test:", (test_res['foreign_worker']=='A201').mean()*100, "Adversarial:", (adv_all['foreign_worker']=='A201').mean()*100)
print("Checking Status distribution in Full Test:\n", test_res['checking_status'].value_counts(normalize=True)*100)
print("Checking Status distribution in Adversarial:\n", adv_all['checking_status'].value_counts(normalize=True)*100)
print("Credit History distribution in Full Test:\n", test_res['credit_history'].value_counts(normalize=True)*100)
print("Credit History distribution in Adversarial:\n", adv_all['credit_history'].value_counts(normalize=True)*100)
print("Housing distribution in Full Test:\n", test_res['housing'].value_counts(normalize=True)*100)
print("Housing distribution in Adversarial:\n", adv_all['housing'].value_counts(normalize=True)*100)
print("Mean Credit Amount - Full Test:", test_res['credit_amount'].mean(), "Adversarial:", adv_all['credit_amount'].mean())
print("Mean Duration - Full Test:", test_res['duration'].mean(), "Adversarial:", adv_all['duration'].mean())

