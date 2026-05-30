---
name: douyin-summary
description: 抖音视频总结助手。当用户提供抖音视频链接时，自动调用此技能获取文案并总结。
---
# 抖音视频总结助手

## 工作流程
1. 识别用户输入中的douyin.com链接
2. 调用scripts/fetch_douyin.py获取视频文案
3. 提取核心观点并结构化输出

## 触发条件
用户发送带 douyin.com 链接的消息时触发。
