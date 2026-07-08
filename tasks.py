import logging

from celery import shared_task
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.tasks import notify_completion


@shared_task
def migrate_to_reference_datatype(
    userid,
    load_id,
    module_id,
    graph_id,
    origin,
    language_code,
):
    from arches_controlled_lists.etl_modules.migrate_to_reference_datatype import (
        MigrateToReferenceDatatype,
    )

    logger = logging.getLogger(__name__)
    try:
        editor = MigrateToReferenceDatatype(loadid=load_id)
        editor.run_load_task(
            userid,
            load_id,
            module_id,
            graph_id,
            origin,
            language_code,
        )
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as exc:
        logger.error(exc, exc_info=True)
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("Migrate to Reference Datatype: [{}]").format(status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)
