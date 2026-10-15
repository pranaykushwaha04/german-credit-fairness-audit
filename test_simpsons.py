import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

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
df['age_group'] = df['age'].apply(lambda x: '<30' if x < 30 else '>=30')

# Check Simpson's paradox across multiple variables
print("=== SIMPSON'S PARADOX EXPLORATION ===")

# Test simple and multivariable models on full dataset, subgroup A, subgroup B
# Candidate split 1: Gender (Male vs Female)
# Candidate split 2: Age group (<30 vs >=30)
# Candidate split 3: Foreign worker (A201 vs A202)
# Candidate split 4: Housing (Rent A151 vs Own A152)

num_cols = ['duration', 'credit_amount', 'installment_commitment', 'residence_since', 'age', 'existing_credits', 'num_dependents']

for split_var, gA, gB in [('gender', 'Male', 'Female'), ('age_group', '<30', '>=30'), ('housing', 'A152', 'A151')]:
    print(f"\n--- Splitting by {split_var} ({gA} vs {gB}) ---")
    df_A = df[df[split_var] == gA]
    df_B = df[df[split_var] == gB]
    
    # Let's test a key numerical predictor, e.g. installment_commitment or credit_amount or duration, or existing_credits
    for test_pred in ['installment_commitment', 'existing_credits', 'residence_since', 'duration', 'credit_amount', 'age']:
        if test_pred == split_var: continue
        # Fit simple logit: approval ~ predictor
        X_full = sm.add_constant(df[test_pred])
        X_A = sm.add_constant(df_A[test_pred])
        X_B = sm.add_constant(df_B[test_pred])
        
        try:
            m_full = sm.Logit(df['approval'], X_full).fit(disp=False)
            m_A = sm.Logit(df_A['approval'], X_A).fit(disp=False)
            m_B = sm.Logit(df_B['approval'], X_B).fit(disp=False)
            
            c_f, p_f = m_full.params[test_pred], m_full.pvalues[test_pred]
            c_A, p_A = m_A.params[test_pred], m_A.pvalues[test_pred]
            c_B, p_B = m_B.params[test_pred], m_B.pvalues[test_pred]
            
            # Check for sign reversal or big difference
            if (c_A * c_B < 0) or (c_f * c_A < 0) or (c_f * c_B < 0):
                print(f"REVERSAL FOUND for {test_pred} in {split_var}:")
                print(f"  Full: coef={c_f:.4f} (p={p_f:.4f})")
                print(f"  {gA}: coef={c_A:.4f} (p={p_A:.4f})")
                print(f"  {gB}: coef={c_B:.4f} (p={p_B:.4f})")
            elif abs(c_A - c_B) > 0.3:
                print(f"Strong divergence for {test_pred} in {split_var}:")
                print(f"  Full: coef={c_f:.4f} (p={p_f:.4f})")
                print(f"  {gA}: coef={c_A:.4f} (p={p_A:.4f})")
                print(f"  {gB}: coef={c_B:.4f} (p={p_B:.4f})")
        except Exception as e:
            pass

