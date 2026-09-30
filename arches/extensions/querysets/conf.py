from django.conf import settings as django_settings


class AppSettings:
    @property
    def CONCEPT_CACHE(self):
        return getattr(django_settings, "ARCHES_QUERYSETS_CONCEPT_CACHE", "default")

    @property
    def RESOURCE_INSTANCE_CACHE(self):
        return getattr(
            django_settings, "ARCHES_QUERYSETS_RESOURCE_INSTANCE_CACHE", "default"
        )


settings = AppSettings()
