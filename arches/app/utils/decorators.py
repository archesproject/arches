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

import warnings
import functools
import logging
import datetime

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from arches.app.utils.permission_backend import user_can_read_resource
from arches.app.utils.permission_backend import user_can_edit_resource
from arches.app.utils.permission_backend import user_can_delete_resource
from arches.app.utils.permission_backend import user_can_read_concepts
from arches.app.utils.permission_backend import user_created_transaction
from arches.app.utils.permission_backend import (
    group_required as permission_group_required,
)


# Get an instance of a logger
logger = logging.getLogger(__name__)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.__code__.co_filename,
            lineno=func.__code__.co_firstlineno + 1,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        logger.warning(
            "%s - DeprecationWarning: Call to deprecated function %s. %s:%s"
            % (
                datetime.datetime.now(),
                func.__name__,
                func.__code__.co_filename,
                func.__code__.co_firstlineno + 1,
            )
        )
        return func(*args, **kwargs)

    return new_func


def group_required(*group_names, raise_exception=False):
    """
    Requires user membership in at least one of the groups passed in.

    """

    def in_groups(u):
        passed = permission_group_required(u, *group_names)
        if passed:
            return True
        elif raise_exception:
            raise PermissionDenied
        # else: user_passes_test() redirects to nowhere
        return False

    return user_passes_test(in_groups)


def can_edit_resource_instance(redirect_to_report=False):
    def decorator(function):
        @functools.wraps(function)
        def _wrapped_view(request, *args, **kwargs):
            resourceid = kwargs["resourceid"] if "resourceid" in kwargs else None
            if user_can_edit_resource(request.user, resourceid=resourceid):
                return function(request, *args, **kwargs)
            else:
                if redirect_to_report:
                    url = reverse("resource_report", kwargs={"resourceid": resourceid})
                    return HttpResponseRedirect(f"{url}?redirected=true")
                else:
                    raise PermissionDenied

        return _wrapped_view

    # If the decorator is called without arguments
    if callable(redirect_to_report):
        return decorator(redirect_to_report)

    return decorator


def can_read_resource_instance(function):
    """
    Requires that a user be able to edit or delete a single nodegroup of a resource

    """

    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        resourceid = kwargs["resourceid"] if "resourceid" in kwargs else None
        if user_can_read_resource(request.user, resourceid=resourceid):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
        return function(request, *args, **kwargs)

    return wrapper


def can_delete_resource_instance(function):
    """
    Requires that a user be able to edit or delete a single nodegroup of a resource

    """

    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        resourceid = kwargs["resourceid"] if "resourceid" in kwargs else None
        if user_can_delete_resource(request.user, resourceid=resourceid):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper


def can_read_concept():
    """
    Requires that a user be able to edit or delete a single nodegroup of a resource

    """

    return user_passes_test(user_can_read_concepts)


# Checks whether current user is the one who created a particular transaction ID
def user_created_transaction_match(function):
    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        transactionid = kwargs["transactionid"] if "transactionid" in kwargs else None
        if user_created_transaction(request.user, transactionid=transactionid):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper
