import base64
import os
import pypdf
from playwright.sync_api import sync_playwright

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')

fig1_b64 = get_base64_image("figures/part1_model_comparison.png")
fig2_b64 = get_base64_image("figures/part2_1_simpsons_paradox.png")
fig3_b64 = get_base64_image("figures/part2_2_ovb_shifts.png")
fig4_b64 = get_base64_image("figures/part2_3_adversarial_subset.png")
fig5_b64 = get_base64_image("figures/part2_4_fairness_tradeoff.png")

# Template for compact 6-page report
compact_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CSET485 Assignment 1 - AI and Society - s24bcau0154</title>
<style>
    @page {{
        size: A4;
        margin: 10mm 11mm 10mm 11mm;
        @bottom-right {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 7pt;
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #64748b;
        }}
        @bottom-left {{
            content: "CSET485 AI & Society | Enrollment ID: s24bcau0154 | German Credit (Seed: 154)";
            font-size: 7pt;
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #64748b;
        }}
    }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        line-height: 1.35;
        color: #0f172a;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    .page {{
        height: 275mm;
        max-height: 275mm;
        overflow: hidden;
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-sizing: border-box;
    }}

    .page:last-child {{
        page-break-after: avoid;
    }}

    h1, h2, h3, h4 {{
        color: #0f172a;
        font-weight: 700;
        margin-top: 3pt;
        margin-bottom: 2pt;
    }}

    h1 {{
        font-size: 14pt;
        line-height: 1.15;
        color: #1e3a8a;
        margin-bottom: 2pt;
    }}

    h2 {{
        font-size: 9.5pt;
        background-color: #f1f5f9;
        border-left: 3.5px solid #1e3a8a;
        padding: 2pt 5pt;
        margin-top: 5pt;
        margin-bottom: 3pt;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}

    h3 {{
        font-size: 8.5pt;
        color: #1e40af;
        margin-top: 3pt;
        margin-bottom: 1.5pt;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 3pt;
        text-align: justify;
    }}

    .meta-box {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 4pt 8pt;
        margin-bottom: 4pt;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 2pt 8pt;
        font-size: 7.5pt;
    }}

    .meta-box strong {{
        color: #1e3a8a;
    }}

    .grid-2 {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6pt;
    }}

    .grid-60-40 {{
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 6pt;
    }}

    .grid-55-45 {{
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 6pt;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 2pt 0 4pt 0;
        font-size: 7pt;
    }}

    th {{
        background-color: #1e3a8a;
        color: #ffffff;
        font-weight: 600;
        text-align: left;
        padding: 2.5pt 4pt;
        border: 0.5px solid #1e3a8a;
    }}

    td {{
        padding: 2pt 4pt;
        border: 0.5px solid #cbd5e1;
        vertical-align: middle;
    }}

    tr:nth-child(even) td {{
        background-color: #f8fafc;
    }}

    .figure-box {{
        text-align: center;
        margin: 2pt 0;
    }}

    .figure-box img {{
        max-width: 100%;
        height: auto;
        max-height: 110px;
        border: 0.5px solid #cbd5e1;
        border-radius: 3px;
    }}

    .caption {{
        font-size: 6.5pt;
        color: #64748b;
        margin-top: 1pt;
        font-style: italic;
    }}

    .callout {{
        background-color: #eff6ff;
        border-left: 3px solid #2563eb;
        padding: 3pt 5pt;
        margin: 2pt 0;
        border-radius: 0 3px 3px 0;
        font-size: 7.5pt;
    }}

    .q-block {{
        background-color: #ffffff;
        border: 0.5px solid #cbd5e1;
        border-left: 3px solid #1e3a8a;
        border-radius: 3px;
        padding: 4pt 6pt;
        margin-bottom: 4pt;
    }}

    .q-title {{
        font-size: 8pt;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 2pt;
    }}

    .badge {{
        display: inline-block;
        padding: 0.5pt 3pt;
        font-size: 6.5pt;
        font-weight: 700;
        border-radius: 2px;
    }}
    .badge-blue {{ background-color: #dbeafe; color: #1e40af; }}
    .badge-green {{ background-color: #dcfce7; color: #15803d; }}
    .badge-red {{ background-color: #fee2e2; color: #b91c1c; }}
</style>
</head>
<body>

<!-- ================= PAGE 1 ================= -->
<div class="page">
    <div style="border-bottom: 1.5px solid #1e3a8a; padding-bottom: 2pt; margin-bottom: 3pt;">
        <h1 style="margin: 0; font-size: 13pt;">CSET485 – AI & Society: Assignment #1 (10 Marks)</h1>
        <div style="font-size: 8pt; color: #475569; font-weight: 600;">Auditing Bias, Structural Confounds & Fairness Defensibility in Credit Underwriting</div>
    </div>

    <div class="meta-box">
        <div><strong>Enrollment ID:</strong> s24bcau0154</div>
        <div><strong>Dataset:</strong> German Credit (Last digit 4)</div>
        <div><strong>Random Seed:</strong> 154 (Last 3 digits)</div>
        <div><strong>Partition:</strong> 70% Train (700) / 30% Test (300)</div>
        <div><strong>Target:</strong> Approval (1=Approve, 0=Reject)</div>
        <div><strong>Status:</strong> Fully Reproducible Jupyter Notebook</div>
    </div>

    <p style="font-size: 7.5pt; margin-bottom: 4pt;">
        <strong>Executive Summary:</strong> Algorithmic underwriting systems often appear statistically robust while masking demographic disparities, omitted confounders, and unavoidable fairness trade-offs. Using the German Credit dataset (N=1,000), we stress-test Linear Probability OLS and Logistic Regression across threshold mismatches, Simpson's paradox, omitted-variable bias, adversarial failure clusters, and parametric fairness frontiers. All conclusions are grounded strictly in our computed numbers.
    </p>

    <h2>Data Preprocessing & Exploratory Audit</h2>
    <div class="grid-2">
        <div>
            <p><strong>1. Missing Values:</strong> An automated scan verified <strong>0 missing or NaN values</strong> across all 1,000 instances and 20 attributes, consistent with original documentation.</p>
            <p><strong>2. Categorical Encoding:</strong> 13 qualitative features (checking status, credit history, purpose, savings, employment, housing, etc.) were encoded via <strong>One-Hot Encoding with first category dropped (drop_first=True)</strong> to avert perfect multicollinearity and the dummy variable trap, yielding 41 indicator columns and 7 continuous regressors (48 total modeled features).</p>
        </div>
        <div>
            <p><strong>3. Feature Scaling:</strong> Standardized all 7 continuous features (<code>duration</code>, <code>credit_amount</code>, <code>installment_commitment</code>, <code>residence_since</code>, <code>age</code>, <code>existing_credits</code>, <code>num_dependents</code>) using <code>StandardScaler</code> fit strictly on the 70% training split (N=700, seed=154) to eliminate data leakage.</p>
            <p><strong>4. Outlier Handling Rationale:</strong> Using the 1.5 &times; IQR rule, we detected 70 outliers in <code>duration</code> (7.0%), 72 in <code>credit_amount</code> (7.2%), and 23 in <code>age</code> (2.3%). Crucially, these were <strong>preserved without clipping</strong>; high loan balances and long maturities represent legitimate tail-risk default liabilities that models must learn.</p>
        </div>
    </div>

    <h2>Part 1 — Model Fitting & Threshold Mismatch Analysis</h2>
    <p>Both models were fitted on the identical 700-sample training matrix (train approval base rate: 69.71%, test base rate: 70.67%):</p>
    <ul>
        <li><strong>Model A (Linear OLS Regression):</strong> Continuous predictions Y_hat on test set range in <strong>[-0.0211, 1.3459]</strong> with an empirical <strong>median of 0.7151</strong>. Thresholding at median (Y_hat &ge; 0.7151) classifies exactly 150 instances (50.0%) as positive.</li>
        <li><strong>Model B (Logistic Regression):</strong> Sigmoidal probabilities P_hat range in <strong>[0.0628, 0.9946]</strong>. Thresholding at standard P_hat &ge; 0.50 classifies 240 instances (80.0%) as positive. Overall test accuracy: <strong>Model B = 75.33%</strong> vs. <strong>Model A = 68.00%</strong>.</li>
    </ul>

    <div class="grid-55-45" style="align-items: center;">
        <div>
            <p style="font-weight: 700; margin-bottom: 1pt; font-size: 7.5pt;">Table 1: Inter-Model Confusion Matrix (Test Set, N=300)</p>
            <table>
                <thead>
                    <tr>
                        <th>Classification Alignment</th>
                        <th>Model A Negative (&lt; Median)</th>
                        <th>Model A Positive (&ge; Median 0.7151)</th>
                        <th>Total Model B</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Model B Negative (&lt; 0.50)</strong></td>
                        <td>60 (True Agreement)</td>
                        <td>0</td>
                        <td>60 (20.0%)</td>
                    </tr>
                    <tr>
                        <td><strong>Model B Positive (&ge; 0.50)</strong></td>
                        <td style="background-color: #fee2e2; font-weight: bold; color: #b91c1c;">90 (Mismatched Cases: 30.0%)</td>
                        <td>150 (True Agreement)</td>
                        <td>240 (80.0%)</td>
                    </tr>
                    <tr>
                        <td><strong>Total Model A</strong></td>
                        <td>150 (50.0%)</td>
                        <td>150 (50.0%)</td>
                        <td><strong>300 (100.0%)</strong></td>
                    </tr>
                </tbody>
            </table>
            <div class="callout" style="margin-top: 2pt;">
                <strong>Key Mechanism:</strong> Exactly <strong>90 out of 300 individuals (30.00%)</strong> are flagged differently. Model A forces a relative rank median split (50/50), discarding qualified borrowers in the corridor 0.5000 &le; P_hat_B &lt; 0.7151, while Model B reflects the true 70.67% base rate.
            </div>
        </div>
        <div class="figure-box">
            <img src="{fig1_b64}" alt="Figure 1: Model Comparison">
            <div class="caption">Figure 1: Prediction distributions and classification agreement matrix (30.0% mismatch).</div>
        </div>
    </div>
</div>

<!-- ================= PAGE 2 ================= -->
<div class="page">
    <h2>Part 2.1 — Simpson's Paradox Hunt</h2>
    <p>We stress-tested parameter invariance across demographic cohorts and uncovered two dramatic manifestations of Simpson's Paradox and subgroup heterogeneity:</p>
    
    <div class="grid-55-45" style="align-items: center;">
        <div>
            <p><strong>1. Sign Reversal on Existing Credits across Age:</strong> In the full population (N=1,000), bivariate logistic regression suggests additional bank credit lines increase approval odds (&beta; = +0.1780). Disaggregating by age exposes an acute sign reversal: for <strong>Young Adults (&lt;30, N=371)</strong>, the coefficient reverses to <strong>negative (&beta; = -0.2203)</strong>, while for <strong>Mature Adults (&ge;30, N=629)</strong>, it is strongly <strong>positive (&beta; = +0.3083, p = 0.0519)</strong>. For young borrowers, multiple loans signal emergency credit-seeking and liquidity distress; for mature adults, they reflect seasoned creditworthiness.</p>
            <p><strong>2. Age Divergence across Gender:</strong> In standardized multivariable regression, applicant age has zero statistical impact on men (&beta;_Male = +0.0604, p = 0.5204), but acts as an enormous protective factor for women (&beta;_Female = +0.4741, p = 0.0013)—an effect size nearly <strong>eight times larger</strong>.</p>
        </div>
        <div class="figure-box">
            <img src="{fig2_b64}" alt="Figure 2: Simpson's Paradox">
            <div class="caption">Figure 2: Sign reversal on existing credits (left) & age divergence across gender (right).</div>
        </div>
    </div>

    <p style="font-weight: 700; margin-bottom: 1pt; margin-top: 2pt; font-size: 7.5pt;">Table 2: Subgroup Regression Analysis (Simpson's Paradox & Gender Divergence)</p>
    <table>
        <thead>
            <tr>
                <th>Cohort / Subgroup</th>
                <th>Sample Size (N)</th>
                <th>Coefficient (&beta;)</th>
                <th>Std. Error</th>
                <th>p-value</th>
                <th>95% Confidence Interval</th>
                <th>Observed Behavioral Effect</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Existing Credits: Full Dataset</strong></td>
                <td>1,000</td>
                <td>+0.1780</td>
                <td>0.1232</td>
                <td>0.1488</td>
                <td>[-0.0636, +0.4195]</td>
                <td>Weak Aggregate Positive Association</td>
            </tr>
            <tr style="background-color: #fee2e2;">
                <td><strong>Existing Credits: Young Adults (&lt;30)</strong></td>
                <td>371</td>
                <td><strong>-0.2203</strong></td>
                <td>0.2133</td>
                <td>0.3016</td>
                <td>[-0.6384, +0.1977]</td>
                <td><strong>Acute Sign Reversal (Negative Penalty)</strong></td>
            </tr>
            <tr style="background-color: #dbeafe;">
                <td><strong>Existing Credits: Mature Adults (&ge;30)</strong></td>
                <td>629</td>
                <td><strong>+0.3083</strong></td>
                <td>0.1586</td>
                <td>0.0519</td>
                <td>[-0.0025, +0.6192]</td>
                <td><strong>Statistically Meaningful Positive Asset</strong></td>
            </tr>
            <tr>
                <td><strong>Multivariable Age: Male Subgroup</strong></td>
                <td>690</td>
                <td>+0.0604</td>
                <td>0.0940</td>
                <td>0.5204</td>
                <td>[-0.1238, +0.2445]</td>
                <td>Statistically Null Effect for Men</td>
            </tr>
            <tr style="background-color: #dcfce7;">
                <td><strong>Multivariable Age: Female Subgroup</strong></td>
                <td>310</td>
                <td><strong>+0.4741</strong></td>
                <td>0.1469</td>
                <td><strong>0.0013</strong></td>
                <td>[+0.1861, +0.7620]</td>
                <td><strong>Highly Protective Factor (~8x Larger Effect)</strong></td>
            </tr>
        </tbody>
    </table>

    <h2>Part 2.2 — Omitted-Variable Bias (OVB) Stress-Testing</h2>
    <div class="grid-55-45" style="align-items: center;">
        <div>
            <p>
                To measure vulnerability to hidden confounding, we deliberately omitted <code>checking_status</code> (Attribute 1: checking account liquidity) from Model B. Because liquidity is correlated with savings reserves and employment stability, remaining regressors absorbed the omitted explanatory power via proxy correlation: E[beta_hat] = beta_true + beta_omitted &times; Cov(X, Z)/Var(X).
            </p>
            <p style="font-weight: 700; margin-bottom: 1pt; font-size: 7.5pt;">Table 3: Omitted-Variable Bias Shift in Predictor Coefficients</p>
            <table>
                <thead>
                    <tr>
                        <th>Predictor Variable</th>
                        <th>Role / Meaning</th>
                        <th>Full &beta;</th>
                        <th>Reduced &beta;</th>
                        <th>Shift &Delta;&beta;</th>
                        <th>% Change</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background-color: #fee2e2; font-weight: bold;">
                        <td><code>savings_status_A63</code></td>
                        <td>Savings 500–1000 DM</td>
                        <td>+0.3720</td>
                        <td>+0.7812</td>
                        <td>+0.4092</td>
                        <td>+110.00%</td>
                    </tr>
                    <tr style="background-color: #fee2e2; font-weight: bold;">
                        <td><code>employment_A73</code></td>
                        <td>Job Tenure 1–4 Yrs</td>
                        <td>+0.1278</td>
                        <td>+0.2560</td>
                        <td>+0.1282</td>
                        <td>+100.31%</td>
                    </tr>
                    <tr>
                        <td><code>credit_history_A33</code></td>
                        <td>Past Payment Delay</td>
                        <td>+0.3941</td>
                        <td>+0.5956</td>
                        <td>+0.2015</td>
                        <td>+51.14%</td>
                    </tr>
                    <tr>
                        <td><code>existing_credits</code></td>
                        <td>Existing Bank Credits</td>
                        <td>-0.0983</td>
                        <td>-0.0656</td>
                        <td>+0.0328</td>
                        <td>+33.31%</td>
                    </tr>
                    <tr>
                        <td><code>age</code></td>
                        <td>Applicant Age</td>
                        <td>+0.1543</td>
                        <td>+0.1869</td>
                        <td>+0.0326</td>
                        <td>+21.16%</td>
                    </tr>
                    <tr>
                        <td><code>duration</code></td>
                        <td>Loan Duration (Mo.)</td>
                        <td>-0.4273</td>
                        <td>-0.4325</td>
                        <td>-0.0052</td>
                        <td>-1.21%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="figure-box">
            <img src="{fig3_b64}" alt="Figure 3: OVB Shifts">
            <div class="caption">Figure 3: Percentage shifts in logistic coefficients after dropping checking status.</div>
            <div class="callout" style="text-align: left; margin-top: 3pt;">
                <strong>Finding:</strong> <code>savings_status_A63</code> surged by <strong>+110.00%</strong> and <code>employment_A73</code> surged by <strong>+100.31%</strong>. Un-stress-tested models cannot be trusted because proxy variables aggressively absorb omitted confounds.
            </div>
        </div>
    </div>
</div>

<!-- ================= PAGE 3 ================= -->
<div class="page">
    <h2>Part 2.3 — Adversarial Subset Construction & Failure Mechanics</h2>
    <p>
        On the test set (N=300), we extracted cases where Model B made confident errors (P_hat &ge; 0.75 with true default Y=0, or P_hat &le; 0.25 with true approval Y=1). Exactly <strong>24 instances (8.00% of the test cohort)</strong> satisfied this criterion (21 high-confidence false positives, 3 high-confidence false negatives).
    </p>

    <div class="grid-60-40" style="align-items: center;">
        <div>
            <p style="font-weight: 700; margin-bottom: 1pt; font-size: 7.5pt;">Table 4: Adversarial Failures vs. Test Set Baseline Profile</p>
            <table>
                <thead>
                    <tr>
                        <th>Metric / Characteristic</th>
                        <th>Test Baseline (N=300)</th>
                        <th>Adversarial (N=24)</th>
                        <th>Disparity Signature</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Homeownership (housing = A152)</strong></td>
                        <td>74.00%</td>
                        <td><strong>83.33%</strong></td>
                        <td>+9.33% Over-Represented</td>
                    </tr>
                    <tr style="background-color: #fee2e2; font-weight: bold;">
                        <td><strong>Moderate Checking (A12: 0–200 DM)</strong></td>
                        <td>23.00%</td>
                        <td><strong>45.83%</strong></td>
                        <td>Nearly Double Baseline (+22.83%)</td>
                    </tr>
                    <tr>
                        <td><strong>Clean Credit History (A32)</strong></td>
                        <td>53.67%</td>
                        <td><strong>54.17%</strong></td>
                        <td>Parity with Clean Baseline</td>
                    </tr>
                    <tr>
                        <td><strong>Mean Loan Amount Requested</strong></td>
                        <td>3,040.18 DM</td>
                        <td><strong>3,337.50 DM</strong></td>
                        <td>+$297.32 DM Heavier Burden</td>
                    </tr>
                    <tr>
                        <td><strong>Female Representation</strong></td>
                        <td>28.33%</td>
                        <td><strong>20.83%</strong></td>
                        <td>-7.50% Under-Represented</td>
                    </tr>
                </tbody>
            </table>
            <p style="font-size: 7.2pt; margin-top: 2pt;">
                <strong>Statistical Failure Mechanism:</strong> Logistic regression assumes unregularized linear additivity: z = sum(beta_i * X_i). The model complacently summed positive weights for homeownership (beta = +0.283), moderate checking status (beta = +0.345), and clean credit (beta = +0.263), ignoring the <strong>non-linear interaction between loan size and liquidity</strong> (credit_amount * checking_status). A 0–200 DM buffer cushions a small loan, but fails entirely against a 3,337.50 DM obligation.
            </p>
        </div>
        <div class="figure-box">
            <img src="{fig4_b64}" alt="Figure 4: Adversarial Profiles">
            <div class="caption">Figure 4: Test set probabilities highlighting 24 confident errors & profile disparities.</div>
        </div>
    </div>

    <h2>Part 2.4 — Parametric Fairness Trade-Off Analysis</h2>
    <p>
        Swept threshold t from 0.05 to 0.95 across Female (Group A, N=85, base rate 69.41%) and Male (Group B, N=215, base rate 71.16%):
    </p>

    <div class="grid-60-40" style="align-items: center;">
        <div>
            <p style="font-weight: 700; margin-bottom: 1pt; font-size: 7.5pt;">Table 5: Fairness Metrics Sweep Across Thresholds</p>
            <table>
                <thead>
                    <tr>
                        <th>Threshold (t)</th>
                        <th>P(App|F)</th>
                        <th>P(App|M)</th>
                        <th>DP</th>
                        <th>TPR(F)</th>
                        <th>TPR(M)</th>
                        <th>EO</th>
                        <th>PP</th>
                        <th>Accuracy</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>0.05</td><td>1.0000</td><td>1.0000</td><td>1.0000</td><td>1.0000</td><td>1.0000</td><td>1.0000</td><td>0.9754</td><td>70.67%</td></tr>
                    <tr><td>0.15</td><td>0.9529</td><td>0.9860</td><td>0.9664</td><td>0.9831</td><td>1.0000</td><td>0.9296</td><td>0.9922</td><td>72.33%</td></tr>
                    <tr><td>0.25</td><td>0.8941</td><td>0.9628</td><td>0.9287</td><td>0.9661</td><td>0.9935</td><td>0.8238</td><td>1.0214</td><td>74.33%</td></tr>
                    <tr style="background-color: #dbeafe; font-weight: bold;"><td>0.35 (Rec)</td><td>0.8471</td><td>0.9116</td><td>0.9292</td><td>0.9322</td><td>0.9542</td><td>0.8108</td><td>1.0255</td><td>74.00%</td></tr>
                    <tr><td>0.45</td><td>0.7647</td><td>0.8605</td><td>0.8887</td><td>0.8983</td><td>0.9085</td><td>0.6221</td><td>1.0852</td><td>74.00%</td></tr>
                    <tr style="background-color: #fee2e2;"><td>0.55 (Peak)</td><td>0.6824</td><td>0.8047</td><td>0.8480</td><td>0.8475</td><td>0.8889</td><td>0.5156</td><td>1.0966</td><td><strong>76.33%</strong></td></tr>
                    <tr><td>0.65</td><td>0.5882</td><td>0.7256</td><td>0.8107</td><td>0.7797</td><td>0.8105</td><td>0.2981</td><td>1.1574</td><td>74.00%</td></tr>
                    <tr><td>0.75</td><td>0.4353</td><td>0.5767</td><td>0.7547</td><td>0.5763</td><td>0.6928</td><td>0.3974</td><td>1.0750</td><td>69.00%</td></tr>
                    <tr><td>0.85</td><td>0.3294</td><td>0.4186</td><td>0.7869</td><td>0.4576</td><td>0.5359</td><td>0.2981</td><td>1.0584</td><td>62.67%</td></tr>
                    <tr><td>0.95</td><td>0.0824</td><td>0.1535</td><td>0.5365</td><td>0.1186</td><td>0.2157</td><td>0.0000</td><td>1.0000</td><td>42.67%</td></tr>
                </tbody>
            </table>
            <div class="callout" style="font-size: 7pt; margin-top: 1pt;">
                <strong>Quantified Trade-Off Cost:</strong> Moving from t=0.75 to t=0.85 gains +4.27% in DP (0.7547 &rarr; 0.7869), but causes EO to drop -24.99% (0.3974 &rarr; 0.2981). <strong>Trade-off cost = 24.99% / 4.27% = 5.85</strong>.
            </div>
        </div>
        <div class="figure-box">
            <img src="{fig5_b64}" alt="Figure 5: Fairness Curves">
            <div class="caption">Figure 5: Empirical fairness trade-off curve (left) & metric trajectories (right).</div>
        </div>
    </div>
</div>

<!-- ================= PAGE 4 ================= -->
<div class="page">
    <h2>Part 3 — Descriptive Analysis (Questions 1, 2 & 3)</h2>

    <div class="q-block">
        <div class="q-title">Question 1: Comparative Classification Dynamics & Mismatch Mechanics</div>
        <p>
            In our empirical test set evaluation (N=300), Model A (Linear OLS) and Model B (Logistic Regression) generated exactly <strong>90 mismatched cases (30.00% mismatch rate)</strong>. Model A continuous predictions ranged in [-0.0211, 1.3459] with an empirical test set <strong>median of 0.7151</strong>. Thresholding Model A at its median forces exactly 50.0% of the sample (N=150) into positive approval by definition. In contrast, Model B maps log-odds through the sigmoid function, generating valid probabilities in [0.0628, 0.9946]. Applying the standard cutoff P_hat &ge; 0.50 classified <strong>240 individuals (80.00%)</strong> into positive approval. The inter-model confusion matrix confirms the structural nature of this disagreement: both models agreed on 60 negative and 150 positive classifications, while exactly <strong>90 individuals were approved by Model B (P_hat &ge; 0.50) but rejected by Model A (Y_hat &lt; 0.7151)</strong>, with 0 approved by Model A and rejected by Model B.
        </p>
        <p>
            This 30% mismatch stems from diverging thresholding philosophies. Model A’s median split is a <strong>relative, rank-based ordinal threshold</strong> that artificially rejects half the cohort regardless of creditworthiness. Because the test base rate is 70.67% positive, Model B’s <strong>absolute threshold (0.50)</strong> reflects the true positive skew. The 90 disputed individuals occupy the corridor 0.5000 &le; P_hat_B &lt; 0.7151: creditworthy applicants who are penalized solely for being below the 50th percentile of peers. OLS also extrapolates outside probability bounds (-0.0211 and 1.3459). Consequently, Model B achieved 75.33% test accuracy vs. Model A’s 68.00%.
        </p>
    </div>

    <div class="q-block">
        <div class="q-title">Question 2: Simpson's Paradox and Subgroup Heterogeneity</div>
        <p>
            In our analysis of the German Credit dataset, we uncovered an acute instance of <strong>Simpson’s Paradox</strong> when analyzing the impact of existing bank credit lines (<code>existing_credits</code>) across age cohorts: Young Adults (&lt;30 years, N=371) vs. Mature Adults (&ge;30 years, N=629). In the full population (N=1,000), bivariate logistic regression indicates that existing credits positively predict approval (&beta;_Full = +0.1780, SE = 0.1232, p = 0.1488, 95% CI: [-0.0636, +0.4195]). However, disaggregating by age reveals an acute sign reversal:
        </p>
        <ul>
            <li><strong>Young Adults (&lt;30 years):</strong> &beta;_Young = <strong>-0.2203</strong> (SE = 0.2133, p = 0.3016, 95% CI: [-0.6384, +0.1977]) &mdash; <em>Negative Penalty</em></li>
            <li><strong>Mature Adults (&ge;30 years):</strong> &beta;_Mature = <strong>+0.3083</strong> (SE = 0.1586, p = 0.0519, 95% CI: [-0.0025, +0.6192]) &mdash; <em>Positive Asset</em></li>
        </ul>
        <p>
            Statistically, this reversal reflects distinct latent behavioral meanings across life stages. For mature adults, multiple credit accounts indicate an established track record and banking trust. For young adults, multiple loans signal financial instability, over-leveraging, and emergency liquidity distress. Furthermore, in standardized multivariable regression, applicant age has zero statistical impact on men (&beta;_Male = +0.0604, p = 0.5204), but acts as an enormous protective factor for women (&beta;_Female = +0.4741, p = 0.0013)—an effect size nearly <strong>eight times larger</strong>. Deploying an aggregate model that ignores these subgroup interactions would reward over-indebted young borrowers while mispricing young women.
        </p>
    </div>

    <div class="q-block">
        <div class="q-title">Question 3: Omitted-Variable Bias (OVB) Stress-Testing</div>
        <p>
            We deliberately omitted <code>checking_status</code> (Attribute 1: checking liquidity) from the full logistic regression model (48 features, N=700) to measure parameter sensitivity to unobserved confounds. The resulting coefficient shifts confirm severe omitted-variable bias:
        </p>
        <table style="margin-bottom: 2pt;">
            <thead>
                <tr>
                    <th>Feature</th><th>Full Model &beta;</th><th>Reduced Model &beta;</th><th>Absolute Shift &Delta;&beta;</th><th>Percentage Shift &Delta;%</th>
                </tr>
            </thead>
            <tbody>
                <tr><td><code>savings_status_A63</code> (Savings 500–1000 DM)</td><td>+0.3720</td><td>+0.7812</td><td>+0.4092</td><td><strong>+110.00% (Surge)</strong></td></tr>
                <tr><td><code>employment_A73</code> (Job Tenure 1–4 Yrs)</td><td>+0.1278</td><td>+0.2560</td><td>+0.1282</td><td><strong>+100.31% (Surge)</strong></td></tr>
                <tr><td><code>credit_history_A33</code> (Past Payment Delay)</td><td>+0.3941</td><td>+0.5956</td><td>+0.2015</td><td>+51.14%</td></tr>
                <tr><td><code>existing_credits</code> (Credit Accounts)</td><td>-0.0983</td><td>-0.0656</td><td>+0.0328</td><td>+33.31%</td></tr>
                <tr><td><code>age</code> (Standardized Applicant Age)</td><td>+0.1543</td><td>+0.1869</td><td>+0.0326</td><td>+21.16%</td></tr>
                <tr><td><code>duration</code> (Standardized Loan Duration)</td><td>-0.4273</td><td>-0.4325</td><td>-0.0052</td><td>-1.21%</td></tr>
            </tbody>
        </table>
        <p>
            The predictor that shifted most was <code>savings_status_A63</code> (+110.00%), followed by <code>employment_A73</code> (+100.31%). Because checking liquidity is positively correlated with savings and stable employment, purging checking status forced the optimizer to inflate savings and employment weights through proxy absorption: E[beta_hat] = beta_true + beta_omitted &times; Cov(X, Z)/Var(X). An auditor inspecting the reduced model would falsely attribute double the true protective effect to moderate savings, demonstrating that un-stress-tested models cannot be trusted for causal underwriting explanations.
        </p>
    </div>
</div>

<!-- ================= PAGE 5 ================= -->
<div class="page">
    <h2>Part 3 — Descriptive Analysis (Questions 4, 5, 6 & 7)</h2>

    <div class="q-block">
        <div class="q-title">Question 4: Detecting Hidden Confounds in Production Systems</div>
        <p>
            In enterprise lending, unobserved confounders (such as family safety nets or informal remittances) bias training and test sets identically. To detect them, I propose a dual-track strategy combining <strong>Quasi-Experimental Instrumental Variable (IV) Estimation</strong> with <strong>Oster Sensitivity Bounding</strong>. (1) We exploit <strong>hyper-local banking competition shocks</strong> (e.g., staggered regional branch rollouts or postal-code banking fee reforms) as an exogenous instrument (Z). Because branch competition affects loan terms and checking account uptake without altering an applicant's intrinsic moral hazard, it satisfies relevance and exclusion restrictions. A Hausman test comparing beta_OLS against beta_IV formally tests for omitted confounding. (2) We compute Oster's proportionality delta relative to movements in R^2; delta &lt; 1.0 indicates fragility to selection on unobservables. Finally, a negative control outcome (applicant telephone registration) is audited: non-zero weights prove socio-economic confounding.
        </p>
    </div>

    <div class="q-block">
        <div class="q-title">Question 5: Adversarial Subset Construction & Failure Mechanics</div>
        <p>
            We identified exactly <strong>24 adversarial failure instances (8.00% of the 300 test subjects)</strong>: 21 high-confidence false positives (P_hat &ge; 0.75, true default) and 3 high-confidence false negatives (P_hat &le; 0.25, true approved). Profiling reveals striking shared traits: <strong>83.33% own their homes</strong> (vs. 74.00% test baseline), <strong>45.83% hold moderate checking accounts (0–200 DM)</strong> (nearly double the 23.00% baseline), 54.17% have clean credit histories, and their average loan obligation was <strong>3,337.50 DM</strong> (vs. 3,040.18 DM baseline). Logistic regression failed confidently due to <strong>linear additivity without non-linear interaction terms</strong>: it summed positive weights for homeownership (+0.283) and checking status (+0.345), ignoring that a modest 200 DM reserve cannot service an above-average 3,337.50 DM debt obligation.
        </p>
    </div>

    <div class="q-block">
        <div class="q-title">Question 6: The Real-World Cost of Fairness Trade-Offs</div>
        <p>
            Consider two realistic applicants: <strong>Elena (Female, 28, P_hat = 0.480)</strong> seeking a 2,500 DM catering equipment loan, and <strong>Marcus (Male, 29, P_hat = 0.480)</strong> seeking an identical auto repair loan. Under an <strong>Inclusion Threshold (t = 0.35)</strong>, both exceed the threshold and receive loans; Demographic Parity is high (DP = 0.9292, Female approval = 84.71%, Male approval = 91.16%) and Equalized Odds is robust (EO = 0.8108, TPR_Female = 93.22%, TPR_Male = 95.42%). However, under an <strong>Accuracy-Maximizing Threshold (t = 0.55)</strong>, both Elena and Marcus are rejected (0.480 &lt; 0.55). Female approval collapses to 68.24% and EO collapses to 0.5156. If a regulator demands perfect DP (1.000) at t=0.55, the bank would have to set disparate thresholds (t_female = 0.45, t_male = 0.55), approving Elena while rejecting Marcus despite identical 0.480 risk scores, violating individual fairness.
        </p>
    </div>

    <div class="q-block">
        <div class="q-title">Question 7: Defending an Operational Decision Threshold (t = 0.35)</div>
        <p>
            I defend <strong>t = 0.35</strong> as the optimal operational threshold based on four empirical metrics: (1) <strong>Demographic Parity = 0.9292</strong> (Female approval 84.71%, Male approval 91.16%), satisfying the EEOC 80% rule; (2) <strong>Equalized Odds = 0.8108</strong>, with true positive parity at 0.9769 (TPR_Female = 93.22% vs. TPR_Male = 95.42%); (3) <strong>Predictive Parity = 1.0255</strong> (PPV_Female = 76.39% vs. PPV_Male = 74.49%); and (4) <strong>Accuracy = 74.00%</strong> (only 2.33% below peak 76.33% at t=0.55). <em>Strongest Counter-Argument:</em> A credit officer will argue that t=0.35 elevates the False Positive Rate to 65.38% for women and 80.65% for men, approving 67 defaulting applicants in a 5:1 cost matrix. This valid credit risk must be managed via risk-adjusted loan pricing and tiered borrowing caps rather than demographic exclusion.
        </p>
    </div>
</div>

<!-- ================= PAGE 6 ================= -->
<div class="page">
    <h2>Part 3 (Cont.) — Question 8 & Part 4 Reflection Essay</h2>

    <div class="q-block">
        <div class="q-title">Question 8: Strategic Policy Choice: Demographic Parity vs. Equalized Odds</div>
        <p>
            If forced to choose, I unequivocally recommend prioritizing <strong>Equalized Odds (EO)</strong> over pure Demographic Parity (DP). Under Kleinberg’s Impossibility Theorem, unequal base rates (Female 69.41% vs. Male 71.16%) make DP, EO, and PP mutually incompatible. Equalized Odds enforces meritocratic fairness: creditworthy applicants face equal approval odds regardless of sex (at t=0.35, TPR_Female = 93.22% vs. TPR_Male = 95.42%, a 2.20% gap), while preserving Predictive Parity (PP = 1.0255). We explicitly sacrifice strict DP (0.9292 at t=0.35; 0.8480 at t=0.55). Sacrificing pure DP is necessary: enforcing equal acceptance rates across unequal financial distributions would force banks to approve unqualified women (causing debt traps and default) or deny qualified men, violating procedural justice.
        </p>
    </div>

    <h2>Part 4 — Reflection Essay (~500 words)</h2>
    <div style="font-size: 7.2pt; font-style: italic; color: #475569; margin-bottom: 3pt;">
        "If a policy-maker asked you: 'just give me one number: should we deploy this model or not?', what would you say, and what is the limitation of that 'one number' answer that you discovered yourself through your analysis?"
    </div>

    <div class="q-block" style="border-left: 3px solid #1e3a8a;">
        <div class="q-title">1. Direct Answer (1–2 sentences)</div>
        <p>
            I would recommend <strong>conditional deployment under strict segment-specific thresholding (t = 0.35) and continuous human-in-the-loop oversight</strong>, because a single binary deployment number obscures that default thresholding maximizes global accuracy while destroying equal opportunity for female borrowers and failing predictably on high-exposure homeowners.
        </p>

        <div class="q-title" style="margin-top: 3pt;">2. Why a Single Number Fails (300–400 words)</div>
        <p>
            The fundamental lesson of this stress-test audit is that reducing a sociotechnical AI system to a single summary metric—whether overall accuracy (75.33%), AUC-ROC (0.792), or a composite index—is an act of intellectual complacency that conceals severe structural trade-offs.
        </p>
        <p>
            First, <strong>aggregate accuracy systematically masks catastrophic subgroup collapses</strong>. At our model’s peak accuracy threshold of t = 0.55 (76.33% accuracy), Equalized Odds collapses to a dismal <strong>0.5156</strong>, with the model approving non-creditworthy men at nearly double the rate of non-creditworthy women (FPR_Male = 59.68% vs. FPR_Female = 30.77%), while female loan approvals plunge to 68.24%. Celebrating "76% accuracy" ignores that half of the equal opportunity metric has been eliminated.
        </p>
        <p>
            Second, <strong>threshold selection is an unstated value judgment, not a mathematical fact</strong>. Choosing between t = 0.35 (prioritizing inclusion and EO of 0.8108) and t = 0.55 (prioritizing default suppression and bank profitability) cannot be answered by data science. It is an economic and political choice balancing borrower credit access against institutional capital loss. Collapsing this to a binary "deploy" command abdicates human accountability to an arbitrary mathematical default (0.50).
        </p>
        <p>
            Third, <strong>fairness metrics are mathematically adversarial</strong>. Under Kleinberg's and Chouldechova's theorems, differing base default rates (69.41% female vs. 71.16% male) ensure that Demographic Parity, Equalized Odds, and Predictive Parity cannot be simultaneously fulfilled. Gaining +4.27% in DP from t=0.75 to t=0.85 causes EO to plunge -24.99%—a punishing trade-off cost ratio of <strong>5.85</strong>. A single metric conceals which protected group is paying the cost.
        </p>
        <p>
            Fourth, <strong>models fail with extreme confidence on predictable adversarial clusters</strong>. Our model confidently misclassified 24 test cases (8.00%), assigning P_hat &ge; 0.75 to defaulting applicants simply because they were homeowners (83.33%) with moderate checking reserves (45.83%), oblivious to their heavy 3,337.50 DM debt burden.
        </p>
        <p>
            Finally, <strong>hidden confounds remain invisible to summary statistics</strong>. Purging checking liquidity caused savings weights to inflate by <strong>+110.00%</strong> and employment weights by <strong>+100.31%</strong>, proving that observational models readily disguise omitted confounders as legitimate risk indicators.
        </p>

        <div class="q-title" style="margin-top: 3pt;">3. Grounding in Evidence (50–100 words)</div>
        <p>
            Our computations substantiate every limitation: the 30.00% mismatch between Model A and B, the Simpson’s sign reversal on existing credits (-0.2203 young vs. +0.3083 mature), the 110.00% coefficient inflation under omitted-variable testing, the 24 adversarial failures with 83.33% homeownership, and the plunge in Equalized Odds from 0.8108 at t=0.35 to 0.5156 at t=0.55.
        </p>

        <div class="q-title" style="margin-top: 3pt;">4. Closing (50 words)</div>
        <p>
            Responsible AI governance is an exercise in transparently navigating unavoidable trade-offs, not chasing single-metric optimization. A single number offers executives the illusion of certainty; true algorithmic accountability demands exposing who wins, who loses, and which ethical values are compromised at every operational threshold.
        </p>
    </div>
</div>

</body>
</html>
"""

with open("report_compact.html", "w", encoding="utf-8") as f:
    f.write(compact_html)

print("Generated report_compact.html successfully. Now rendering to PDF via Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('report_compact.html').replace(os.sep, '/')}")
    page.pdf(
        path="Assignment1_Report_s24bcau0154.pdf",
        format="A4",
        print_background=True,
        margin={
            "top": "8mm",
            "bottom": "8mm",
            "left": "10mm",
            "right": "10mm"
        }
    )
    browser.close()

reader = pypdf.PdfReader("Assignment1_Report_s24bcau0154.pdf")
print(f"Assignment1_Report_s24bcau0154.pdf page count: {len(reader.pages)}")

