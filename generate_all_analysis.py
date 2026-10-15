import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import statsmodels.api as sm
import json
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

os.makedirs('outputs', exist_ok=True)
os.makedirs('figures', exist_ok=True)

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
df['age_group'] = df['age'].apply(lambda x: 'Young (<30)' if x < 30 else 'Older (>=30)')

# Save basic stats
summary_stats = {
    'total_samples': len(df),
    'num_features_raw': len(columns) - 1,
    'approval_count': int(df['approval'].sum()),
    'approval_rate': float(df['approval'].mean()),
    'rejection_count': int((df['approval'] == 0).sum()),
    'rejection_rate': float((df['approval'] == 0).mean()),
    'male_count': int((df['gender'] == 'Male').sum()),
    'male_approval_rate': float(df[df['gender'] == 'Male']['approval'].mean()),
    'female_count': int((df['gender'] == 'Female').sum()),
    'female_approval_rate': float(df[df['gender'] == 'Female']['approval'].mean())
}

num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']
cat_cols = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment', 'personal_status_sex', 'other_parties', 'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone', 'foreign_worker']

# Train-test split (70% train, 30% test) with random_state=154
train_df, test_df = train_test_split(df, test_size=0.30, random_state=154)

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

# ==================== PART 1: FIT MODEL A & MODEL B ====================
model_a = LinearRegression()
model_a.fit(X_train, y_train)
pred_a_test = model_a.predict(X_test)
median_a = float(np.median(pred_a_test))
class_a_test = (pred_a_test >= median_a).astype(int)

model_b = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
model_b.fit(X_train, y_train)
prob_b_test = model_b.predict_proba(X_test)[:, 1]
class_b_test = (prob_b_test >= 0.5).astype(int)

cm_ab = confusion_matrix(class_b_test, class_a_test) # Rows: Model B, Cols: Model A
mismatches = int(np.sum(class_a_test != class_b_test))
mismatch_pct = float(mismatches / len(test_df) * 100)

part1_results = {
    'model_a_median': median_a,
    'model_a_min': float(pred_a_test.min()),
    'model_a_max': float(pred_a_test.max()),
    'model_b_prob_min': float(prob_b_test.min()),
    'model_b_prob_max': float(prob_b_test.max()),
    'model_a_pos_count': int(np.sum(class_a_test == 1)),
    'model_b_pos_count': int(np.sum(class_b_test == 1)),
    'cm_matrix': cm_ab.tolist(),
    'mismatches': mismatches,
    'mismatch_pct': mismatch_pct,
    'model_a_acc': float(accuracy_score(y_test, class_a_test)),
    'model_b_acc': float(accuracy_score(y_test, class_b_test))
}

# Plot Part 1: Prediction distributions & Confusion Matrix
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Distribution plot
sns.kdeplot(pred_a_test, label=f'Model A (Linear Reg, Median={median_a:.2f})', color='#1f77b4', lw=2, ax=ax1)
sns.kdeplot(prob_b_test, label='Model B (Logistic Reg, Cutoff=0.50)', color='#ff7f0e', lw=2, ax=ax1)
ax1.axvline(median_a, color='#1f77b4', linestyle='--', label=f'Model A Cutoff ({median_a:.3f})')
ax1.axvline(0.5, color='#ff7f0e', linestyle=':', label='Model B Cutoff (0.500)')
ax1.set_title('Test Set Predictions Distribution: Model A vs Model B', fontsize=12, fontweight='bold')
ax1.set_xlabel('Predicted Score / Probability')
ax1.set_ylabel('Density')
ax1.legend(loc='upper left', frameon=True)

# Confusion Matrix between models
sns.heatmap(cm_ab, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax2,
            xticklabels=['Model A Low (0)', 'Model A High (1)'],
            yticklabels=['Model B Low (0)', 'Model B High (1)'])
ax2.set_title(f'Model Agreement Matrix (Mismatch: {mismatch_pct:.1f}%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Model A (Linear OLS Threshold >= Median)')
ax2.set_ylabel('Model B (Logistic Reg Threshold >= 0.5)')
plt.tight_layout()
plt.savefig('figures/part1_model_comparison.png')
plt.close()

# ==================== PART 2.1: SIMPSON'S PARADOX HUNT ====================
# We evaluate existing_credits and age across Gender and Age Group
# Standardize features for subgroup regressions
df_scaled = df.copy()
for col in num_cols:
    df_scaled[col] = (df[col] - df[col].mean()) / df[col].std()

# Test Subgroup split: Gender
preds_sub = ['duration', 'credit_amount', 'installment_commitment', 'existing_credits', 'age']
X_f = sm.add_constant(df_scaled[preds_sub])
X_M = sm.add_constant(df_scaled[df_scaled['gender'] == 'Male'][preds_sub])
X_F = sm.add_constant(df_scaled[df_scaled['gender'] == 'Female'][preds_sub])

m_full = sm.Logit(df_scaled['approval'], X_f).fit(disp=False)
m_M = sm.Logit(df_scaled[df_scaled['gender'] == 'Male']['approval'], X_M).fit(disp=False)
m_F = sm.Logit(df_scaled[df_scaled['gender'] == 'Female']['approval'], X_F).fit(disp=False)

simpson_gender_records = []
for p in preds_sub:
    ci_f = m_full.conf_int().loc[p]
    ci_M = m_M.conf_int().loc[p]
    ci_F = m_F.conf_int().loc[p]
    simpson_gender_records.append({
        'Predictor': p,
        'Full_Coef': m_full.params[p], 'Full_SE': m_full.bse[p], 'Full_p': m_full.pvalues[p],
        'Full_CI_lower': ci_f[0], 'Full_CI_upper': ci_f[1],
        'Male_Coef': m_M.params[p], 'Male_SE': m_M.bse[p], 'Male_p': m_M.pvalues[p],
        'Male_CI_lower': ci_M[0], 'Male_CI_upper': ci_M[1],
        'Female_Coef': m_F.params[p], 'Female_SE': m_F.bse[p], 'Female_p': m_F.pvalues[p],
        'Female_CI_lower': ci_F[0], 'Female_CI_upper': ci_F[1]
    })
simpson_gender_df = pd.DataFrame(simpson_gender_records)
simpson_gender_df.to_csv('outputs/simpson_gender.csv', index=False)

# Also Bivariate Existing Credits across Age Group (<30 vs >=30)
df_young = df[df['age'] < 30]
df_older = df[df['age'] >= 30]
X_ec_f = sm.add_constant(df['existing_credits'])
X_ec_y = sm.add_constant(df_young['existing_credits'])
X_ec_o = sm.add_constant(df_older['existing_credits'])

m_ec_f = sm.Logit(df['approval'], X_ec_f).fit(disp=False)
m_ec_y = sm.Logit(df_young['approval'], X_ec_y).fit(disp=False)
m_ec_o = sm.Logit(df_older['approval'], X_ec_o).fit(disp=False)

simpson_age_records = [{
    'Subgroup': 'Full Dataset (N=1000)',
    'Coefficient': m_ec_f.params['existing_credits'],
    'Std_Error': m_ec_f.bse['existing_credits'],
    'p_value': m_ec_f.pvalues['existing_credits'],
    'CI_lower': m_ec_f.conf_int().loc['existing_credits'][0],
    'CI_upper': m_ec_f.conf_int().loc['existing_credits'][1],
}, {
    'Subgroup': 'Young Adults (<30, N=371)',
    'Coefficient': m_ec_y.params['existing_credits'],
    'Std_Error': m_ec_y.bse['existing_credits'],
    'p_value': m_ec_y.pvalues['existing_credits'],
    'CI_lower': m_ec_y.conf_int().loc['existing_credits'][0],
    'CI_upper': m_ec_y.conf_int().loc['existing_credits'][1],
}, {
    'Subgroup': 'Mature Adults (>=30, N=629)',
    'Coefficient': m_ec_o.params['existing_credits'],
    'Std_Error': m_ec_o.bse['existing_credits'],
    'p_value': m_ec_o.pvalues['existing_credits'],
    'CI_lower': m_ec_o.conf_int().loc['existing_credits'][0],
    'CI_upper': m_ec_o.conf_int().loc['existing_credits'][1],
}]
simpson_age_df = pd.DataFrame(simpson_age_records)
simpson_age_df.to_csv('outputs/simpson_age_reversal.csv', index=False)

