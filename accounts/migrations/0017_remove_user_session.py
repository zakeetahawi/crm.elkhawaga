from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20250415_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersession',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserSession',
        ),
    ]
