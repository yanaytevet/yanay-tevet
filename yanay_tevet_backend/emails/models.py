from django.db import models


class EmailTemplate(models.Model):
    class Meta:
        managed = False
        app_label = 'emails'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
