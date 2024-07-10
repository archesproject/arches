import logging
import os
import uuid

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.template.loader import get_template, render_to_string
from guardian.models import GroupObjectPermission
from guardian.shortcuts import assign_perm

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.utils.external_oauth_backend import ExternalOauthAuthenticationBackend

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=models.File)
def delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = models.File.objects.get(pk=instance.pk).path
    except models.File.DoesNotExist:
        return False

    new_file = instance.path
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            return False


# This event listener auto-deletes files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(post_delete, sender=models.File)
def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is deleted.
    """

    if instance.path:
        try:
            if os.path.isfile(instance.path.path):
                os.remove(instance.path.path)
        # except block added to deal with S3 file deletion
        # see comments on 2nd answer below
        # http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab
        except Exception as e:
            storage, name = instance.path.storage, instance.path.name
            storage.delete(name)


# This event listener auto-deletes files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(post_delete, sender=models.FileValue)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `FileValue` object is deleted.
    """
    if instance.value.path:
        try:
            if os.path.isfile(instance.value.path):
                os.remove(instance.value.path)
        # except block added to deal with S3 file deletion
        # see comments on 2nd answer below
        # http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab
        except Exception as e:
            storage, name = instance.value.storage, instance.value.name
            storage.delete(name)


# This event listener auto-deletes files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(pre_save, sender=models.FileValue)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `FileValue` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = models.FileValue.objects.get(pk=instance.pk).value
    except models.FileValue.DoesNotExist:
        return False

    new_file = instance.value
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.value):
                os.remove(old_file.value)
        except Exception:
            return False


@receiver(post_save, sender=models.Node)
def clear_user_permission_cache(sender, instance, **kwargs):
    user_permission_cache = caches["user_permission"]

    if user_permission_cache:
        user_permission_cache.clear()


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    models.UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_permissions_for_new_users(sender, instance, created, **kwargs):
    if created:
        ct = ContentType.objects.get(app_label="models", model="resourceinstance")
        resourceInstanceIds = list(
            GroupObjectPermission.objects.filter(content_type=ct)
            .values_list("object_pk", flat=True)
            .distinct()
        )
        for resourceInstanceId in resourceInstanceIds:
            resourceInstanceId = uuid.UUID(resourceInstanceId)
        resources = models.ResourceInstance.objects.filter(pk__in=resourceInstanceIds)
        assign_perm("no_access_to_resourceinstance", instance, resources)
        for resource_instance in resources:
            resource = Resource(resource_instance.resourceinstanceid)
            resource.graph_id = resource_instance.graph_id
            resource.createdtime = resource_instance.createdtime
            resource.index()


@receiver(post_save, sender=models.UserXNotification)
def send_email_on_save(sender, instance, **kwargs):
    """Checks if a notification type needs to send an email, does so if email server exists"""

    if instance.notif.notiftype is not None and instance.isread is False:
        if models.UserXNotificationType.objects.filter(
            user=instance.recipient,
            notiftype=instance.notif.notiftype,
            emailnotify=False,
        ).exists():
            return False

        try:
            context = instance.notif.context.copy()
            text_content = render_to_string(
                instance.notif.notiftype.emailtemplate, context
            )
            html_template = get_template(instance.notif.notiftype.emailtemplate)
            html_content = html_template.render(context)
            if context["email"] == instance.recipient.email:
                email_to = instance.recipient.email
            else:
                email_to = context["email"]

            if type(email_to) is not list:
                email_to = [email_to]

            subject, from_email, to = (
                instance.notif.notiftype.name,
                settings.DEFAULT_FROM_EMAIL,
                email_to,
            )
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            if instance.notif.notiftype.webnotify is not True:
                instance.isread = True
                instance.save()
        except Exception as e:
            logger.warning(e)
            logger.warning(
                "Error occurred sending email.  See previous stack trace and check email configuration in settings.py."
            )

    return False


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    try:
        token = ExternalOauthAuthenticationBackend.get_token(user)
        if token is not None:
            token.delete()
    except models.ExternalOauthToken.DoesNotExist:
        pass


@receiver(user_logged_in)
def login(sender, user, request, **kwargs):
    if (
        user.backend
        == "arches.app.utils.external_oauth_backend.ExternalOauthAuthenticationBackend"
    ):
        try:
            token = ExternalOauthAuthenticationBackend.get_token(user)
            request.session.set_expiry(
                (token.access_token_expiration - datetime.now()).total_seconds()
            )
        except models.ExternalOauthToken.DoesNotExist:
            pass