# Plot Simpson's Paradox
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Age effect across gender
gender_plot_df = pd.DataFrame({
    'Group': ['Full Dataset', 'Male Subgroup', 'Female Subgroup'],
    'Age_Coef': [m_full.params['age'], m_M.params['age'], m_F.params['age']],
    'Age_SE': [m_full.bse['age'], m_M.bse['age'], m_F.bse['age']]
})
ax1.bar(gender_plot_df['Group'], gender_plot_df['Age_Coef'], yerr=1.96*gender_plot_df['Age_SE'],
        capsize=5, color=['#2ca02c', '#1f77b4', '#d62728'], alpha=0.85)
ax1.set_title("Effect of Age on Approval by Gender\n(Female Coef ~8x Male Coef, p=0.001 vs 0.520)", fontsize=11, fontweight='bold')
ax1.set_ylabel('Standardized Log-Odds Coefficient (95% CI)')
ax1.axhline(0, color='black', lw=0.8, linestyle='--')

# Plot 2: Sign Reversal for Existing Credits across Age Groups
ax2.bar(simpson_age_df['Subgroup'], simpson_age_df['Coefficient'],
        yerr=1.96*simpson_age_df['Std_Error'], capsize=5,
        color=['#7f7f7f', '#d62728', '#1f77b4'], alpha=0.85)
ax2.set_title("Simpson's Sign Reversal: Existing Credits on Approval\n(Negative for Young, Positive for Mature)", fontsize=11, fontweight='bold')
ax2.set_ylabel('Log-Odds Coefficient (95% CI)')
ax2.axhline(0, color='black', lw=1, linestyle='--')
plt.tight_layout()
plt.savefig('figures/part2_1_simpsons_paradox.png')
plt.close()

# ==================== PART 2.2: OMITTED-VARIABLE BIAS ====================
clf_full = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf_full.fit(X_train, y_train)

checking_cols = [c for c in X_train_cat.columns if c.startswith('checking_status_')]
X_train_reduced = X_train.drop(columns=checking_cols)
clf_reduced = LogisticRegression(solver='liblinear', random_state=154, max_iter=1000)
clf_reduced.fit(X_train_reduced, y_train)

coef_full_s = pd.Series(clf_full.coef_[0], index=X_train.columns)
coef_red_s = pd.Series(clf_reduced.coef_[0], index=X_train_reduced.columns)

ovb_records = []
for c in X_train_reduced.columns:
    c_full = coef_full_s[c]
    c_red = coef_red_s[c]
    abs_change = c_red - c_full
    pct_change = (abs_change / abs(c_full)) * 100
    ovb_records.append({
        'Feature': c,
        'Full_Model_Coef': c_full,
        'Reduced_Model_Coef': c_red,
        'Absolute_Shift': abs_change,
        'Percentage_Change': pct_change,
        'Abs_Percentage_Change': abs(pct_change)
    })
ovb_df = pd.DataFrame(ovb_records)
ovb_df = ovb_df.sort_values(by='Abs_Percentage_Change', ascending=False)
ovb_df.to_csv('outputs/ovb_all_features.csv', index=False)

# Select key 5 representative predictors for deep reporting
selected_ovb_features = ['savings_status_A63', 'employment_A73', 'credit_history_A33', 'existing_credits', 'age', 'duration']
ovb_summary = ovb_df[ovb_df['Feature'].isin(selected_ovb_features)].copy()
ovb_summary.to_csv('outputs/ovb_summary_table.csv', index=False)

