from datetime import datetime
from django.db.utils import IntegrityError, ProgrammingError
from django.utils.translation import gettext as _
from django.db import connection
from arches.app.utils.index_database import index_resources_by_transaction
import logging

logger = logging.getLogger(__name__)


def save_to_tiles(loadid, finalize_import=True, multiprocessing=True):
    with connection.cursor() as cursor:
        try:
            cursor.execute("""CALL __arches_prepare_bulk_load();""")
            cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [loadid])
            saved = cursor.fetchone()[0]
        except (IntegrityError, ProgrammingError) as e:
            logger.error(e)
            cursor.execute(
                """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                ("failed", datetime.now(), loadid),
            )
            return {
                "status": 400,
                "success": False,
                "title": _("Failed to complete load"),
                "message": _("Unable to insert record into staging table"),
            }
        finally:
            try:
                cursor.execute("""CALL __arches_complete_bulk_load();""")

                if finalize_import:
                    cursor.execute("""SELECT __arches_refresh_spatial_views();""")
                    refresh_successful = cursor.fetchone()[0]
                    if not refresh_successful:
                        raise Exception('Unable to refresh spatial views')
            except Exception as e:
                logger.exception(e)
                cursor.execute(
                    """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
                    ("unindexed", datetime.now(), True, True, loadid),
                )

        if saved:
            cursor.execute(
                """UPDATE load_event SET (status, load_end_time) = (%s, %s) WHERE loadid = %s""",
                ("completed", datetime.now(), loadid),
            )
            try:
                index_resources_by_transaction(loadid, quiet=True, use_multiprocessing=False, recalculate_descriptors=True)
                cursor.execute(
                    """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
                    ("indexed", datetime.now(), True, True, loadid),
                )
                return {"success": True, "data": "indexed"}
            except Exception as e:
                logger.exception(e)
                cursor.execute(
                    """UPDATE load_event SET (status, load_end_time) = (%s, %s) WHERE loadid = %s""",
                    ("unindexed", datetime.now(), loadid),
                )
                return {"success": False, "data": "saved"}
        else:
            cursor.execute(
                """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                ("failed", datetime.now(), loadid),
            )
            return {"success": False, "data": "failed"}
