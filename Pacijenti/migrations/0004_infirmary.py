# Generated by Django 5.1.7 on 2025-06-09 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pacijenti', '0003_korisnik_uloga'),
    ]

    operations = [
        migrations.CreateModel(
            name='Infirmary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('long', models.DecimalField(decimal_places=3, max_digits=8)),
                ('lat', models.DecimalField(decimal_places=3, max_digits=8)),
                ('doktor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to='Pacijenti.doktor')),
                ('medicinska_sestra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sestre', to='Pacijenti.medicinskasestra')),
            ],
        ),
    ]
