def looks_like_api_call(request):
    known_api_paths_without_api_signposting = [
        # Until these are renamed for consistency, just list them.
        "arches.app.views.workflow_history",
    ]
    if "/api/" in request.path:
        return True
    if not request.resolver_match:
        return False
    if ".api." in request.resolver_match.func.__module__:
        return True
    if (
        request.resolver_match.func.__module__
        in known_api_paths_without_api_signposting
    ):
        return True
    return False