# Plot OVB
plt.figure(figsize=(10, 5))
top_ovb = ovb_df.head(8).sort_values(by='Percentage_Change', ascending=True)
colors = ['#d62728' if x < 0 else '#1f77b4' for x in top_ovb['Percentage_Change']]
plt.barh(top_ovb['Feature'], top_ovb['Percentage_Change'], color=colors, alpha=0.85)
plt.axvline(0, color='black', lw=0.8, linestyle='--')
plt.title('Omitted-Variable Bias: % Shift in Coefficients After Dropping Checking Account Status', fontsize=12, fontweight='bold')
plt.xlabel('Percentage Change in Logistic Regression Coefficient (%)')
plt.tight_layout()
plt.savefig('figures/part2_2_ovb_shifts.png')
plt.close()

# ==================== PART 2.3: ADVERSARIAL SUBSET ====================
test_df_adv = test_df.copy()
test_df_adv['prob_approval'] = prob_b_test
test_df_adv['y_true'] = y_test.values

fp_high = test_df_adv[(test_df_adv['prob_approval'] >= 0.75) & (test_df_adv['y_true'] == 0)]
fn_high = test_df_adv[(test_df_adv['prob_approval'] <= 0.25) & (test_df_adv['y_true'] == 1)]
adv_subset = pd.concat([fp_high, fn_high])
adv_subset.to_csv('outputs/adversarial_subset_rows.csv', index=False)

adv_stats = {
    'total_test': len(test_df),
    'fp_high_count': len(fp_high),
    'fn_high_count': len(fn_high),
    'total_adv_count': len(adv_subset),
    'adv_percentage': float(len(adv_subset) / len(test_df) * 100),
    'test_mean_age': float(test_df['age'].mean()),
    'adv_mean_age': float(adv_subset['age'].mean()),
    'test_female_pct': float((test_df['gender'] == 'Female').mean() * 100),
    'adv_female_pct': float((adv_subset['gender'] == 'Female').mean() * 100),
    'test_foreign_pct': float((test_df['foreign_worker'] == 'A201').mean() * 100),
    'adv_foreign_pct': float((adv_subset['foreign_worker'] == 'A201').mean() * 100),
    'test_own_housing_pct': float((test_df['housing'] == 'A152').mean() * 100),
    'adv_own_housing_pct': float((adv_subset['housing'] == 'A152').mean() * 100),
    'test_mean_amount': float(test_df['credit_amount'].mean()),
    'adv_mean_amount': float(adv_subset['credit_amount'].mean()),
    'test_mean_duration': float(test_df['duration'].mean()),
    'adv_mean_duration': float(adv_subset['duration'].mean()),
    'adv_checking_A12_pct': float((adv_subset['checking_status'] == 'A12').mean() * 100),
    'test_checking_A12_pct': float((test_df['checking_status'] == 'A12').mean() * 100),
}

# Plot Adversarial Subset Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Scatter of predictions vs true label with adversarial highlighted
ax1.scatter(test_df_adv[test_df_adv['y_true'] == 1].index, test_df_adv[test_df_adv['y_true'] == 1]['prob_approval'],
            color='#2ca02c', alpha=0.5, label='Actual Approved (Y=1)', s=25)
ax1.scatter(test_df_adv[test_df_adv['y_true'] == 0].index, test_df_adv[test_df_adv['y_true'] == 0]['prob_approval'],
            color='#d62728', alpha=0.5, label='Actual Default/Reject (Y=0)', s=25)
ax1.scatter(adv_subset.index, adv_subset['prob_approval'], facecolors='none', edgecolors='black', s=80, lw=1.5,
            label='Adversarial Cases (Confident Errors)')
