MATCH_MODE_OPTIONS = [
    {'value': 'experts', 'api_value': 'expert', 'label': '匹配达人'},
    {'value': 'peers', 'api_value': 'peer', 'label': '匹配同好'},
]

MATCH_MODE_API_VALUES = {option['api_value'] for option in MATCH_MODE_OPTIONS}
