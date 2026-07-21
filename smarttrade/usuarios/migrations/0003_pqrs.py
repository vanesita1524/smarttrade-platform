from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usuarios', '0002_perfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='PQRS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('mensaje', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En Proceso'), ('resuelto', 'Resuelto'), ('cerrado', 'Cerrado')], default='pendiente', max_length=20)),
                ('respuesta', models.TextField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pqrs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'PQRS',
                'verbose_name_plural': 'PQRS',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]