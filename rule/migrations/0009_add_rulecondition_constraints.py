from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rule', '0008_update_seed_condition_types'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='rulecondition',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(operator__isnull=True)
                    | models.Q(operator__in=['at_least', 'at_most', 'exactly'])
                ),
                name='rule_rulecondition_operator_valid',
            ),
        ),
        migrations.AddConstraint(
            model_name='rulecondition',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    type__in=[
                        'hand_structure',
                        'chow_count',
                        'pung_count',
                        'kong_count',
                        'pair_count',
                        'tile_count',
                        'suit_count',
                        'win_condition',
                    ]
                ),
                name='rule_rulecondition_type_valid',
            ),
        ),
        migrations.AddConstraint(
            model_name='rulecondition',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        type__in=['chow_count', 'pung_count', 'kong_count', 'pair_count', 'tile_count'],
                        target__in=[
                            'simple', 'terminal', 'honor', 'dragon', 'wind',
                            'red', 'green', 'white', 'bamboo', 'dot', 'character', 'flower',
                        ],
                        operator__isnull=False,
                        value__isnull=False,
                        context__isnull=True,
                    )
                    | models.Q(
                        type__in=['chow_count', 'pung_count', 'kong_count', 'pair_count'],
                        target__isnull=True,
                        operator__isnull=False,
                        value__isnull=False,
                        context__isnull=True,
                    )
                    | models.Q(
                        type__in=['chow_count', 'pung_count', 'kong_count', 'pair_count'],
                        context__in=['seat_wind', 'round_wind', 'concealed'],
                        operator__isnull=False,
                        value__isnull=False,
                    )
                    | models.Q(
                        type='hand_structure',
                        target__in=['standard', 'seven_pairs', 'thirteen_orphans', 'nine_gates', 'all_green'],
                        operator__isnull=True,
                        value__isnull=True,
                        context__isnull=True,
                    )
                    | models.Q(
                        type='suit_count',
                        target__isnull=True,
                        operator__isnull=False,
                        value__isnull=False,
                        context__isnull=True,
                    )
                    | models.Q(
                        type='win_condition',
                        context__in=[
                            'concealed', 'seat_wind', 'round_wind', 'self_draw', 'rob_kong',
                            'replacement', 'double_replacement', 'last_tile', 'last_discard',
                            'heavenly', 'earthly',
                        ],
                        operator__isnull=True,
                        target__isnull=True,
                        value__isnull=True,
                    )
                ),
                name='rule_rulecondition_target_valid',
            ),
        ),
    ]
