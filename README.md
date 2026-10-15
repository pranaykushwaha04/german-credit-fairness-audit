# CSET485 – AI and Society: Assignment #1
## Algorithmic Stress-Testing, Hidden Confounds & Fairness Trade-Offs in Credit Underwriting

**Student Enrollment ID:** `s24bcau0154`  
**Dataset Assigned:** German Credit Data (Statlog) — *Assigned based on last digit `4`*  
**Random State / Seed:** `154` — *Assigned based on last 3 digits of roll number*  
**Data Partition:** 70% Train (700 rows) / 30% Test (300 rows)  
**Course:** CSET485 – AI and Society (10 Marks)  
**Submission Deadline:** 19 Oct 2026, 23:59 IST  

---

## 📌 Executive Summary
Predictive models deployed in high-stakes societal domains—such as credit lending, bail determinations, and hiring—frequently project an illusion of statistical rigor while concealing demographic inequities, severe omitted-variable bias, and irreconcilable fairness trade-offs. 

Using the **German Credit dataset ($N=1,000$)**, this repository delivers an end-to-end empirical audit comparing **Ordinary Least Squares (OLS) Linear Probability Modeling** and **Logistic Regression**, followed by four targeted stress-testing protocols:
1. **Model A vs. Model B Threshold Mismatch Analysis:** Linear OLS median cutoff (`0.7151`) vs. Logistic `0.50` probability cutoff produced **90 mismatched cases (30.00%)**.
2. **Simpson's Paradox Hunt:** Sign reversal on `existing_credits` across age cohorts (Young $<30$: $\beta = -0.2203$ vs. Mature $\ge 30$: $\beta = +0.3083$), and an 8x larger protective effect of age for females ($\beta = +0.4741, p = 0.0013$) vs. males ($\beta = +0.0604, p = 0.5204$).
3. **Omitted-Variable Bias (OVB):** Purging checking liquidity (`checking_status`) forced remaining proxies to absorb omitted explanatory power, inflating `savings_status_A63` by **$+110.00\%$** and `employment_A73` by **$+100.31\%$**.
4. **Adversarial Subset Construction:** Extracted 24 confident errors (8.00% of test set), characterized by 83.33% homeownership, 45.83% moderate checking accounts, and heavier loan obligations (3,337.50 DM vs. 3,040.18 DM baseline), exposing unregularized linear additivity failures.
5. **Parametric Fairness Trade-Offs:** Swept decision thresholds from $t=0.05$ to $0.95$ across gender. Defended $t=0.35$ ($\text{DP} = 0.9292, \text{EO} = 0.8108, \text{PP} = 1.0255$, Accuracy = 74.00%), and quantified a trade-off cost of **5.85** between DP and EO.

---

## 📁 Repository Structure

```text
├── assignment1_german_credit_analysis.ipynb   # Main reproducible Jupyter Notebook (Code + Outputs)
├── german.data                               # Raw German Credit dataset (1,000 rows, 20 attributes)
├── german.doc                                # Official UCI Hofmann dataset documentation
├── Assignment1_Report_s24bcau0154.pdf        # Complete 6-Page Submission PDF Report
├── increase_font.pdf                         # 6-Page Submission PDF with 10pt font
├── increase_font.docx                        # 6-Page Submission Word document
├── figures/                                  # High-resolution generated audit plots
│   ├── part1_model_comparison.png            # Part 1 prediction distributions & mismatch matrix
│   ├── part2_1_simpsons_paradox.png          # Part 2.1 Simpson's paradox & gender divergence
│   ├── part2_2_ovb_shifts.png                # Part 2.2 Omitted-variable bias shifts
│   ├── part2_3_adversarial_subset.png        # Part 2.3 Adversarial subset profile disparities
│   └── part2_4_fairness_tradeoff.png         # Part 2.4 Empirical DP vs EO trade-off frontier
├── outputs/                                  # Structured CSV export tables & summary JSON
│   ├── fairness_metrics_sweep.csv            # 10-threshold fairness metrics sweep
│   ├── ovb_summary_table.csv                 # Before/after OVB coefficient shifts
│   ├── simpson_age_reversal.csv              # Simpson's age cohort regression outputs
│   ├── simpson_gender.csv                    # Multivariable gender divergence outputs
│   ├── adversarial_subset_rows.csv           # 24 confident adversarial failure rows
│   └── all_summary_results.json              # Aggregated metrics JSON
├── requirements.txt                          # Python dependencies
└── README.md                                 # Documentation & audit walkthrough
```

---

## 🚀 How to Run & Reproduce

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Set up virtual environment & install requirements
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Jupyter Notebook
```bash
jupyter notebook assignment1_german_credit_analysis.ipynb
```
Select **Kernel -> Restart & Run All**. Every number, table, and visualization cited in the report will be recomputed from scratch.

---

## 📊 Summary of Computed Empirical Results

| Analysis / Section | Key Metric | Computed Numerical Value | Interpretation |
| :--- | :--- | :---: | :--- |
| **Part 1: Model A** | OLS Median Prediction | **`0.7151`** | Predictions span `[-0.0211, 1.3459]`, outside probability bounds |
| **Part 1: Model B** | Logistic Cutoff | **`0.5000`** | Sigmoidal probabilities `[0.0628, 0.9946]` |
| **Part 1: Mismatch** | Classification Disagreement | **`90 / 300 (30.00%)`** | Model A relative rank cutoff rejects qualified corridor $0.50 \le P < 0.7151$ |
| **Part 2.1: Simpson's** | Existing Credits ($\beta$) | Full: **`+0.1780`**<br>Young: **`-0.2203`**<br>Mature: **`+0.3083`** | Acute sign reversal across age cohorts ($p=0.0519$ for mature) |
| **Part 2.1: Gender** | Age Effect on Approval ($\beta$) | Male: **`+0.0604`** ($p=0.5204$)<br>Female: **`+0.4741`** ($p=0.0013$) | Age has ~8x larger protective effect for women than men |
| **Part 2.2: OVB** | `savings_status_A63` Shift | **`+0.3720 → +0.7812 (+110.00%)`** | Omitted checking liquidity absorbed by savings proxies |
| **Part 2.2: OVB** | `employment_A73` Shift | **`+0.1278 → +0.2560 (+100.31%)`** | Employment tenure weight artificially doubled |
| **Part 2.3: Adversarial** | High-Confidence Errors | **`24 / 300 (8.00%)`** | 21 false positives ($\hat{P} \ge 0.75$), 3 false negatives ($\hat{P} \le 0.25$) |
| **Part 2.3: Profile** | Homeownership Rate | **`83.33%`** (vs 74.00% baseline) | Linear additivity blindness to debt-to-reserve interactions |
| **Part 2.4: Sweep** | Recommended Threshold | **`t = 0.35`** | $\text{DP} = 0.9292$, $\text{EO} = 0.8108$, $\text{PP} = 1.0255$, Acc = $74.00\%$ |
| **Part 2.4: Trade-Off** | Cost Ratio ($t=0.75 \to 0.85$) | **`5.85`** | Gaining +4.27% in DP costs -24.99% in EO ($\text{Cost} = 24.99 / 4.27$) |

---

## 📜 Author & Academic Integrity
- **Student Enrollment:** `s24bcau0154`
- **Institution / Course:** CSET485 – AI and Society
- **Deliverable:** Fully reproducible code and standalone PDF audit report submitted per academic guidelines.
