from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10515_i18n_plugins"),
    ]

    add_celery_threshold_config = """
        update etl_modules
            set config = jsonb_set(config, '{celeryThreshold}', to_jsonb(500), true)
            where etlmoduleid = '0a0cea7e-b59a-431a-93d8-e9f8c41bdd6b';
        update etl_modules
            set config = jsonb_set(config, '{celeryThreshold}', to_jsonb(100000), true)
            where etlmoduleid in (
                '3b19a76a-0b09-450e-bee1-65accb096eaf',
                'b96b8078-23b7-484f-b9d0-8ca304a5f7b6'
            );
    """

    revert_config = """
        update etl_modules
        set config = config - 'celeryThreshold'
        where etlmoduleid in (
            '0a0cea7e-b59a-431a-93d8-e9f8c41bdd6b',
            '3b19a76a-0b09-450e-bee1-65accb096eaf',
            'b96b8078-23b7-484f-b9d0-8ca304a5f7b6'
        );
    """

    operations = [
        migrations.RunSQL(
            add_celery_threshold_config,
            revert_config,
        ),
    ]
