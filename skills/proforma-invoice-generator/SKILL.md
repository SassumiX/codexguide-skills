---
name: proforma-invoice-generator
description: 杭州碧图进出口有限公司（Hangzhou Betrue Import & Export Co. Ltd）Proforma Invoice 在线生成器。当用户需要生成外贸形式发票（P/I）、发送报价单、创建 Proforma Invoice 时激活。支持填写买家信息、商品明细、HS Code、成交条款、银行账户信息，输出 HTML/PDF 文件和可分享预览链接。
---

# Proforma Invoice Generator

Generate professional Proforma Invoices (P/I) for Hangzhou Betrue Import & Export Co. Ltd.

## File Structure

```
proforma-invoice-generator/
├── SKILL.md                               ← 技能入口
├── scripts/
│   └── proforma_invoice_generator.py     ← 生成器脚本
└── assets/
    └── proforma-invoice-template.html    ← HTML 模板
```

## Workflow

**Step 1 — Collect order data**

Ask the user for:
- P/I number (or auto-generate: `BTU` + YYYYMMDD)
- Buyer info: name, address, email, VAT/Tax ID
- Destination port & Incoterm (EXW/FOB/CIF/etc.)
- Payment terms (T/T, L/C, etc.)
- Goods list: article name, HS code, qty, unit, unit price

If user sends a PDF/Word/Excel with order info → extract it first.

**Step 2 — Render the invoice**

Run the generator script from the skill directory:

```bash
cd /workspace/skills/proforma-invoice-generator
python3 scripts/proforma_invoice_generator.py --json /tmp/order.json
```

Order data JSON format:

```json
{
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
    {"article": "UNITREE ROBOT (G1 EDU)", "hs_code": "85437099", "qty": 1, "unit": "SET", "unit_price": 21667.00, "amount": 21667.00}
  ],
  "currency": "EUR",
  "service_fee_rate": 5,
  "payment_method": "Telegraphic Transfer (T/T)",
  "payment_terms_detail": "100% prepaid before shipment.",
  "lead_time": "30-45 days after payment confirmation",
  "incoterm_detail": "EXW Yiwu. Buyer arranges freight and insurance.",
  "packaging": "Standard export packaging",
  "inspection": "Self-inspection by manufacturer / SGS at buyer's request",
  "shipping_mark": "As per buyer's instruction",
  "insurance": "Covered by buyer",
  "quality_std": "GB/T / ISO 9001 or buyer's standard",
  "remarks": "Buyer's VAT/Tax ID to be provided if required for customs.",
  "beneficiary_bank": "AGRICULTURAL BANK OF CHINA, ZHEJIANG BRANCH, HANGZHOU ZHEDA SUB-BRANCH",
  "bank_address": "NO. 743 SHENHUA ROAD, HANGZHOU, ZHEJIANG, CHINA",
  "bank_tel": "86-0571-85235554",
  "swift_code": "ABOCCNBJ110",
  "cnaps": "103331004258",
  "account_no": "19042538040000548"
}
```

**Step 3 — Deploy for sharing**

Use `mcp_matrix_deploy` tool to deploy the output dir and get a shareable link:

```bash
# Deploy /workspace/proforma-invoice/output/ as a website
# Returns a public URL like https://xxxx.space.minimaxi.com/PROFORMA_INVOICE_xxx.html
```

**Step 4 — Deliver to user**
Send the CDN URL or file path to David.

## Bank Info (pre-filled)

```
Beneficiary: HANGZHOU BETRUE IMPORT & EXPORT CO., LTD
Bank: AGRICULTURAL BANK OF CHINA, ZHEJIANG BRANCH, HANGZHOU ZHEDA SUB-BRANCH
SWIFT: ABOCCNBJ110
EUR A/C: 19042538040000548
USD A/C: 19042514040001794
CNAPS: 103331004258
```

## Company Info (pre-filled)

```
HANGZHOU BETRUE IMPORT & EXPORT CO., LTD
1-213, Qunlian Comprehensive Building, Sandun Town, Westlake District, Hangzhou, P.R. CHINA
Tel: +86 186 0588 1846 | Email: factorihub@outlook.com
```