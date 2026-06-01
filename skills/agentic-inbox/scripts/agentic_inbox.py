#!/usr/bin/env python3
"""
AI 收件箱 - Agentic Inbox v2
读取 1210175824@qq.com → AI总结 → 微信推送
"""

import imaplib
import ssl
import time
import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from email.header import decode_header
from email import policy
from email.parser import BytesParser

# ===== 配置 =====
IMAP_HOST = 'imap.qq.com'
IMAP_PORT = 993
EMAIL = '1210175824@qq.com'
AUTH_CODE = 'kxjyhcrnuethjchi'  # ⚠️ 如需修改，替换此处
STATE_FILE = '/workspace/agentic_inbox/state.json'
LOG_FILE = '/workspace/agentic_inbox/log.json'

# ===== 工具函数 =====
def decode_str(raw):
    if not raw:
        return ''
    parts = decode_header(raw)
    result = ''
    for part, enc in parts:
        if isinstance(part, bytes):
            result += part.decode(enc or 'utf-8', errors='replace')
        elif isinstance(part, str):
            result += part
    return result

def get_body(msg):
    """提取邮件正文（处理多格式）"""
    body = ''
    try:
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == 'text/plain' and not body:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='replace')
                    break
                elif ct == 'text/html' and not body:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='replace')
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='replace')
    except:
        pass

    body = re.sub(r'<style[^>]*>.*?</style>', ' ', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'&nbsp;', ' ', body)
    body = re.sub(r'&amp;', '&', body)
    body = re.sub(r'&lt;', '<', body)
    body = re.sub(r'&gt;', '>', body)
    body = re.sub(r'\s+', ' ', body).strip()
    return body[:1500]

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                raw = f.read().strip()
                if raw:
                    return json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            pass
    return {'seen_ids': [], 'last_run': None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# ===== 邮件分类 =====
def classify_email(from_addr, subject, body_preview):
    from_lower = from_addr.lower()
    subject_lower = subject.lower()
    body_lower = body_preview.lower()
    combined = from_lower + ' ' + subject_lower + ' ' + body_lower

    geo_keywords = ['geodinvest', 'contact@geodinvest', 'geodinves', 'geod invest']
    inquiry_keywords = ['inquiry', '询价', 'quote', 'price', 'interested', '合作', '业务',
                        'order', 'purchase', 'buy', '样品', '报价', 'contact us',
                        'your product', 'your company', 'building material',
                        'ecopa', 'construction']
    system_keywords = ['undeliverable', 'mailer-daemon', 'postmaster', 'failure',
                       'delivery status', '自动退信', '无法送达', 'noreply',
                       'no-reply', 'newsletter', 'dmarc', 'spf', 'unsubscribe', '退订', '营销邮件']
    system_patterns = ['undeliverable', 'mailer-daemon', 'postmaster',
                       'delivery status notification', 'failure',
                       '自动退信', '无法送达', 'dmarc', 'spf', 'resposta automática',
                       'retorno ao remetente', 'returned mail']

    for pattern in system_patterns:
        if pattern in subject_lower:
            return '⚪ 系统通知'

    for kw in geo_keywords:
        if kw in from_lower:
            return '🔴 高优先级'

    for kw in inquiry_keywords:
        if kw in combined:
            return '🔴 高优先级'

    for kw in system_keywords:
        if kw in combined:
            return '⚪ 系统通知'

    return '🟡 一般邮件'

# ===== 主程序 =====
def main():
    print(f"\n{'='*50}")
    print(f"🤖 AI 收件箱启动 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    state = load_state()

    try:
        log("连接QQ邮箱 IMAP...")
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=25)
        mail.login(EMAIL, AUTH_CODE)
        log("✅ 已登录")

        mail.select('INBOX')

        since_date = (datetime.now() - timedelta(days=3)).strftime('%d-%b-%Y')
        status, all_ids = mail.search(None, f'SINCE {since_date}')
        ids = all_ids[0].split() if all_ids[0] else []
        log(f"📥 最近3天共 {len(ids)} 封邮件")

        new_emails = []
        recent_ids = list(reversed(ids[-15:]))

        for uid in recent_ids:
            uid_str = uid.decode() if isinstance(uid, bytes) else uid

            if uid_str in state.get('seen_ids', []):
                continue

            try:
                status, msg_data = mail.fetch(uid, '(RFC822)')
                if not (msg_data and msg_data[0] and isinstance(msg_data[0], tuple)):
                    continue

                raw_email = msg_data[0][1]
                msg = BytesParser(policy=policy.default).parsebytes(raw_email)

                from_addr = decode_str(msg['From']) or ''
                subject = decode_str(msg['Subject']) or '(无主题)'
                date_str = msg['Date'] or ''
                msg_id = msg['Message-ID'] or uid_str

                body = get_body(msg)
                category = classify_email(from_addr, subject, body)

                from_match = re.search(r'([^<]+?)\s*<', from_addr)
                sender_name = from_match.group(1).strip() if from_match else from_addr[:40]

                email_data = {
                    'uid': uid_str,
                    'msg_id': msg_id,
                    'from': from_addr,
                    'sender': sender_name,
                    'subject': subject,
                    'date': date_str,
                    'category': category,
                    'body': body[:800],
                    'timestamp': datetime.now().isoformat(),
                }

                new_emails.append(email_data)
                log(f"  {category} | {subject[:60]}")

            except Exception as e:
                log(f"  Error: {e}")

        mail.logout()

        important = [e for e in new_emails if e['category'] == '🔴 高优先级']
        others = [e for e in new_emails if e['category'] == '🟡 一般邮件']

        print(f"\n📊 分类结果：")
        print(f"  🔴 高优先级: {len(important)} 封")
        print(f"  🟡 一般邮件: {len(others)} 封")

        # 确保所有ID都是字符串，防 JSON 序列化失败
        seen_ids_list = [uid.decode() if isinstance(uid, bytes) else uid for uid in ids]
        new_ids_clean = [s for s in seen_ids_list if isinstance(s, str)]
        existing_ids_clean = [s for s in state.get('seen_ids', []) if isinstance(s, str)]
        combined = list(dict.fromkeys(new_ids_clean + existing_ids_clean))[:200]
        seen_ids = [s for s in combined if isinstance(s, str)][:200]

        state['seen_ids'] = seen_ids
        state['last_run'] = datetime.now().isoformat()
        save_state(state)

        if not new_emails:
            print("\n📭 无新邮件")
            return None

        lines = [f"📬 AI 收件箱 · {datetime.now().strftime('%H:%M')}"]
        lines.append("─" * 40)

        if important:
            lines.append(f"🔴 重要邮件 ({len(important)}封)")
            for e in important:
                date_short = e['date'][:16] if len(e['date']) > 16 else e['date']
                lines.append(f"\n📩 {e['sender']}")
                lines.append(f"   主题: {e['subject'][:70]}")
                lines.append(f"   {date_short}")
                body = e['body'][:200].strip()
                if body:
                    lines.append(f"   摘要: {body}...")

        if others:
            lines.append(f"\n🟡 一般邮件 ({len(others)}封)")
            for e in others[:3]:
                lines.append(f"• {e['subject'][:60]}")
            if len(others) > 3:
                lines.append(f"  ... 还有{len(others)-3}封")

        message = '\n'.join(lines)
        print(f"\n📤 推送内容：\n{message}")

        return {
            'new_emails': new_emails,
            'important': important,
            'message': message
        }

    except Exception as e:
        log(f"❌ 主程序错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = main()
    if result:
        print(f"\n✅ 完成 - {len(result['new_emails'])}封新邮件")