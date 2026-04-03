import re

from rest_framework import serializers


PROHIBITED_KEYWORDS = [
    '加微信',
    'vx',
    'v信',
    '联系方式',
    '代购',
    '刷单',
    '返利',
    '代理',
    '赌博',
    '色情',
    '辱骂',
    '骗子',
    '包治百病',
    '百分百治愈',
]


NORMALIZED_KEYWORDS = {keyword.lower() for keyword in PROHIBITED_KEYWORDS}


def find_prohibited_keywords(*parts):
    text = ' '.join(part for part in parts if part)
    normalized = re.sub(r'\s+', '', text).lower()
    matched = [keyword for keyword in NORMALIZED_KEYWORDS if keyword in normalized]
    return sorted(set(matched))


def validate_clean_content(*parts):
    matched = find_prohibited_keywords(*parts)
    if matched:
        raise serializers.ValidationError(
            f"内容包含疑似违规关键词：{', '.join(matched[:5])}，请修改后再提交"
        )
