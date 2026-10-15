import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_compact_docx():
    doc = docx.Document()

    # Set page margins to 0.5 inches (36pt) for 6-page density
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.55)
        section.right_margin = Inches(0.55)
        
        # Add running header and footer
        header = section.header
        hp = header.paragraphs[0]
        hp.text = "CSET485 – AI and Society | Assignment #1: Algorithmic Stress-Testing & Fairness Audit"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp.style.font.name = "Calibri"
        hp.style.font.size = Pt(8)
        hp.style.font.color.rgb = RGBColor(100, 116, 139)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = "Enrollment ID: s24bcau0154 | Dataset: German Credit Data (Seed: 154)"
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fp.style.font.name = "Calibri"
        fp.style.font.size = Pt(8)
        fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Style definitions
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(8.5)
    style_normal.font.color.rgb = RGBColor(30, 41, 59)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(2.5)

    def add_sec_head(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(30, 58, 138)
        return p

    def add_sub_head(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(30, 64, 175)
        return p

    # --- TITLE ---
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(1)
    r_title = title_p.add_run("CSET485 – AI and Society: Assignment #1 (10 Marks)")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(3)
    r_sub = sub_p.add_run("Auditing Bias, Structural Confounds & Fairness Defensibility in Credit Underwriting")
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata Table
    meta_table = doc.add_table(rows=2, cols=3)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        [("Enrollment ID:", " s24bcau0154"), ("Assigned Dataset:", " German Credit (Last digit 4)"), ("Seed:", " 154 (Last 3 digits)")],
        [("Partition:", " 70% Train (700) / 30% Test (300)"), ("Target:", " Approval (1=Approve, 0=Reject)"), ("Reproducibility:", " Full Jupyter Notebook")]
    ]
    for r_idx, row in enumerate(meta_table.rows):
        for c_idx, cell in enumerate(row.cells):
            label, val = meta_data[r_idx][c_idx]
            cell.width = Inches(2.4)
            set_cell_background(cell, "F1F5F9")
            set_cell_margins(cell, 40, 40, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r1 = p.add_run(label)
            r1.bold = True
            r1.font.size = Pt(7.5)
            r1.font.color.rgb = RGBColor(30, 64, 175)
            r2 = p.add_run(val)
            r2.font.size = Pt(7.5)

    p_exec = doc.add_paragraph()
    p_exec.paragraph_format.space_before = Pt(3)
    p_exec.paragraph_format.space_after = Pt(3)
    r_eb = p_exec.add_run("Executive Summary: ")
    r_eb.bold = True
    p_exec.add_run(
        "Algorithmic underwriting systems often appear statistically robust while masking demographic disparities, omitted confounders, "
        "and unavoidable fairness trade-offs. Using the German Credit dataset (N=1,000), we stress-test Linear Probability OLS and Logistic Regression "
        "across threshold mismatches, Simpson's paradox, omitted-variable bias, adversarial failure clusters, and parametric fairness frontiers. "
        "All findings are grounded strictly in our computed numbers."
    )

    # --- DATA PREPROCESSING ---
    add_sec_head("Data Preprocessing & Exploratory Audit")
    doc.add_paragraph(
        "1. Missing Values: Programmatic scan confirmed 0 missing values across all 1,000 instances and 20 features.\n"
        "2. Categorical Feature Encoding: 13 qualitative features were encoded via One-Hot Encoding dropping the first category (drop_first=True) to eliminate multicollinearity and dummy variable traps, yielding 41 indicator columns and 7 continuous regressors (48 total modeled predictors).\n"
        "3. Feature Scaling: Standardized all 7 continuous features (duration, credit_amount, installment_commitment, residence_since, age, existing_credits, num_dependents) with StandardScaler fit strictly on the 70% train split (N=700, seed=154) to eliminate data leakage.\n"
        "4. Outlier Handling Rationale: 70 outliers in duration (7.0%), 72 in credit_amount (7.2%), and 23 in age (2.3%) were identified via the 1.5 x IQR rule. These were deliberately preserved without clipping; high balances and long loan maturities represent legitimate tail-risk default liabilities that models must learn."
    )

    # --- PART 1 ---
    add_sec_head("Part 1 — Model Fitting & Threshold Mismatch Analysis")
    doc.add_paragraph(
        "Both models were fitted on the 700-sample training matrix (train base rate: 69.71%, test base rate: 70.67%):\n"
        "• Model A (Linear OLS Regression): Continuous predictions Y_hat on test set range in [-0.0211, 1.3459] with an empirical median of 0.7151. Mandating the threshold at the median (Y_hat >= 0.7151) classifies exactly 150 instances (50.0%) as positive.\n"
        "• Model B (Logistic Regression): Sigmoidal probabilities P_hat range in [0.0628, 0.9946]. Thresholding at standard P_hat >= 0.50 classifies 240 instances (80.0%) as positive. Overall test accuracy: Model B = 75.33% vs. Model A = 68.00%."
    )

    # Confusion matrix Table 1
    t1 = doc.add_table(rows=3, cols=4)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["Classification Matrix", "Model A Negative (< Median)", "Model A Positive (>= Median 0.7151)", "Total Model B"]
    for c_idx, h in enumerate(t1_headers):
        cell = t1.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    t1_rows = [
        ["Model B Negative (< 0.50)", "60 (True Agreement)", "0", "60 (20.0%)"],
        ["Model B Positive (>= 0.50)", "90 (Mismatched Cases: 30.0%)", "150 (True Agreement)", "240 (80.0%)"]
    ]
    for r_idx, r_data in enumerate(t1_rows):
        for c_idx, val in enumerate(r_data):
            cell = t1.cell(r_idx + 1, c_idx)
            if "Mismatched" in val:
                set_cell_background(cell, "FEE2E2")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if "Mismatched" in val:
                r.bold = True

    doc.add_paragraph(
        "Key Mechanism: Exactly 90 out of 300 individuals (30.00%) are mismatched. Model A forces a relative rank median split (50/50), discarding qualified borrowers in the corridor 0.5000 <= P_hat_B < 0.7151, while Model B reflects the true 70.67% base rate."
    )

    if os.path.exists("figures/part1_model_comparison.png"):
        doc.add_picture("figures/part1_model_comparison.png", width=Inches(4.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(3)

    doc.add_page_break()

    # --- PART 2.1 & 2.2 ---
    add_sec_head("Part 2.1 — Simpson's Paradox Hunt")
    doc.add_paragraph(
        "1. Sign Reversal on Existing Credits across Age: In the full population (N=1,000), bivariate logistic regression indicates existing credits increase approval odds (beta = +0.1780). Disaggregating by age reveals an acute sign reversal: for Young Adults (<30, N=371), beta reverses to negative (beta = -0.2203), whereas for Mature Adults (>=30, N=629), it is strongly positive (beta = +0.3083, p = 0.0519). For young borrowers, multiple loans signal emergency borrowing and liquidity distress; for mature adults, they reflect seasoned credit history.\n"
        "2. Age Divergence across Gender: In standardized multivariable regression, applicant age has zero statistical impact on men (beta_Male = +0.0604, p = 0.5204), but acts as an enormous protective factor for women (beta_Female = +0.4741, p = 0.0013)—an effect size nearly eight times larger."
    )

    # Table 2
    t2 = doc.add_table(rows=6, cols=6)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Subgroup Analysis", "N", "Coef (beta)", "Std. Error", "p-value", "95% Confidence Interval"]
    for c_idx, h in enumerate(t2_headers):
        cell = t2.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    t2_rows = [
        ["Existing Credits: Full Dataset", "1,000", "+0.1780", "0.1232", "0.1488", "[-0.0636, +0.4195] (Weak Positive)"],
        ["Existing Credits: Young (<30)", "371", "-0.2203", "0.2133", "0.3016", "[-0.6384, +0.1977] (Sign Reversal)"],
        ["Existing Credits: Mature (>=30)", "629", "+0.3083", "0.1586", "0.0519", "[-0.0025, +0.6192] (Positive Asset)"],
        ["Multivariable Age: Male Subgroup", "690", "+0.0604", "0.0940", "0.5204", "[-0.1238, +0.2445] (Null for Men)"],
        ["Multivariable Age: Female Subgroup", "310", "+0.4741", "0.1469", "0.0013", "[+0.1861, +0.7620] (~8x Effect Size)"]
    ]
    for r_idx, r_data in enumerate(t2_rows):
        for c_idx, val in enumerate(r_data):
            cell = t2.cell(r_idx + 1, c_idx)
            if "Sign Reversal" in val:
                set_cell_background(cell, "FEE2E2")
            elif "8x" in val:
                set_cell_background(cell, "DCFCE7")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if "Sign Reversal" in val or "8x" in val:
                r.bold = True

    if os.path.exists("figures/part2_1_simpsons_paradox.png"):
        doc.add_picture("figures/part2_1_simpsons_paradox.png", width=Inches(4.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(3)

    add_sec_head("Part 2.2 — Omitted-Variable Bias (OVB) Stress-Testing")
    doc.add_paragraph(
        "To measure sensitivity to unobserved confounds, checking_status (Attribute 1: checking liquidity) was omitted. "
        "Because liquidity correlates with savings and job tenure, remaining regressors absorbed omitted explanatory power through proxy correlation: E[beta_hat] = beta_true + beta_omitted x Cov(X, Z)/Var(X)."
    )

    # Table 3
    t3 = doc.add_table(rows=7, cols=6)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_headers = ["Predictor Variable", "Role / Meaning", "Full beta", "Reduced beta", "Shift Delta beta", "% Change"]
    for c_idx, h in enumerate(t3_headers):
        cell = t3.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    t3_rows = [
        ["savings_status_A63", "Savings 500–1000 DM", "+0.3720", "+0.7812", "+0.4092", "+110.00% (Surge)"],
        ["employment_A73", "Job Tenure 1–4 Yrs", "+0.1278", "+0.2560", "+0.1282", "+100.31% (Surge)"],
        ["credit_history_A33", "Past Payment Delay", "+0.3941", "+0.5956", "+0.2015", "+51.14%"],
        ["existing_credits", "Existing Bank Credits", "-0.0983", "-0.0656", "+0.0328", "+33.31%"],
        ["age", "Applicant Age", "+0.1543", "+0.1869", "+0.0326", "+21.16%"],
        ["duration", "Loan Duration (Mo.)", "-0.4273", "-0.4325", "-0.0052", "-1.21%"]
    ]
    for r_idx, r_data in enumerate(t3_rows):
        for c_idx, val in enumerate(r_data):
            cell = t3.cell(r_idx + 1, c_idx)
            if "Surge" in val:
                set_cell_background(cell, "DBEAFE")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if "Surge" in val:
                r.bold = True

    if os.path.exists("figures/part2_2_ovb_shifts.png"):
        doc.add_picture("figures/part2_2_ovb_shifts.png", width=Inches(4.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(3)

    doc.add_page_break()

    # --- PART 2.3 & 2.4 ---
    add_sec_head("Part 2.3 — Adversarial Subset Construction & Failure Mechanics")
    doc.add_paragraph(
        "Extracted test cases where Model B made confident errors (P_hat >= 0.75 with default Y=0, or P_hat <= 0.25 with approval Y=1). Exactly 24 instances (8.00% of test cohort) satisfied this condition: 21 high-confidence false positives, 3 high-confidence false negatives."
    )

    t4 = doc.add_table(rows=6, cols=4)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4_headers = ["Attribute / Demographic Metric", "Test Set Baseline (N=300)", "Adversarial Subset (N=24)", "Disparity / Signature"]
    for c_idx, h in enumerate(t4_headers):
        cell = t4.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    t4_rows = [
        ["Homeownership Rate (housing = A152)", "74.00%", "83.33%", "+9.33% Over-Represented"],
        ["Moderate Checking (A12: 0–200 DM)", "23.00%", "45.83%", "Nearly Double Baseline (+22.83%)"],
        ["Clean Existing Credit History (A32)", "53.67%", "54.17%", "Parity with Clean Baseline"],
        ["Mean Requested Credit Obligation", "3,040.18 DM", "3,337.50 DM", "+$297.32 DM Heavier Burden"],
        ["Female Representation", "28.33%", "20.83%", "-7.50% Under-Represented"]
    ]
    for r_idx, r_data in enumerate(t4_rows):
        for c_idx, val in enumerate(r_data):
            cell = t4.cell(r_idx + 1, c_idx)
            if "Double" in val:
                set_cell_background(cell, "FEE2E2")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if "Double" in val:
                r.bold = True

    doc.add_paragraph(
        "Statistical Failure Mechanism: Logistic regression assumes unregularized linear additivity: z = sum(beta_i * X_i). The model complacently summed positive weights for homeownership (beta = +0.283), moderate checking status (beta = +0.345), and clean credit (beta = +0.263), ignoring the non-linear interaction between loan size and liquidity (credit_amount * checking_status). A 0–200 DM buffer cushions a small loan, but fails entirely against a 3,337.50 DM obligation."
    )

    if os.path.exists("figures/part2_3_adversarial_subset.png"):
        doc.add_picture("figures/part2_3_adversarial_subset.png", width=Inches(4.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(3)

    add_sec_head("Part 2.4 — Parametric Fairness Trade-Off Analysis")
    doc.add_paragraph(
        "Swept threshold t from 0.05 to 0.95 across Female (Group A, N=85, base rate 69.41%) and Male (Group B, N=215, base rate 71.16%):"
    )

    t5 = doc.add_table(rows=11, cols=9)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5_headers = ["Threshold (t)", "P(App|F)", "P(App|M)", "DP", "TPR(F)", "TPR(M)", "EO", "PP", "Accuracy"]
    for c_idx, h in enumerate(t5_headers):
        cell = t5.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 35, 35, 45, 45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7)
        r.font.color.rgb = RGBColor(255, 255, 255)

    t5_rows = [
        ["0.05", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000", "0.9754", "70.67%"],
        ["0.15", "0.9529", "0.9860", "0.9664", "0.9831", "1.0000", "0.9296", "0.9922", "72.33%"],
        ["0.25", "0.8941", "0.9628", "0.9287", "0.9661", "0.9935", "0.8238", "1.0214", "74.33%"],
        ["0.35 (Rec)", "0.8471", "0.9116", "0.9292", "0.9322", "0.9542", "0.8108", "1.0255", "74.00%"],
        ["0.45", "0.7647", "0.8605", "0.8887", "0.8983", "0.9085", "0.6221", "1.0852", "74.00%"],
        ["0.55 (Peak)", "0.6824", "0.8047", "0.8480", "0.8475", "0.8889", "0.5156", "1.0966", "76.33%"],
        ["0.65", "0.5882", "0.7256", "0.8107", "0.7797", "0.8105", "0.2981", "1.1574", "74.00%"],
        ["0.75", "0.4353", "0.5767", "0.7547", "0.5763", "0.6928", "0.3974", "1.0750", "69.00%"],
        ["0.85", "0.3294", "0.4186", "0.7869", "0.4576", "0.5359", "0.2981", "1.0584", "62.67%"],
        ["0.95", "0.0824", "0.1535", "0.5365", "0.1186", "0.2157", "0.0000", "1.0000", "42.67%"]
    ]
    for r_idx, r_data in enumerate(t5_rows):
        for c_idx, val in enumerate(r_data):
            cell = t5.cell(r_idx + 1, c_idx)
            if "0.35" in r_data[0]:
                set_cell_background(cell, "DBEAFE")
            elif "0.55" in r_data[0]:
                set_cell_background(cell, "FEE2E2")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 30, 30, 45, 45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(7)
            if "0.35" in r_data[0]:
                r.bold = True

    doc.add_paragraph(
        "Trade-Off Quantification: Moving from t=0.75 to t=0.85 gains +4.27% in DP (0.7547 -> 0.7869), but causes EO to drop -24.99% (0.3974 -> 0.2981). "
        "Trade-Off Cost = (Loss in EO) / (Gain in DP) = 24.99% / 4.27% = 5.85. Every 1% gained in DP costs 5.85% in EO."
    )

    if os.path.exists("figures/part2_4_fairness_tradeoff.png"):
        doc.add_picture("figures/part2_4_fairness_tradeoff.png", width=Inches(4.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(3)

    doc.add_page_break()

    # --- PART 3: Q1, Q2, Q3 ---
    add_sec_head("Part 3 — Descriptive Analysis (Questions 1, 2 & 3)")

    add_sub_head("Question 1: Comparative Classification Dynamics & Mismatch Mechanics")
    doc.add_paragraph(
        "In our empirical test set evaluation (N=300), Model A (Linear OLS) and Model B (Logistic Regression) generated exactly 90 mismatched cases (30.00% mismatch rate). Model A continuous predictions ranged in [-0.0211, 1.3459] with an empirical test set median of 0.7151. Thresholding Model A at its median forces exactly 50.0% of the sample (N=150) into positive approval by definition. In contrast, Model B maps log-odds through the sigmoid function, generating valid probabilities in [0.0628, 0.9946]. Applying the standard cutoff P_hat >= 0.50 classified 240 individuals (80.00%) into positive approval. The inter-model confusion matrix confirms the structural nature of this disagreement: both models agreed on 60 negative and 150 positive classifications, while exactly 90 individuals were approved by Model B (P_hat >= 0.50) but rejected by Model A (Y_hat < 0.7151), with 0 approved by Model A and rejected by Model B.\n\n"
        "This 30% mismatch stems from diverging thresholding philosophies. Model A’s median split is a relative, rank-based ordinal threshold that artificially rejects half the cohort regardless of creditworthiness. Because the test base rate is 70.67% positive, Model B’s absolute threshold (0.50) reflects the true positive skew. The 90 disputed individuals occupy the corridor 0.5000 <= P_hat_B < 0.7151: creditworthy applicants who are penalized solely for being below the 50th percentile of peers. OLS also extrapolates outside probability bounds (-0.0211 and 1.3459). Consequently, Model B achieved 75.33% test accuracy vs. Model A’s 68.00%."
    )

    add_sub_head("Question 2: Simpson's Paradox and Subgroup Heterogeneity")
    doc.add_paragraph(
        "In our analysis of the German Credit dataset, we uncovered an acute instance of Simpson’s Paradox when analyzing the impact of existing bank credit lines (existing_credits) across age cohorts: Young Adults (<30 years, N=371) vs. Mature Adults (>=30 years, N=629). In the full population (N=1,000), bivariate logistic regression indicates that existing credits positively predict approval (beta_Full = +0.1780, SE = 0.1232, p = 0.1488, 95% CI: [-0.0636, +0.4195]). However, disaggregating by age reveals an acute sign reversal:\n"
        "• Young Adults (<30 years): beta_Young = -0.2203 (SE = 0.2133, p = 0.3016, 95% CI: [-0.6384, +0.1977]) — Negative Penalty\n"
        "• Mature Adults (>=30 years): beta_Mature = +0.3083 (SE = 0.1586, p = 0.0519, 95% CI: [-0.0025, +0.6192]) — Positive Asset\n\n"
        "Statistically, this reversal reflects distinct latent behavioral meanings across life stages. For mature adults, multiple credit accounts indicate an established track record and banking trust. For young adults, multiple loans signal financial instability, over-leveraging, and emergency liquidity distress. Furthermore, in standardized multivariable regression, applicant age has zero statistical impact on men (beta_Male = +0.0604, p = 0.5204), but acts as an enormous protective factor for women (beta_Female = +0.4741, p = 0.0013)—an effect size nearly eight times larger. Deploying an aggregate model that ignores these subgroup interactions would reward over-indebted young borrowers while mispricing young women."
    )

    add_sub_head("Question 3: Omitted-Variable Bias (OVB) Stress-Testing")
    doc.add_paragraph(
        "We deliberately omitted checking_status (Attribute 1: checking liquidity) from the full logistic regression model (48 features, N=700) to measure parameter sensitivity to unobserved confounds. The resulting coefficient shifts confirm severe omitted-variable bias:\n"
        "• savings_status_A63 (Savings 500–1000 DM): +0.3720 -> +0.7812 (+110.00% surge)\n"
        "• employment_A73 (Job Tenure 1–4 Yrs): +0.1278 -> +0.2560 (+100.31% surge)\n"
        "• credit_history_A33 (Past Payment Delay): +0.3941 -> +0.5956 (+51.14% change)\n"
        "• existing_credits (Existing Bank Credits): -0.0983 -> -0.0656 (+33.31% change)\n"
        "• age (Standardized Age): +0.1543 -> +0.1869 (+21.16% change)\n"
        "• duration (Standardized Loan Duration): -0.4273 -> -0.4325 (-1.21% change)\n\n"
        "The predictor that shifted most was savings_status_A63 (+110.00%), followed by employment_A73 (+100.31%). Because checking liquidity is positively correlated with savings and stable employment, purging checking status forced the optimizer to inflate savings and employment weights through proxy absorption: E[beta_hat] = beta_true + beta_omitted x Cov(X, Z)/Var(X). An auditor inspecting the reduced model would falsely attribute double the true protective effect to moderate savings, demonstrating that un-stress-tested models cannot be trusted for causal underwriting explanations."
    )

    doc.add_page_break()

    # --- PART 3: Q4, Q5, Q6, Q7 ---
    add_sec_head("Part 3 — Descriptive Analysis (Questions 4, 5, 6 & 7)")

    add_sub_head("Question 4: Detecting Hidden Confounds in Production Systems")
    doc.add_paragraph(
        "In enterprise lending, unobserved confounders (such as family safety nets or informal remittances) bias training and test sets identically. To detect them, I propose a dual-track strategy combining Quasi-Experimental Instrumental Variable (IV) Estimation with Oster Sensitivity Bounding. (1) We exploit hyper-local banking competition shocks (e.g., staggered regional branch rollouts or postal-code banking fee reforms) as an exogenous instrument (Z). Because branch competition affects loan terms and checking account uptake without altering an applicant's intrinsic moral hazard, it satisfies relevance and exclusion restrictions. A Hausman test comparing beta_OLS against beta_IV formally tests for omitted confounding. (2) We compute Oster's proportionality delta relative to movements in R^2; delta < 1.0 indicates fragility to selection on unobservables. Finally, a negative control outcome (applicant telephone registration) is audited: non-zero weights prove socio-economic confounding."
    )

    add_sub_head("Question 5: Adversarial Subset Construction & Failure Mechanics")
    doc.add_paragraph(
        "We identified exactly 24 adversarial failure instances (8.00% of the 300 test subjects): 21 high-confidence false positives (P_hat >= 0.75, true default) and 3 high-confidence false negatives (P_hat <= 0.25, true approved). Profiling reveals striking shared traits: 83.33% own their homes (vs. 74.00% test baseline), 45.83% hold moderate checking accounts (0–200 DM) (nearly double the 23.00% baseline), 54.17% have clean credit histories, and their average loan obligation was 3,337.50 DM (vs. 3,040.18 DM baseline). Logistic regression failed confidently due to linear additivity without non-linear interaction terms: it summed positive weights for homeownership (+0.283) and checking status (+0.345), ignoring that a modest 200 DM reserve cannot service an above-average 3,337.50 DM debt obligation."
    )

    add_sub_head("Question 6: The Real-World Cost of Fairness Trade-Offs")
    doc.add_paragraph(
        "Consider two realistic applicants: Elena (Female, 28, P_hat = 0.480) seeking a 2,500 DM catering equipment loan, and Marcus (Male, 29, P_hat = 0.480) seeking an identical auto repair loan. Under an Inclusion Threshold (t = 0.35), both exceed the threshold and receive loans; Demographic Parity is high (DP = 0.9292, Female approval = 84.71%, Male approval = 91.16%) and Equalized Odds is robust (EO = 0.8108, TPR_Female = 93.22%, TPR_Male = 95.42%). However, under an Accuracy-Maximizing Threshold (t = 0.55), both Elena and Marcus are rejected (0.480 < 0.55). Female approval collapses to 68.24% and EO collapses to 0.5156. If a regulator demands perfect DP (1.000) at t=0.55, the bank would have to set disparate thresholds (t_female = 0.45, t_male = 0.55), approving Elena while rejecting Marcus despite identical 0.480 risk scores, violating individual fairness."
    )

    add_sub_head("Question 7: Defending an Operational Decision Threshold (t = 0.35)")
    doc.add_paragraph(
        "I defend t = 0.35 as the optimal operational threshold based on four empirical metrics: (1) Demographic Parity = 0.9292 (Female approval 84.71%, Male approval 91.16%), satisfying the EEOC 80% rule; (2) Equalized Odds = 0.8108, with true positive parity at 0.9769 (TPR_Female = 93.22% vs. TPR_Male = 95.42%); (3) Predictive Parity = 1.0255 (PPV_Female = 76.39% vs. PPV_Male = 74.49%); and (4) Accuracy = 74.00% (only 2.33% below peak 76.33% at t=0.55). Strongest Counter-Argument: A credit officer will argue that t=0.35 elevates the False Positive Rate to 65.38% for women and 80.65% for men, approving 67 defaulting applicants in a 5:1 cost matrix. This valid credit risk must be managed via risk-adjusted loan pricing and tiered borrowing caps rather than demographic exclusion."
    )

    doc.add_page_break()

    # --- PART 3: Q8 & PART 4 ---
    add_sec_head("Part 3 (Cont.) — Question 8 & Part 4 Reflection Essay")

    add_sub_head("Question 8: Strategic Policy Choice: Demographic Parity vs. Equalized Odds")
    doc.add_paragraph(
        "If forced to choose, I unequivocally recommend prioritizing Equalized Odds (EO) over pure Demographic Parity (DP). Under Kleinberg’s Impossibility Theorem, unequal base rates (Female 69.41% vs. Male 71.16%) make DP, EO, and PP mutually incompatible. Equalized Odds enforces meritocratic fairness: creditworthy applicants face equal approval odds regardless of sex (at t=0.35, TPR_Female = 93.22% vs. TPR_Male = 95.42%, a 2.20% gap), while preserving Predictive Parity (PP = 1.0255). We explicitly sacrifice strict DP (0.9292 at t=0.35; 0.8480 at t=0.55). Sacrificing pure DP is necessary: enforcing equal acceptance rates across unequal financial distributions would force banks to approve unqualified women (causing debt traps and default) or deny qualified men, violating procedural justice."
    )

    add_sec_head("Part 4 — Reflection Essay (~500 words)")
    doc.add_paragraph(
        '"If a policy-maker asked you: \'just give me one number: should we deploy this model or not?\', what would you say, '
        'and what is the limitation of that \'one number\' answer that you discovered yourself through your analysis?"'
    )

    add_sub_head("1. Direct Answer (1–2 sentences)")
    doc.add_paragraph(
        "I would recommend conditional deployment under strict segment-specific thresholding (t = 0.35) and continuous human-in-the-loop oversight, "
        "because a single binary deployment number obscures that default thresholding maximizes global accuracy while destroying equal opportunity for female borrowers and failing predictably on high-exposure homeowners."
    )

    add_sub_head("2. Why a Single Number Fails (300–400 words)")
    doc.add_paragraph(
        "The fundamental lesson of this stress-test audit is that reducing a sociotechnical AI system to a single summary metric—whether overall accuracy (75.33%), AUC-ROC (0.792), or a composite index—is an act of intellectual complacency that conceals severe structural trade-offs.\n\n"
        "First, aggregate accuracy systematically masks catastrophic subgroup collapses. At our model’s peak accuracy threshold of t = 0.55 (76.33% accuracy), Equalized Odds collapses to a dismal 0.5156, with the model approving non-creditworthy men at nearly double the rate of non-creditworthy women (FPR_Male = 59.68% vs. FPR_Female = 30.77%), while female loan approvals plunge to 68.24%. Celebrating '76% accuracy' ignores that half of the equal opportunity metric has been eliminated.\n\n"
        "Second, threshold selection is an unstated value judgment, not a mathematical fact. Choosing between t = 0.35 (prioritizing inclusion and EO of 0.8108) and t = 0.55 (prioritizing default suppression and bank profitability) cannot be answered by data science. It is an economic and political choice balancing borrower credit access against institutional capital loss. Collapsing this to a binary 'deploy' command abdicates human accountability to an arbitrary mathematical default (0.50).\n\n"
        "Third, fairness metrics are mathematically adversarial. Under Kleinberg's and Chouldechova's theorems, differing base default rates (69.41% female vs. 71.16% male) ensure that Demographic Parity, Equalized Odds, and Predictive Parity cannot be simultaneously fulfilled. Gaining +4.27% in DP from t=0.75 to t=0.85 causes EO to plunge -24.99%—a punishing trade-off cost ratio of 5.85. A single metric conceals which protected group is paying the cost.\n\n"
        "Fourth, models fail with extreme confidence on predictable adversarial clusters. Our model confidently misclassified 24 test cases (8.00%), assigning P_hat >= 0.75 to defaulting applicants simply because they were homeowners (83.33%) with moderate checking reserves (45.83%), oblivious to their heavy 3,337.50 DM debt burden.\n\n"
        "Finally, hidden confounds remain invisible to summary statistics. Purging checking liquidity caused savings weights to inflate by +110.00% and employment weights by +100.31%, proving that observational models readily disguise omitted confounders as legitimate risk indicators."
    )

    add_sub_head("3. Grounding in Evidence (50–100 words)")
    doc.add_paragraph(
        "Our computations substantiate every limitation: the 30.00% mismatch between Model A and B, the Simpson’s sign reversal on existing credits (-0.2203 young vs. +0.3083 mature), the 110.00% coefficient inflation under omitted-variable testing, the 24 adversarial failures with 83.33% homeownership, and the plunge in Equalized Odds from 0.8108 at t=0.35 to 0.5156 at t=0.55."
    )

    add_sub_head("4. Closing (50 words)")
    doc.add_paragraph(
        "Responsible AI governance is an exercise in transparently navigating unavoidable trade-offs, not chasing single-metric optimization. A single number offers executives the illusion of certainty; true algorithmic accountability demands exposing who wins, who loses, and which ethical values are compromised at every operational threshold."
    )

    # Save to compact file
    compact_path = "Assignment1_Report_s24bcau0154_6pages.docx"
    doc.save(compact_path)
    print(f"Saved: {compact_path}")
    
    # Also try saving to main docx if not locked
    main_path = "Assignment1_Report_s24bcau0154.docx"
    try:
        doc.save(main_path)
        print(f"Saved: {main_path}")
    except PermissionError:
        print(f"Note: {main_path} is currently open in Word/another program. The compact 6-page version is saved at {compact_path}!")

if __name__ == "__main__":
    create_compact_docx()
