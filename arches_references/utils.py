def field_names(instance):
    return {f.name for f in instance.__class__._meta.fields}
