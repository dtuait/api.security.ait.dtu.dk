"""Alter the authtoken key length to support extended tokens."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authtoken", "0004_alter_tokenproxy_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="token",
            name="key",
            field=models.CharField(
                max_length=255,
                primary_key=True,
                serialize=False,
                verbose_name="Key",
            ),
        ),
    ]
