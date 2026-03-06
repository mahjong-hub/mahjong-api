import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rule', '0004_ruleset_rulesetversion_rulesetscoringconfig_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleexclusion',
            name='ruleset_version',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='exclusions',
                to='rule.rulesetversion',
            ),
        ),
        migrations.AlterField(
            model_name='ruleexclusion',
            name='ruleset_version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='exclusions',
                to='rule.rulesetversion',
            ),
        ),
    ]