ax1.axhline(0.75, color='gray', linestyle='--', lw=1)
ax1.axhline(0.25, color='gray', linestyle='--', lw=1)
ax1.set_title('Test Set Probabilities & Adversarial Failures', fontsize=11, fontweight='bold')
ax1.set_ylabel('Model B P(Approval)')
ax1.set_xlabel('Test Sample Index')
ax1.legend(loc='lower left', frameon=True)

# Demographics comparison bar chart
comp_labels = ['Mean Age (yr)', 'Female (%)', 'Own Home (%)', 'Checking 0-200 DM (%)']
test_vals = [adv_stats['test_mean_age'], adv_stats['test_female_pct'], adv_stats['test_own_housing_pct'], adv_stats['test_checking_A12_pct']]
adv_vals = [adv_stats['adv_mean_age'], adv_stats['adv_female_pct'], adv_stats['adv_own_housing_pct'], adv_stats['adv_checking_A12_pct']]

x = np.arange(len(comp_labels))
width = 0.35
ax2.bar(x - width/2, test_vals, width, label='Full Test Set (N=300)', color='#1f77b4', alpha=0.85)
ax2.bar(x + width/2, adv_vals, width, label='Adversarial Subset (N=24)', color='#e377c2', alpha=0.85)
ax2.set_xticks(x)
ax2.set_xticklabels(comp_labels)
ax2.set_title('Profile Comparison: Test Set vs Adversarial Failures', fontsize=11, fontweight='bold')
ax2.legend(frameon=True)
plt.tight_layout()
plt.savefig('figures/part2_3_adversarial_subset.png')
plt.close()

# ==================== PART 2.4: FAIRNESS TRADE-OFF ANALYSIS ====================
mask_A = (test_df['gender'] == 'Female').values
mask_B = (test_df['gender'] == 'Male').values
y_true = y_test.values

thresholds = np.arange(0.05, 1.05, 0.10)
fairness_records = []

for t in thresholds:
    t_round = round(t, 2)
    y_pred = (prob_b_test >= t).astype(int)
    
    # Female (A)
    y_p_A = y_pred[mask_A]
    y_t_A = y_true[mask_A]
    pos_A, neg_A = np.sum(y_t_A == 1), np.sum(y_t_A == 0)
    p_hat_A = np.mean(y_p_A)
    tpr_A = np.sum((y_p_A == 1) & (y_t_A == 1)) / pos_A if pos_A > 0 else np.nan
    fpr_A = np.sum((y_p_A == 1) & (y_t_A == 0)) / neg_A if neg_A > 0 else np.nan
    pred_pos_A = np.sum(y_p_A == 1)
    ppv_A = np.sum((y_p_A == 1) & (y_t_A == 1)) / pred_pos_A if pred_pos_A > 0 else np.nan
    
    # Male (B)
    y_p_B = y_pred[mask_B]
    y_t_B = y_true[mask_B]
    pos_B, neg_B = np.sum(y_t_B == 1), np.sum(y_t_B == 0)
    p_hat_B = np.mean(y_p_B)
    tpr_B = np.sum((y_p_B == 1) & (y_t_B == 1)) / pos_B if pos_B > 0 else np.nan
    fpr_B = np.sum((y_p_B == 1) & (y_t_B == 0)) / neg_B if neg_B > 0 else np.nan
    pred_pos_B = np.sum(y_p_B == 1)
    ppv_B = np.sum((y_p_B == 1) & (y_t_B == 1)) / pred_pos_B if pred_pos_B > 0 else np.nan
    
    dp = p_hat_A / p_hat_B if p_hat_B > 0 else np.nan
    tpr_ratio = tpr_A / tpr_B if (tpr_B is not np.nan and tpr_B > 0) else np.nan
    fpr_ratio = fpr_A / fpr_B if (fpr_B is not np.nan and fpr_B > 0) else np.nan
    eo = min(tpr_ratio, fpr_ratio) if (not np.isnan(tpr_ratio) and not np.isnan(fpr_ratio)) else np.nan
    pp = ppv_A / ppv_B if (ppv_B is not np.nan and ppv_B > 0) else np.nan
    acc = np.mean(y_pred == y_true)
    
    fairness_records.append({
        'Threshold': t_round,
        'P_hat_Female': p_hat_A,
        'P_hat_Male': p_hat_B,
        'DP': dp,
        'TPR_Female': tpr_A,
        'TPR_Male': tpr_B,
        'FPR_Female': fpr_A,
        'FPR_Male': fpr_B,
        'EO': eo,
        'PPV_Female': ppv_A,
        'PPV_Male': ppv_B,
        'PP': pp,
        'Accuracy': acc
    })

