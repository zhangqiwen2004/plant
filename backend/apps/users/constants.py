TAG_OPTION_GROUPS = [
    {
        'value': 'plant_type',
        'label': '植物类型',
        'options': ['多肉植物', '观叶植物', '开花植物', '仙人掌', '蕨类植物', '藤蔓植物', '香草植物', '水培植物'],
    },
    {
        'value': 'care_environment',
        'label': '养护环境',
        'options': ['室内', '阳台', '庭院', '办公室', '北向', '南向'],
    },
    {
        'value': 'interest',
        'label': '兴趣方向',
        'options': ['多肉造景', '阳台花园', '室内绿化', '空气净化', '品种收集', '繁殖扦插'],
    },
    {
        'value': 'problem',
        'label': '常见问题',
        'options': ['黄叶问题', '浇水问题', '光照不足', '病虫害', '烂根', '徒长'],
    },
]

TAG_OPTIONS_BY_TYPE = {
    group['value']: set(group['options'])
    for group in TAG_OPTION_GROUPS
}
