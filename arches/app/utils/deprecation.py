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

# This module must not import from arches so that low-level modules
# (e.g. arches.app.models.models) can use @deprecated without circular imports.
# It is re-exported from arches.app.utils.decorators.

import functools
import logging
import warnings

logger = logging.getLogger(__name__)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used, stating that the function will be
    removed in the next feature release.
    """

    message = (
        "Call to deprecated function {}.{}. "
        "It will be removed in the next feature release.".format(
            func.__module__, func.__qualname__
        )
    )

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)
        logger.warning(message)
        return func(*args, **kwargs)

    return new_func