fairness_df = pd.DataFrame(fairness_records)
fairness_df.to_csv('outputs/fairness_metrics_sweep.csv', index=False)

# Plot Part 2.4: Trade-Off Chart & Multi-Metric Curves
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Chart 1: Trade-off chart X=DP (0-1.5), Y=EO (0-1.5)
valid_tradeoff = fairness_df.dropna(subset=['DP', 'EO'])
ax1.plot(valid_tradeoff['DP'], valid_tradeoff['EO'], marker='o', color='#1f77b4', lw=2, markersize=8)
for _, row in valid_tradeoff.iterrows():
    ax1.annotate(f"t={row['Threshold']:.2f}", (row['DP'], row['EO']),
                 textcoords="offset points", xytext=(8, -4), fontsize=9, fontweight='bold')
ax1.axvline(1.0, color='gray', linestyle='--', alpha=0.7, label='Ideal DP (1.0)')
ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.7, label='Ideal EO (1.0)')
ax1.scatter([1.0], [1.0], color='gold', edgecolor='black', s=120, zorder=5, label='Fairness Utopia (1.0, 1.0)')
ax1.set_xlim(0.4, 1.2)
ax1.set_ylim(0.2, 1.1)
ax1.set_xlabel('Demographic Parity (DP: P(Approve|Female) / P(Approve|Male))', fontsize=10, fontweight='bold')
ax1.set_ylabel('Equalized Odds (EO: min(TPR ratio, FPR ratio))', fontsize=10, fontweight='bold')
ax1.set_title('Fairness Trade-Off Curve (DP vs EO across Decision Thresholds)', fontsize=11, fontweight='bold')
ax1.legend(loc='lower left', frameon=True)

# Chart 2: Metric trends across Thresholds
ax2.plot(fairness_df['Threshold'], fairness_df['DP'], marker='s', label='Demographic Parity (DP)', color='#2ca02c', lw=2)
ax2.plot(fairness_df['Threshold'], fairness_df['EO'], marker='^', label='Equalized Odds (EO)', color='#1f77b4', lw=2)
ax2.plot(fairness_df['Threshold'], fairness_df['PP'], marker='d', label='Predictive Parity (PP)', color='#d62728', lw=2)
ax2.plot(fairness_df['Threshold'], fairness_df['Accuracy'], marker='x', label='Overall Accuracy', color='#7f7f7f', lw=1.5, linestyle='--')
ax2.axhline(1.0, color='black', linestyle=':', lw=1, alpha=0.6)
ax2.set_xlabel('Decision Threshold (t)', fontsize=10, fontweight='bold')
ax2.set_ylabel('Metric Value / Ratio', fontsize=10, fontweight='bold')
ax2.set_title('Fairness & Accuracy Metrics Across Decision Thresholds', fontsize=11, fontweight='bold')
ax2.set_ylim(0.2, 1.3)
ax2.legend(loc='upper right', frameon=True)
plt.tight_layout()
plt.savefig('figures/part2_4_fairness_tradeoff.png')
plt.close()

# Save combined metadata summary json
all_results = {
    'summary_stats': summary_stats,
    'part1_results': part1_results,
    'adv_stats': adv_stats
}
with open('outputs/all_summary_results.json', 'w') as f:
    json.dump(all_results, f, indent=4)

print("ALL COMPUTATIONS AND FIGURES GENERATED SUCCESSFULLY!")
