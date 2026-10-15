import numpy as np
import pandas as pd
import statsmodels.api as sm

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

# Check multivariable model across gender: Male vs Female
# Let's see how predictors behave in Full, Male, Female
features = ['duration', 'credit_amount', 'installment_commitment', 'age', 'existing_credits']
# Scale continuous for comparability
df_scaled = df.copy()
for col in features:
    df_scaled[col] = (df[col] - df[col].mean()) / df[col].std()

for split_name, col_split, val_A, val_B in [
    ('Gender', 'gender', 'Male', 'Female'),
    ('Age Group', 'age_group', 'Young (<30)', 'Older (>=30)'),
    ('Foreign Worker', 'foreign_worker', 'A201', 'A202')
]:
    print(f"\n================ Split: {split_name} ({val_A} vs {val_B}) ================")
    df_A = df_scaled[df_scaled[col_split] == val_A]
    df_B = df_scaled[df_scaled[col_split] == val_B]
    
    # Predictors: duration, credit_amount, installment_commitment, existing_credits, age (if not age_group)
    preds = [c for c in ['duration', 'credit_amount', 'installment_commitment', 'existing_credits', 'age'] if c != col_split and not (split_name == 'Age Group' and c == 'age')]
    
    X_f = sm.add_constant(df_scaled[preds])
    X_A = sm.add_constant(df_A[preds])
    X_B = sm.add_constant(df_B[preds])
    
    m_f = sm.Logit(df_scaled['approval'], X_f).fit(disp=False)
    m_A = sm.Logit(df_A['approval'], X_A).fit(disp=False)
    m_B = sm.Logit(df_B['approval'], X_B).fit(disp=False)
    
    res = []
    for p in preds:
        res.append({
            'Predictor': p,
            'Full_coef': m_f.params[p], 'Full_p': m_f.pvalues[p],
            f'{val_A}_coef': m_A.params[p], f'{val_A}_p': m_A.pvalues[p],
            f'{val_B}_coef': m_B.params[p], f'{val_B}_p': m_B.pvalues[p],
        })
    res_df = pd.DataFrame(res)
    print(res_df.to_string(index=False))

