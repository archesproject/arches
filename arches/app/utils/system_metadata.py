"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import platform
import subprocess
from django.db import connection, transaction
from arches.app.models.system_settings import settings


def system_metadata():
    os_type = platform.system()
    os_release = platform.release()
    cursor = connection.cursor()
    sql = "SELECT version()"

    try:
        cursor.execute(sql)
        db = cursor.fetchall()[0][0]
    except:
        db = "No DB version found."

    try:
        full_tag = subprocess.Popen(
            "git log --pretty=format:'%h %ai' --abbrev-commit --date=short -1",
            cwd=settings.PACKAGE_ROOT,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        tag = full_tag.stdout.readline().strip()
    except:
        tag = "git not found."

    metadata = {"os": os_type, "os version": os_release, "db": db, "git hash": tag}
    return metadata
