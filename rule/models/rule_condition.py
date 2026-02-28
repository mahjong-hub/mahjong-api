import uuid

from django.db import models


class RuleCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='conditions',
        on_delete=models.CASCADE,
    )
    operator = models.CharField(max_length=32)
    value = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=32)
    target = models.CharField(max_length=64, null=True, blank=True)
    context = models.CharField(max_length=64, null=True, blank=True)
