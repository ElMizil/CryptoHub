# Generated by Django 4.2.3 on 2023-12-13 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0005_rename_cvv_card_cvv_alter_card_expiration_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('amount', models.IntegerField(default=0)),
                ('value', models.IntegerField(default=0)),
            ],
        ),
    ]