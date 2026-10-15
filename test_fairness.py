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

clf = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf.fit(X_train, y_train)

test_probs = clf.predict_proba(X_test)[:, 1]

# Fairness Analysis on test set
# Group A: Female, Group B: Male
mask_A = (test_df['gender'] == 'Female').values
mask_B = (test_df['gender'] == 'Male').values
y_true = y_test.values

print(f"Group A (Female) count: {np.sum(mask_A)}, Base rate: {np.mean(y_true[mask_A]):.4f}")
print(f"Group B (Male) count: {np.sum(mask_B)}, Base rate: {np.mean(y_true[mask_B]):.4f}")

thresholds = np.arange(0.05, 1.05, 0.10)
records = []

for t in thresholds:
    t_round = round(t, 2)
    y_pred = (test_probs >= t).astype(int)
    
    # Group A
    y_pred_A = y_pred[mask_A]
    y_true_A = y_true[mask_A]
    n_A = len(y_true_A)
    p_hat_A = np.mean(y_pred_A)
    
    # TPR_A, FPR_A
    pos_A = np.sum(y_true_A == 1)
    neg_A = np.sum(y_true_A == 0)
    tpr_A = np.sum((y_pred_A == 1) & (y_true_A == 1)) / pos_A if pos_A > 0 else np.nan
    fpr_A = np.sum((y_pred_A == 1) & (y_true_A == 0)) / neg_A if neg_A > 0 else np.nan
    
    # PPV (Predictive parity component): P(Y=1 | Y_hat=1)
    pred_pos_A = np.sum(y_pred_A == 1)
    ppv_A = np.sum((y_pred_A == 1) & (y_true_A == 1)) / pred_pos_A if pred_pos_A > 0 else np.nan
    
    # Group B
    y_pred_B = y_pred[mask_B]
    y_true_B = y_true[mask_B]
    n_B = len(y_true_B)
    p_hat_B = np.mean(y_pred_B)
    
    pos_B = np.sum(y_true_B == 1)
    neg_B = np.sum(y_true_B == 0)
    tpr_B = np.sum((y_pred_B == 1) & (y_true_B == 1)) / pos_B if pos_B > 0 else np.nan
    fpr_B = np.sum((y_pred_B == 1) & (y_true_B == 0)) / neg_B if neg_B > 0 else np.nan
    
    pred_pos_B = np.sum(y_pred_B == 1)
    ppv_B = np.sum((y_pred_B == 1) & (y_true_B == 1)) / pred_pos_B if pred_pos_B > 0 else np.nan
    
    # Demographic Parity: P(Y_hat=1|A) / P(Y_hat=1|B)
    dp = p_hat_A / p_hat_B if p_hat_B > 0 else np.nan
    
    # Equalized Odds: min(TPR_A/TPR_B, FPR_A/FPR_B)
    # Note: if ratios inverted or > 1, let's see how the formula specifies:
    # prompt: EO: min(TPR_A/TPR_B, FPR_A/FPR_B) - ideal value 1.0
    # Also let's check TPR ratio and FPR ratio separately
    tpr_ratio = tpr_A / tpr_B if (tpr_B is not np.nan and tpr_B > 0) else np.nan
    fpr_ratio = fpr_A / fpr_B if (fpr_B is not np.nan and fpr_B > 0) else np.nan
    eo = min(tpr_ratio, fpr_ratio) if (not np.isnan(tpr_ratio) and not np.isnan(fpr_ratio)) else np.nan
    
    # Predictive Parity: P(Y=1|Y_hat=1, A) / P(Y=1|Y_hat=1, B)
    pp = ppv_A / ppv_B if (ppv_B is not np.nan and ppv_B > 0) else np.nan
    
    acc = np.mean(y_pred == y_true)
    
    records.append({
        'Threshold': t_round,
        'P_hat_Female': p_hat_A,
        'P_hat_Male': p_hat_B,
        'DP': dp,
        'TPR_Female': tpr_A,
        'TPR_Male': tpr_B,
        'FPR_Female': fpr_A,
        'FPR_Male': fpr_B,
        'TPR_Ratio': tpr_ratio,
        'FPR_Ratio': fpr_ratio,
        'EO': eo,
        'PPV_Female': ppv_A,
        'PPV_Male': ppv_B,
        'PP': pp,
        'Accuracy': acc
    })

res_df = pd.DataFrame(records)
print("\n--- FAIRNESS METRICS ACROSS THRESHOLDS (Group A=Female, Group B=Male) ---")
print(res_df[['Threshold', 'DP', 'EO', 'PP', 'Accuracy', 'P_hat_Female', 'P_hat_Male']].to_string(index=False))

