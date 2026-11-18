from django.db import migrations

from workout_plan.catalog.exercise_name_translations import EXERCISE_NAME_TRANSLATIONS


def seed_translations(apps, schema_editor):
    exercise_model = apps.get_model('workout_plan', 'Exercise')
    for exercise in exercise_model.objects.filter(catalog_key__in=EXERCISE_NAME_TRANSLATIONS.keys()):
        exercise.name_translations = EXERCISE_NAME_TRANSLATIONS[exercise.catalog_key]
        exercise.save(update_fields=['name_translations'])


class Migration(migrations.Migration):

    dependencies = [
        ('workout_plan', '0006_exercise_name_translations'),
    ]

    operations = [
        migrations.RunPython(seed_translations, migrations.RunPython.noop),
    ]
