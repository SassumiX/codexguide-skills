---
name: agentic-inbox
description: QQ邮箱 AI 收件箱 — IMAP读取 + AI分类 + 微信推送。每小时自动检查新邮件，只推送重要邮件，过滤系统退信。当用户说"AI收件箱"、"检查邮件"、"有新邮件吗"时激活。
category: productivity
tags: [imap, email, qq邮箱, 微信推送, 自动化, 外贸]
trigger:
  - AI收件箱
  - 检查邮件
  - 有新邮件吗
  - agentic inbox
  - 收件箱
---

# Agentic Inbox — AI 收件箱

## 技能说明
QQ 邮箱 AI 收件箱，通过 IMAP 每小时自动读取新邮件 → AI 分类 → 微信推送。
- 只推送 **🔴 高优先级**邮件（客户询价、geodinvest 转发）
- **⚪ 系统退信** 自动过滤，不打扰
- **🟡 一般邮件** 最多列出 3 封摘要

## 系统架构
```
contact@geodinvest.com（企业邮箱发件）
        ↓ (Wix DNS 转发)
1210175824@qq.com（收件主邮箱）
        ↓ (IMAP 每小时读取)
AI 分类 + 摘要提取
        ↓ (微信推送)
David
```

## 前置条件
1. contact@geodinvest.com 已配置转发到 1210175824@qq.com
2. QQ 邮箱开启 IMAP 服务（设置 → 账户 → 开启 IMAP/SMTP）
3. 已生成 QQ 邮箱授权码

## 快速使用

### 手动触发
```
cd /workspace/agentic_inbox && python3 agentic_inbox.py
```

### 查看运行日志
```
tail -50 /workspace/agentic_inbox/log.json
```

### 查看当前状态
```
cat /workspace/agentic_inbox/state.json
```

## 核心文件

| 文件 | 作用 |
|------|------|
| `agentic_inbox.py` | 主程序（IMAP 读取 → 分类 → 推送） |
| `state.json` | 已处理邮件 ID 列表（防重） |
| `log.json` | 运行日志 |

## Cron Job 配置

已设置每小时整点自动推送：
- **Job ID**: `2aec5a10600c`
- **触发时间**: `0 * * * *`（每小时的第 0 分钟）
- **推送目标**: 微信 o9cq80xFn15ACGxHA1JpQbsca-5M@im.wechat

### 管理 Cron Job
```bash
# 查看任务
/cronjob list

# 暂停
/cronjob pause 2aec5a10600c

# 恢复
/cronjob resume 2aec5a10600c

# 立即触发一次
/cronjob run 2aec5a10600c
```

## 邮件分类规则

### 🔴 高优先级（推送）
- 发件人含 `geodinvest` / `contact@geodinvest`
- 主题/正文含询价关键词：inquiry, 询价, quote, price, interested, 合作, 样品, order, purchase
- 重要客户名：david, zhao david, 顾伟强, 吴伟, 张玉文, william
- 真实客户回复（含"RE:"的回复）

### ⚪ 系统通知（过滤不推送）
- Undeliverable / Mailer-Daemon / Delivery Status Notification
- 自动退信（中文/葡文/英文）
- DMARC / SPF 验证失败
- Newsletter / 营销邮件

### 🟡 一般邮件（摘要推送，最多3封）
- 普通商务往来

## 配置参数
> ⚠️ 敏感信息已写入脚本，勿外传

| 参数 | 当前值 |
|------|--------|
| IMAP 主机 | imap.qq.com |
| IMAP 端口 | 993 |
| 邮箱账号 | 1210175824@qq.com |
| 授权码 | `kxjyhcrnuethjchi` |

如需修改授权码，直接编辑 `agentic_inbox.py` 第 23 行 `AUTH_CODE`。

## 故障排除

### 脚本报错 "Expecting value"
**原因**: state.json 损坏（被 bytes 类型污染）
```bash
echo '{"seen_ids":[],"last_run":null}' > /workspace/agentic_inbox/state.json
```

### 推送重复
**原因**: seen_ids 中有重复
```bash
echo '{"seen_ids":[],"last_run":null}' > /workspace/agentic_inbox/state.json
```
会重新读取最近 15 封邮件，请确认是否有重复。

### IMAP 超时
**原因**: 网络抖动或 QQ 服务器限流
```bash
cd /workspace/agentic_inbox && python3 agentic_inbox.py
```
稍后重试，或检查是否触发了 QQ 安全登录拦截。

### 微信推送失败（errcode:-3 / errcode:-2）
**原因**: 微信会话未建立连接
- errcode:-3 = 连接未建立，需对方扫码激活
- errcode:-2 = 会话过期，需重新发起

**解决**: 无法主动建立，只能由客户侧扫码激活。

### 日志显示 "最近3天共 0 封邮件"
**原因**: 最近无新邮件（完全正常！）
- 确认 QQ 邮箱确实收到了转发邮件
- 检查 1210175824@qq.com 是否开启了 contact@ 的转发

## 踩坑记录
1. **Gmail IMAP 连不上**（超时）→ 改用 QQ 邮箱方案
2. **contact@geodinvest.com 是 Google Workspace** → MX = aspmx.l.google.com，需 App Password
3. **Wix 企业邮箱** → 收费套餐才能 IMAP，改用 DNS 转发到 QQ 邮箱
4. **state.json 被 bytes 污染** → 已修复，确保所有 ID 都是字符串
5. **QQ 邮箱安全拦截** → 每次登录需滑动验证，建议用授权码而非密码