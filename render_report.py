import base64
import os
from playwright.sync_api import sync_playwright

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')

fig1_b64 = get_base64_image("figures/part1_model_comparison.png")
fig2_b64 = get_base64_image("figures/part2_1_simpsons_paradox.png")
fig3_b64 = get_base64_image("figures/part2_2_ovb_shifts.png")
fig4_b64 = get_base64_image("figures/part2_3_adversarial_subset.png")
fig5_b64 = get_base64_image("figures/part2_4_fairness_tradeoff.png")

# Read template
with open("report_template.html", "r", encoding="utf-8") as f:
    template = f.read()

# Replace placeholders
final_html = template.replace("{{FIG1}}", fig1_b64)
final_html = final_html.replace("{{FIG2}}", fig2_b64)
final_html = final_html.replace("{{FIG3}}", fig3_b64)
final_html = final_html.replace("{{FIG4}}", fig4_b64)
final_html = final_html.replace("{{FIG5}}", fig5_b64)

with open("report.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Generated report.html successfully. Now rendering to PDF via Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('report.html').replace(os.sep, '/')}")
    page.pdf(
        path="Assignment1_Report_s24bcau0154.pdf",
        format="A4",
        print_background=True,
        margin={
            "top": "15mm",
            "bottom": "15mm",
            "left": "14mm",
            "right": "14mm"
        }
    )
    browser.close()

print("Assignment1_Report_s24bcau0154.pdf generated successfully!")
