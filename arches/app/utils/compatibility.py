import logging
from arches import VERSION
from arches.app.models.system_settings import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def is_arches_compatible(min_arches=settings.MIN_ARCHES_VERSION, max_arches=settings.MAX_ARCHES_VERSION, target="project"):
    """
    Check if the current version of arches falls between a min and max version.

    Keyword arguments
    min_arches -- A tuple with at least a major version of arches, but may also include a min and patch release e.g. (7,4,0)
    max_arches -- A tuple with at least a major version of arches, but may also include a min and patch release e.g. (7,5,0)
    target -- A description of what is being checked for compatibility

    """

    if min_arches is None or max_arches is None:
        logger.error(
            _("Either a minimum or maximum compatible Arches version is not specified. Unable to check {0} compatibility".format(target))
        )
        return

    if len(min_arches) <= 3 and len(max_arches) <= 3:
        min_is_valid = min_arches <= VERSION[: len(min_arches)]
        max_is_valid = max_arches >= VERSION[: len(max_arches)]
        return min_is_valid and max_is_valid
    else:
        raise ValueError(_("No more than 3 digits allowed in MIN_ARCHES_VERSION or MAX_ARCHES_VERSION"))


class CompatibilityError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
