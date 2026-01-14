from django.db import migrations

def add_default_roles(apps, schema_editor):
    Role = apps.get_model('auth_system', 'Role')
    
    # Default roles list: (name, code, is_default)
    default_roles = [
        ('Admin', 'ADMIN', False),
        ('Driver', 'DRIVER', False),
        ('Owner', 'OWNER', False),
        ('Customer', 'CUSTOMER', True),  # optional default role
    ]

    for name, code, is_default in default_roles:
        # get_or_create ensures duplicates are not created
        Role.objects.get_or_create(
            code=code,  # role code column me insert hoga
            defaults={
                'name': name,
                'is_default': is_default,
                'is_active': True
            }
        )

class Migration(migrations.Migration):

    dependencies = [
        ('auth_system', '0001_initial'),  # Last migration jisme Role table create hua
    ]

    operations = [
        migrations.RunPython(add_default_roles),
    ]
