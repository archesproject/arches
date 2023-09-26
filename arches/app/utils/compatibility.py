import arches
import logging
import semantic_version
from arches.app.models.system_settings import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

def is_compatible_with_arches(min_arches=settings.MIN_ARCHES_VERSION, max_arches=settings.MAX_ARCHES_VERSION, target="project"):
    """
    Check if the current version of arches falls between a min and max version.

    Keyword arguments
    min_arches -- A semvar string representing the minimum supported arches version
    max_arches -- A semver string representing the maximum supported arches version
    target -- A description of what is being checked for compatibility

    """
    
    try:
        arches_version = semantic_version.Version(arches.__version__)
    except ValueError:
        arches_version = semantic_version.Version.coerce(arches.__version__)

    min_is_valid = True
    max_is_valid = True

    versions = {
        'minimum': min_arches,
        'maximum': max_arches
    }

    for key, value in versions.items():
        if value:
            try:
                sem_version = semantic_version.Version(value)
            except ValueError:
                sem_version = semantic_version.Version.coerce(value)
            except Exception as e:
                logger.error(e)
                return False
            if key == "minimum":
                min_is_valid = sem_version <= arches_version
            if key == "maximum":
                max_is_valid = sem_version >= arches_version
        else:
            logger.warning(
                _("A {0} Arches version is not specified. Unable to check {0} version {1} compatibility".format(key, target))
            )
    return min_is_valid and max_is_valid

class CompatibilityError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
