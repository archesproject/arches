import logging
import os

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.template.loader import get_template, render_to_string

from arches.app.models import models
from arches.app.utils.external_oauth_backend import ExternalOauthAuthenticationBackend
from arches.app.utils.permission_backend import process_new_user


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


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return

    models.UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_permissions_for_new_users(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return

    if created:
        process_new_user(instance, created)


@receiver(m2m_changed, sender=User.groups.through)
def update_groups_for_user(sender, instance, action, **kwargs):
    from arches.app.utils.permission_backend import update_groups_for_user

    if action in ("post_add", "post_remove"):
        update_groups_for_user(instance)


@receiver(m2m_changed, sender=User.user_permissions.through)
def update_permissions_for_user(sender, instance, action, **kwargs):
    from arches.app.utils.permission_backend import update_permissions_for_user

    if action in ("post_add", "post_remove"):
        update_permissions_for_user(instance)


@receiver(m2m_changed, sender=Group.permissions.through)
def update_permissions_for_group(sender, instance, action, **kwargs):
    from arches.app.utils.permission_backend import update_permissions_for_group

    if action in ("post_add", "post_remove"):
        update_permissions_for_group(instance)


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


@receiver(pre_save, sender=models.SearchComponent)
def ensure_single_default_searchview(sender, instance, **kwargs):
    if instance.config.get("default", False) and instance.type == "search-view":
        existing_default = models.SearchComponent.objects.filter(
            config__default=True, type="search-view"
        ).exclude(searchcomponentid=instance.searchcomponentid)
        if existing_default.exists():
            raise ValidationError(
                "Only one search logic component can be default at a time."
            )


@receiver(post_save, sender=models.Card)
@receiver(post_delete, sender=models.Card)
@receiver(post_save, sender=models.CardModel)
@receiver(post_delete, sender=models.CardModel)
@receiver(post_save, sender=models.Node)
@receiver(post_delete, sender=models.Node)
@receiver(post_save, sender=models.Edge)
@receiver(post_delete, sender=models.Edge)
@receiver(post_save, sender=models.FunctionXGraph)
@receiver(post_delete, sender=models.FunctionXGraph)
@receiver(post_save, sender=models.GraphXPublishedGraph)
@receiver(post_delete, sender=models.GraphXPublishedGraph)
def set_related_graph_has_unpublished_changes_to_true(sender, instance, **kwargs):
    models.GraphModel.objects.filter(pk=instance.graph_id).update(
        has_unpublished_changes=True
    )


@receiver(post_save, sender=models.NodeGroup)
@receiver(post_delete, sender=models.NodeGroup)
def set_related_graph_has_unpublished_changes_to_true(sender, instance, **kwargs):
    # NodeGroups have no direct relation to the GraphModel objects,
    # so this signal can fail to find the node when deleting a Graphs
    try:
        models.GraphModel.objects.filter(pk=instance.grouping_node.graph_id).update(
            has_unpublished_changes=True
        )
    except:
        pass


@receiver(post_save, sender=models.CardXNodeXWidget)
@receiver(post_delete, sender=models.CardXNodeXWidget)
def set_related_graph_has_unpublished_changes_to_true(sender, instance, **kwargs):
    # CardXNodeXWidgets have no direct relation to the GraphModel objects,
    # so this signal can fail to find the node when deleting a Graphs
    try:
        models.GraphModel.objects.filter(pk=instance.node.graph_id).update(
            has_unpublished_changes=True
        )
    except:
        pass
