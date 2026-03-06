from django.db import migrations

RULES = [
    {
        'code': 'common_hand',
        'label': {'en': 'Common Hand', 'zh-hk': '平糊', 'zh-cn': '平和'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'is',       'value': None, 'type': 'hand', 'target': 'standard', 'context': None},
            {'operator': 'at_least', 'value': 4,    'type': 'chow', 'target': None,       'context': None},
            {'operator': 'none',     'value': None, 'type': 'tile', 'target': 'honor',    'context': None},
        ],
    },
    {
        'code': 'dragon_pung_red',
        'label': {'en': 'Red Dragon Pung', 'zh-hk': '中', 'zh-cn': '紅中'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 1, 'type': 'pung', 'target': 'red', 'context': None},
        ],
    },
    {
        'code': 'dragon_pung_green',
        'label': {'en': 'Green Dragon Pung', 'zh-hk': '發', 'zh-cn': '發財'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 1, 'type': 'pung', 'target': 'green', 'context': None},
        ],
    },
    {
        'code': 'dragon_pung_white',
        'label': {'en': 'White Dragon Pung', 'zh-hk': '白', 'zh-cn': '白板'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 1, 'type': 'pung', 'target': 'white', 'context': None},
        ],
    },
    {
        'code': 'seat_wind_pung',
        'label': {'en': 'Seat Wind Pung', 'zh-hk': '門風', 'zh-cn': '門風刻'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 1, 'type': 'pung', 'target': 'wind', 'context': 'seat_wind'},
        ],
    },
    {
        'code': 'round_wind_pung',
        'label': {'en': 'Round Wind Pung', 'zh-hk': '圈風', 'zh-cn': '圈風刻'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 1, 'type': 'pung', 'target': 'wind', 'context': 'round_wind'},
        ],
    },
    {
        'code': 'self_drawn',
        'label': {'en': 'Self Drawn', 'zh-hk': '自摸', 'zh-cn': '自摸'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'self_draw'},
        ],
    },
    {
        'code': 'concealed_hand',
        'label': {'en': 'Concealed Hand', 'zh-hk': '門清', 'zh-cn': '門前清'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'hand', 'target': None, 'context': 'concealed'},
        ],
    },
    {
        'code': 'no_flowers',
        'label': {'en': 'No Flowers', 'zh-hk': '無花', 'zh-cn': '無花'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'none', 'value': None, 'type': 'tile', 'target': 'flower', 'context': None},
        ],
    },
    {
        'code': 'last_tile_draw',
        'label': {'en': 'Last Tile Draw', 'zh-hk': '海底撈月', 'zh-cn': '海底撈月'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'last_tile'},
        ],
    },
    {
        'code': 'last_tile_discard',
        'label': {'en': 'Last Tile Discard', 'zh-hk': '河底撈魚', 'zh-cn': '河底撈魚'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'last_discard'},
        ],
    },
    {
        'code': 'win_on_replacement',
        'label': {'en': 'Win on Replacement', 'zh-hk': '嶺上開花', 'zh-cn': '嶺上開花'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'replacement'},
        ],
    },
    {
        'code': 'rob_kong',
        'label': {'en': 'Rob Kong', 'zh-hk': '搶槓', 'zh-cn': '搶槓'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'rob_kong'},
        ],
    },
    {
        'code': 'little_three_dragons',
        'label': {'en': 'Little Three Dragons', 'zh-hk': '小三元', 'zh-cn': '小三元'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'at_least', 'value': 2, 'type': 'pung', 'target': 'dragon', 'context': None},
            {'operator': 'at_least', 'value': 1, 'type': 'pair', 'target': 'dragon', 'context': None},
        ],
    },
    {
        'code': 'win_on_double_replacement',
        'label': {'en': 'Win on Double Replacement', 'zh-hk': '槓上槓', 'zh-cn': '槓上槓'},
        'kind': 'bonus',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'double_replacement'},
        ],
    },
    {
        'code': 'all_pungs',
        'label': {'en': 'All Pungs', 'zh-hk': '對對胡', 'zh-cn': '碰碰胡'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'is',       'value': None, 'type': 'hand', 'target': 'standard', 'context': None},
            {'operator': 'at_least', 'value': 4,    'type': 'pung', 'target': None,       'context': None},
        ],
    },
    {
        'code': 'half_flush',
        'label': {'en': 'Half Flush', 'zh-hk': '混一色', 'zh-cn': '混一色'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'is',       'value': None, 'type': 'hand', 'target': 'standard', 'context': None},
            {'operator': 'exactly',  'value': 1,    'type': 'suit', 'target': None,       'context': None},
            {'operator': 'at_least', 'value': 1,    'type': 'tile', 'target': 'honor',    'context': None},
        ],
    },
    {
        'code': 'seven_pairs',
        'label': {'en': 'Seven Pairs', 'zh-hk': '七對子', 'zh-cn': '七对子'},
        'kind': 'special',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'hand', 'target': 'seven_pairs', 'context': None},
        ],
    },
    {
        'code': 'full_flush',
        'label': {'en': 'Full Flush', 'zh-hk': '清一色', 'zh-cn': '清一色'},
        'kind': 'pattern',
        'conditions': [
            {'operator': 'is',      'value': None, 'type': 'hand', 'target': 'standard', 'context': None},
            {'operator': 'exactly', 'value': 1,    'type': 'suit', 'target': None,       'context': None},
            {'operator': 'none',    'value': None, 'type': 'tile', 'target': 'honor',    'context': None},
        ],
    },
    {
        'code': 'big_three_dragons',
        'label': {'en': 'Big Three Dragons', 'zh-hk': '大三元', 'zh-cn': '大三元'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'at_least', 'value': 3, 'type': 'pung', 'target': 'dragon', 'context': None},
        ],
    },
    {
        'code': 'little_four_winds',
        'label': {'en': 'Little Four Winds', 'zh-hk': '小四喜', 'zh-cn': '小四喜'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'at_least', 'value': 3, 'type': 'pung', 'target': 'wind', 'context': None},
            {'operator': 'at_least', 'value': 1, 'type': 'pair', 'target': 'wind', 'context': None},
        ],
    },
    {
        'code': 'big_four_winds',
        'label': {'en': 'Big Four Winds', 'zh-hk': '大四喜', 'zh-cn': '大四喜'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'at_least', 'value': 4, 'type': 'pung', 'target': 'wind', 'context': None},
        ],
    },
    {
        'code': 'all_honors',
        'label': {'en': 'All Honors', 'zh-hk': '字一色', 'zh-cn': '字一色'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'none', 'value': None, 'type': 'tile', 'target': 'simple',   'context': None},
            {'operator': 'none', 'value': None, 'type': 'tile', 'target': 'terminal', 'context': None},
        ],
    },
    {
        'code': 'all_terminals',
        'label': {'en': 'All Terminals', 'zh-hk': '清老頭', 'zh-cn': '清老頭'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'none', 'value': None, 'type': 'tile', 'target': 'simple', 'context': None},
            {'operator': 'none', 'value': None, 'type': 'tile', 'target': 'honor',  'context': None},
        ],
    },
    {
        'code': 'half_terminals',
        'label': {'en': 'Half Terminals', 'zh-hk': '混老頭', 'zh-cn': '混老頭'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is',       'value': None, 'type': 'hand', 'target': 'standard', 'context': None},
            {'operator': 'at_least', 'value': 4,    'type': 'pung', 'target': None,       'context': None},
            {'operator': 'none',     'value': None, 'type': 'tile', 'target': 'simple',   'context': None},
        ],
    },
    {
        'code': 'nine_gates',
        'label': {'en': 'Nine Gates', 'zh-hk': '九蓮寶燈', 'zh-cn': '九蓮寶燈'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'hand', 'target': 'nine_gates', 'context': None},
        ],
    },
    {
        'code': 'thirteen_orphans',
        'label': {'en': 'Thirteen Orphans', 'zh-hk': '十三么', 'zh-cn': '十三幺'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'hand', 'target': 'thirteen_orphans', 'context': None},
        ],
    },
    {
        'code': 'four_concealed_pungs',
        'label': {'en': 'Four Concealed Pungs', 'zh-hk': '四暗刻', 'zh-cn': '四暗刻'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'at_least', 'value': 4, 'type': 'pung', 'target': None, 'context': 'concealed'},
        ],
    },
    {
        'code': 'all_kongs',
        'label': {'en': 'All Kongs', 'zh-hk': '十八羅漢', 'zh-cn': '四槓'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'at_least', 'value': 4, 'type': 'kong', 'target': None, 'context': None},
        ],
    },
    {
        'code': 'perfect_green',
        'label': {'en': 'Perfect Green', 'zh-hk': '綠一色', 'zh-cn': '綠一色'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'hand', 'target': 'all_green', 'context': None},
        ],
    },
    {
        'code': 'heavenly_hand',
        'label': {'en': 'Heavenly Hand', 'zh-hk': '天糊', 'zh-cn': '天糊'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'heavenly'},
        ],
    },
    {
        'code': 'earthly_hand',
        'label': {'en': 'Earthly Hand', 'zh-hk': '地糊', 'zh-cn': '地糊'},
        'kind': 'limit',
        'conditions': [
            {'operator': 'is', 'value': None, 'type': 'win', 'target': None, 'context': 'earthly'},
        ],
    },
]


def seed_rules(apps, schema_editor):
    RuleDefinition = apps.get_model('rule', 'RuleDefinition')
    RuleLogic = apps.get_model('rule', 'RuleLogic')
    RuleCondition = apps.get_model('rule', 'RuleCondition')

    for rule in RULES:
        rd, _ = RuleDefinition.objects.update_or_create(
            code=rule['code'],
            defaults={'label': rule['label'], 'kind': rule['kind']},
        )
        rl, _ = RuleLogic.objects.update_or_create(
            rule_definition=rd,
            defaults={'combine_op': 'and'},
        )
        rl.conditions.all().delete()
        for c in rule['conditions']:
            RuleCondition.objects.create(rule_logic=rl, **c)


def unseed_rules(apps, schema_editor):
    RuleDefinition = apps.get_model('rule', 'RuleDefinition')
    RuleDefinition.objects.filter(
        code__in=[r['code'] for r in RULES],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rule', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_rules, reverse_code=unseed_rules),
    ]
