from slugify import slugify
import uuid

from django.utils.translation import gettext as _
from django.db import models

from arches.app.models.system_settings import settings
from arches.app.models.utils import make_name_unique


class GraphModelQuerySet(models.QuerySet):
    def generate_slug(self, name, is_resource):
        if name:
            slug = slugify(name, separator="_")
        else:
            if is_resource:
                slug = "new_resource_model"
            else:
                slug = "new_branch"
        existing_slugs = self.values_list("slug", flat=True)
        slug = make_name_unique(slug, existing_slugs, "_")

        return slug

    def create_graph(self, name="", *, slug=None, user=None, is_resource=False):
        from arches.app.models import models as arches_models

        """
        Create a new Graph and related objects, encapsulating all creation side effects.
        """
        new_id = uuid.uuid4()
        nodegroup = None

        if not slug:
            slug = self.generate_slug(name, is_resource)

        graph_model = arches_models.GraphModel(
            name=name,
            subtitle="",
            author=(
                " ".join(filter(None, [user.first_name, user.last_name]))
                if user
                else ""
            ),
            description="",
            version="",
            isresource=is_resource,
            iconclass="",
            ontology=None,
            slug=slug,
        )
        graph_model.save()  # to access side-effects declared in save method

        if not is_resource:
            nodegroup = arches_models.NodeGroup.objects.create(pk=new_id)
            arches_models.CardModel.objects.create(
                nodegroup=nodegroup, name=name, graph=graph_model
            )

        # root node
        arches_models.Node.objects.create(
            pk=new_id,
            name=name,
            description="",
            istopnode=True,
            ontologyclass=None,
            datatype="semantic",
            nodegroup=nodegroup,
            graph=graph_model,
        )

        graph = self.get(pk=graph_model.graphid)

        graph.publish(
            user=user,
            notes=_("Graph created."),
        )
        graph.create_draft_graph()

        # ensures entity returned matches database entity
        return self.get(pk=graph_model.graphid)

    def filter_active(self, is_active=True):
        return self.filter(is_active=is_active)

    def filter_drafts(self, is_draft=True):
        return self.filter(source_identifier__isnull=not is_draft)

    def exclude_system_settings(self):
        return self.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)

    def get_current_graphs(self, exclude_system_settings=True, exclude_inactive=True):
        query_set = self.filter(isresource=True).filter_drafts(is_draft=False)
        if exclude_system_settings:
            query_set = query_set.exclude_system_settings()
        if exclude_inactive:
            query_set = query_set.filter_active()
        return query_set

    def get_resource_models(self, exclude_system_settings=True, exclude_inactive=True):
        return self.get_current_graphs(
            exclude_system_settings=exclude_system_settings,
            exclude_inactive=exclude_inactive,
        ).filter(isresource=True)

    def get_branches(self, exclude_system_settings=True, exclude_inactive=True):
        return self.get_current_graphs(
            exclude_system_settings=exclude_system_settings,
            exclude_inactive=exclude_inactive,
        ).filter(isresource=False)


class GraphQuerySet(GraphModelQuerySet):
    def create(self, *args, **kwargs):
        raise NotImplementedError(
            "Use create_graph() to create new Graph instances with proper business logic."
        )
