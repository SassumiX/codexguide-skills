---
name: geodinvest-email-signature
description: Geodinvest / ECOPA 外贸开发信英文签名生成技能。触发条件：需要生成外贸客户开发签名时激活。
triggers:
  - 生成签名
  - email signature
  - geodinvest 签名
---

# ⚠️ 强制规则：发邮件前必须先加载本技能

> **2026-06-01 教训：发送任何 Geodinvest 外贸邮件前，必须先 `skill_view("geodinvest-email-signature")` 加载本技能，确认使用正确签名格式。禁止手搓签名或跳过本技能。**

---

# Geodinvest 邮件签名生成技能

## 签名内容（英文版·2026-06-01 修正）

**注意：bullet 必须使用 `•`（圆点），禁止使用 Unicode 特殊符号如 `▸` `&#9655;` `&#9658;`，会导致邮件客户端显示乱码！**

```html
David Zhao<br>
Business Development | <a href="https://www.geodinvest.com">Geodinvest</a><br>
HANGZHOU BETRUE IMPORT AND EXPORT CO., LTD<br><br>
&#x1F33F; <a href="https://n28cyp23x414.space.minimaxi.com/">ECOPA</a> Green Building Materials<br>
&#x1F3E0; Est. 2006 | 18+ Years in China-Europe<br><br>
• <a href="https://n28cyp23x414.space.minimaxi.com/">Global Supply</a><br>
• <a href="https://n28cyp23x414.space.minimaxi.com/">European Project Cooperation</a><br>
• <a href="https://n28cyp23x414.space.minimaxi.com/">China-Europe Cross-Border Supply Chain</a><br><br>
&#x1F4F1; WhatsApp: +86 186 0588 1846<br>
&#x1F310; <a href="https://www.geodinvest.com">www.geodinvest.com</a><br>
&#x1F4C2; <a href="https://geodinvest.wixel.com/a7a84645-00b8-4293-9141-311ac3a8863d">View Full Catalogue &#8594;</a>
```

**CATALOGUE_LINK（落地页）:** `https://n28cyp23x414.space.minimaxi.com/`（2026-05-28 确认，直接落地页地址）

## 使用方法

直接复制上方 HTML 内容拼接到邮件正文中。

## 注意事项 / 陷阱

1. **Bullet 只能用 `•`** —— 历史教训：2026-06-01 曾使用 `▸` `&#9655;` `&#9658;`，在 QQ/网易邮箱显示为乱码 "陕"，切记切记！
2. **ECOPA 链接用落地页** `https://n28cyp23x414.space.minimaxi.com/`，不要再用旧链接
3. **Catalogue 链接**用 WIX 生成的目录链接：`https://geodinvest.wixel.com/a7a84645-00b8-4293-9141-311ac3a8863d`

## 已使用此签名的文件（勿直接修改，用 Skill 里的版本统一更新）

- `/workspace/clients/geodinvest_daily_send.py`
- `/workspace/clients/retry_failed301_400.py`
- `/workspace/clients/send_rows301_400.py`
- `/workspace/signature_email.html`

更新签名时，同步更新上述所有文件。

## 🔗 链接更新规范（2026-06-03 教训）

批量替换链接时，必须执行 **三轮验证**：

1. **旧链接残留** — `grep -r "旧URL"` 全量检查
2. **新链接覆盖** — `grep -r "新URL"` 确认覆盖文件数
3. **尾部斜杠** — `grep "新URL_without_slash">` 专门检查是否有 `">` 结尾的漏网之鱼

> ⚠️ 教训：ECOPA 链接从 `nwn3f51fjzkx` 换到 `n28cyp23x414` 时，已更新的文件里 `">` 结尾漏加 `/` 导致链接打不开。自动化 replace 只替换了文本，没有验证 URL 完整性。
>
> 每次链接更新后，**必须检查文件中是否有 `xxx.space.minimaxi.com">`（缺尾部 `/`）的模式**，手动补全。