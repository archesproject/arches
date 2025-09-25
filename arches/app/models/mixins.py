class SaveSupportsBlindOverwriteMixin:
    def add_force_keyword(self, kwargs):
        """
        Django 3.0 introduced a performance optimization when calling save() on
        instances where its primary key field has a default. In this case, Django
        assumes that calling save() on an instance that has not been fetched
        will never be used to overwrite an existing row. For "blind" overwrites,
        the suggested pattern is to use queryset methods update() or update_or_create()
        to signal that overwriting is intentional. In Django 5.1+, you can at least
        pass force_update=True to save() to perform a blind overwrite if desired.
        This helper determines whether that's needed and sets force_update=True if so.

        **New Django models should avoid using this mixin** and should use update()
        or update_or_create() instead. This is really just here to avoiding auditing
        for blind overwrites in code calling save() on models predating Django 3.0.

        (The solution in Arches 6.2 during the Django 3.2 upgrade was just to remove
        field defaults, in favor of overrides of __init__() and save() to supply defaults,
        but that left gaps, e.g. queryset methods like create(). So Arches 8.0 added
        the field defaults back and added this mixin.)

        https://forum.djangoproject.com/t/save-behavior-when-updating-model-with-default-primary-keys
        """
        new_kwargs = {**kwargs}
        if new_kwargs.get("force_insert") or new_kwargs.get("force_update"):
            # The caller knows what they are doing.
            return new_kwargs
        has_default_pk = all(
            f.has_default() or f.has_db_default() for f in self._meta.pk_fields
        )
        if not has_default_pk:
            msg = f"Calling add_force_keyword() is a pessimization for models without default primary keys: {self.__class__.__name__}"
            raise ValueError(msg)
        row_exists = (
            self.__class__.objects.using(new_kwargs.get("using"))
            .filter(pk=self.pk)
            .exists()
        )
        if row_exists:
            new_kwargs["force_update"] = True
        return new_kwargs

    def save(self, **kwargs):
        kwargs = self.add_force_keyword(kwargs)
        super().save(**kwargs)
