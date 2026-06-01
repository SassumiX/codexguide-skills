# agentic-inbox 配置参考

## 当前配置值

| 参数 | 值 | 说明 |
|------|----|------|
| `IMAP_HOST` | `imap.qq.com` | QQ 邮箱 IMAP 服务器 |
| `IMAP_PORT` | `993` | SSL 连接端口 |
| `EMAIL` | `1210175824@qq.com` | 收件主邮箱 |
| `AUTH_CODE` | `kxjyhcrnuethjchi` | QQ 邮箱授权码（非密码） |
| `STATE_FILE` | `/workspace/agentic_inbox/state.json` | 已读邮件状态文件 |
| `LOG_FILE` | `/workspace/agentic_inbox/log.json` | 运行日志 |

## 修改 AUTH_CODE（授权码）

QQ 邮箱授权码获取路径：
1. 登录 mail.qq.com
2. 设置 → 账户
3. POP3/IMAP/SMTP/Exchange/CardDAEM/CalDAV服务
4. 开启 **IMAP/SMTP服务**
5. 点击"生成授权码"（需手机验证）
6. 替换 `scripts/agentic_inbox.py` 第 22 行

⚠️ **不要用 QQ 密码**，必须用授权码。

## 切换其他邮箱

如需改用其他邮箱（如 163、Gmail），修改 `scripts/agentic_inbox.py` 顶部配置：

### 163 邮箱
```python
IMAP_HOST = 'imap.163.com'
IMAP_PORT = 993
EMAIL = 'your_email@163.com'
AUTH_CODE = '你的163授权码'
```

### Gmail
```python
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = 'your_email@gmail.com'
AUTH_CODE = '你的Gmail应用专用密码'
```
> ⚠️ Gmail 在国内可能超时，建议用 QQ 邮箱或 163 邮箱方案。

## 分类规则调优

编辑 `scripts/agentic_inbox.py` 第 94–141 行的 `classify_email()` 函数：

### 添加重要客户
在 `important_names` 列表添加：
```python
important_names = ['david', 'zhao david', '顾伟强', '吴伟', '张玉文', 'william', '新客户名']
```

### 添加询价关键词
在 `inquiry_keywords` 添加：
```python
'inquiry', '询价', ... , '你的关键词'
```

### 添加过滤关键词
在 `system_keywords` 添加：
```python
'undeliverable', ... , '你的过滤词'
```

## 推送目标变更

如需改推其他微信账号，修改 Cron Job 的 `deliver` 参数：
```
/cronjob update 2aec5a10600c deliver:platform:chat_id
```

## 调整扫描时间范围

默认扫描最近 **3 天**，如需修改：
```python
since_date = (datetime.now() - timedelta(days=3)).strftime('%d-%b-%Y')
```
改为 `days=1`（1天）或 `days=7`（7天）。