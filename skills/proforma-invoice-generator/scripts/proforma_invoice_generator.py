#!/usr/bin/env python3
"""
proforma_invoice_generator.py
生成杭州碧图进出口有限公司 Proforma Invoice (HTML + PDF)
"""
import sys, os, json, re
from datetime import datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(SKILL_DIR, "assets", "proforma-invoice-template.html")
OUTPUT_DIR = "/workspace/proforma-invoice/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def format_number(n, decimals=2):
    if n is None: return "0.00"
    return f"{float(n):,.{decimals}f}"

def num_to_words(n, currency="EUR"):
    units = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE",
             "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN",
             "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
    tens = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
    def _words(x):
        if x < 20: return units[x]
        if x < 100: return (tens[x//10] + ("-" + units[x%10] if x%10 else ""))
        if x < 1000: return _words(x//100) + " HUNDRED " + _words(x%100)
        if x < 1000000: return _words(x//1000) + " THOUSAND " + _words(x%1000)
        return str(x)
    whole = int(n)
    cents = int(round((n - whole) * 100))
    words = _words(whole)
    return f"{words} {currency} {'AND ' + str(cents) + '/100' if cents else 'ONLY'}"

def compute_totals(goods, service_fee_rate=5, other_fee=0, other_fee_label=""):
    subtotal = sum(float(g.get("amount", 0)) for g in goods)
    service_fee = subtotal * service_fee_rate / 100 if service_fee_rate else 0
    grand_total = subtotal + service_fee + other_fee
    return subtotal, service_fee, grand_total

def render_template(template_path, data):
    with open(template_path, encoding="utf-8") as f:
        tpl = f.read()
    def process_conditionals(text, data):
        def _ifcond(m):
            key = m.group(1)
            inside = m.group(2)
            if data.get(key.strip()):
                return inside
            return ""
        return re.sub(r'\{\{#if\s+(\S+?)\}\}(.*?)\{\{/if\}\}', _ifcond, text, flags=re.DOTALL)
    def process_loops(text, data):
        def _each(m):
            key = m.group(1)
            inside = m.group(2)
            items = data.get(key.strip(), [])
            out = ""
            for i, item in enumerate(items):
                row = inside
                row = re.sub(r'\{\{add @index 1\}\}', str(i+1), row)
                row = re.sub(r'\{\{(\w+)\}\}', lambda m2: str(item.get(m2.group(1), "")), row)
                row = re.sub(r'\{\{format_number\s+(\S+?)\}\}',
                             lambda m2: format_number(item.get(m2.group(1), 0)), row)
                out += row
            return out
        return re.sub(r'\{\{#each\s+(\S+?)\}\}(.*?)\{\{/each\}\}', _each, text, flags=re.DOTALL)
    def _top(m):
        key = m.group(1)
        if key.startswith("format_number "):
            return format_number(data.get(key.split()[1], 0))
        return str(data.get(key, ""))
    tpl = process_conditionals(tpl, data)
    tpl = process_loops(tpl, data)
    tpl = re.sub(r'\{\{(\S+?)\}\}', _top, tpl)
    return tpl

SAMPLE_DATA = {
    "pi_number": "2026BTU",
    "issue_date": "2026-05-30",
    "valid_until": "2026-06-30",
    "ref_number": "202618001",
    "buyer_name": "Dr Tiens Company",
    "buyer_address": "Sofia, Bulgaria",
    "buyer_contact": "Dr. Tien",
    "buyer_email": "dr.lulutien@gmail.com",
    "buyer_tel": "",
    "buyer_vat": "TO BE PROVIDED",
    "destination_port": "Sofia, Bulgaria",
    "final_destination": "Sofia, Bulgaria",
    "incoterm": "EXW Yiwu",
    "loading_port": "Yiwu / Shanghai, China",
    "payment_terms": "T/T 100% Prepaid",
    "expected_shipment": "Within 45 days after payment",
    "goods": [
        {"article": "UNITREE ROBOT (G1 EDU)", "hs_code": "85437099", "qty": 1, "unit": "SET", "unit_price": 21667.00, "amount": 21667.00},
        {"article": "MASSAGE ROBOT (Single-arm)", "hs_code": "90191010", "qty": 1, "unit": "SET", "unit_price": 12820.00, "amount": 12820.00},
        {"article": "OXYGEN CABIN", "hs_code": "9403200000", "qty": 1, "unit": "SET", "unit_price": 24616.00, "amount": 24616.00},
        {"article": "AI DIAGNOSTIC INSTRUMENT", "hs_code": "90189099", "qty": 1, "unit": "SET", "unit_price": 1412.00, "amount": 1412.00},
        {"article": "DIATHERMY DEVICE", "hs_code": "90189099", "qty": 1, "unit": "SET", "unit_price": 2052.00, "amount": 2052.00},
        {"article": "BRAIN HEALTH DEVICE", "hs_code": "90189099", "qty": 1, "unit": "SET", "unit_price": 1283.00, "amount": 1283.00},
        {"article": "BEAUTY INSTRUMENT", "hs_code": "90189099", "qty": 1, "unit": "SET", "unit_price": 1303.00, "amount": 1303.00},
        {"article": "MASSAGE BED & ACCESSORIES", "hs_code": "94029000", "qty": 1, "unit": "SET", "unit_price": 1263.00, "amount": 1263.00},
    ],
    "currency": "EUR",
    "service_fee_rate": 5,
    "payment_method": "Telegraphic Transfer (T/T)",
    "payment_terms_detail": "100% prepaid before shipment. Buyer should ensure seller receives the full invoice amount.",
    "lead_time": "30-45 days after payment confirmation",
    "incoterm_detail": "EXW Yiwu. Buyer arranges freight and insurance.",
    "packaging": "Standard export packaging",
    "inspection": "Self-inspection by manufacturer / SGS at buyer's request",
    "shipping_mark": "As per buyer's instruction",
    "insurance": "Covered by buyer",
    "quality_std": "GB/T / ISO 9001 or buyer's standard",
    "remarks": "Buyer's VAT/Tax ID to be provided if required for customs or payment.",
    "beneficiary_bank": "AGRICULTURAL BANK OF CHINA, ZHEJIANG BRANCH, HANGZHOU ZHEDA SUB-BRANCH",
    "bank_address": "NO. 743 SHENHUA ROAD, HANGZHOU, ZHEJIANG, CHINA",
    "bank_tel": "86-0571-85235554",
    "swift_code": "ABOCCNBJ110",
    "cnaps": "103331004258",
    "account_no": "19042538040000548",
}

def main():
    if len(sys.argv) < 2 or "--sample" in sys.argv:
        data = SAMPLE_DATA.copy()
        fname = "PROFORMA_INVOICE_" + data["pi_number"] + ".html"
    elif sys.argv[1] == "--json":
        with open(sys.argv[2], encoding="utf-8") as f:
            data = json.load(f)
        fname = "PROFORMA_INVOICE_" + data.get("pi_number", "BTU") + ".html"
    else:
        print("Usage: python proforma_invoice_generator.py [--sample|--json data.json]")
        sys.exit(1)

    subtotal, service_fee, grand_total = compute_totals(
        data["goods"], data.get("service_fee_rate", 0), data.get("other_fee", 0)
    )
    data["subtotal"] = subtotal
    data["service_fee"] = service_fee
    data["grand_total"] = grand_total
    data["total_in_words"] = num_to_words(grand_total, data.get("currency", "EUR"))

    html = render_template(TEMPLATE_PATH, data)
    html_path = os.path.join(OUTPUT_DIR, fname)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML: {html_path}")

    pdf_path = html_path.replace(".html", ".pdf")
    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(pdf_path)
        print(f"PDF: {pdf_path}")
    except Exception as e:
        print(f"PDF generation skipped: {e}")

if __name__ == "__main__":
    main()