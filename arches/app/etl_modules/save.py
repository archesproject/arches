from datetime import datetime
import json
from django.db.utils import IntegrityError, ProgrammingError
from django.contrib.auth.models import User
from django.db import connection
from django.utils.translation import gettext as _
from arches.app.models.system_settings import settings
from arches.app.utils.index_database import index_resources_by_transaction
import logging

logger = logging.getLogger(__name__)


def save_to_tiles(userid, loadid, finalize_import=True, multiprocessing=True):
    with connection.cursor() as cursor:
        try:
            cursor.execute("""CALL __arches_prepare_bulk_load();""")
            cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [loadid])
            saved = cursor.fetchone()[0]
            if saved:
                cursor.execute(
                    """SELECT g.name graph, COUNT(DISTINCT l.resourceid)
                        FROM load_staging l, resource_instances r, graphs g
                        WHERE l.loadid = %s
                        AND r.resourceinstanceid = l.resourceid
                        AND g.graphid = r.graphid
                        GROUP BY g.name
                    """, [loadid]
                )
                resources = cursor.fetchall()
                number_of_resources = {}
                for resource in resources:
                    graph = json.loads(resource[0])[settings.LANGUAGE_CODE]
                    number_of_resources.update({ graph: { "total": resource[1] } })
                cursor.execute(
                    """SELECT g.name graph, n.name, COUNT(*)
                        FROM load_staging l, nodes n, graphs g
                        WHERE l.loadid = %s
                        AND n.nodeid = l.nodegroupid
                        AND n.graphid = g.graphid
                        GROUP BY n.name, g.name;
                    """, [loadid]
                )
                tiles = cursor.fetchall()
                for tile in tiles:
                    graph = json.loads(tile[0])[settings.LANGUAGE_CODE]
                    number_of_resources[graph].setdefault('tiles', []).append({'tile': tile[1], 'count': tile[2] })

                number_of_import = json.dumps({ "number_of_import": [{ "name": k, "total": v["total"], "tiles": v["tiles"] } for k, v in number_of_resources.items()]})
                cursor.execute(
                    """UPDATE load_event SET load_details = load_details || %s::JSONB WHERE loadid = %s""",
                    (number_of_import, loadid),
                )

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
                user = User.objects.get(id=userid)
                user_email = getattr(user, "email", "")
                user_firstname = getattr(user, "first_name", "")
                user_lastname = getattr(user, "last_name", "")
                user_username = getattr(user, "username", "")
                cursor.execute(
                    """
                        UPDATE edit_log e
                        SET (resourcedisplayname, userid, user_firstname, user_lastname, user_email, user_username) = (r.name ->> %s, %s, %s, %s, %s, %s)
                        FROM resource_instances r
                        WHERE e.resourceinstanceid::uuid = r.resourceinstanceid
                        AND transactionid = %s
                    """,
                    (settings.LANGUAGE_CODE, userid, user_firstname, user_lastname, user_email, user_username, loadid),
                )
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
