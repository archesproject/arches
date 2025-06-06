class BaseFunction(object):
    def __init__(self, config=None, nodegroup_id=None):
        self.config = config
        self.nodegroup_id = nodegroup_id

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError

    # occurrs after Tile.save
    def post_save(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def on_import(self, *args, **kwargs):
        raise NotImplementedError

    def on_update_lifecycle_state(
        self, resource_instance, current_state, new_state, request=None, context=None
    ):
        """
        Called on update of the lifecycle state of a resource instance.
        This method should be overridden by subclasses to implement specific logic.
        """
        raise NotImplementedError

    # saves changes to the function itself
    def after_function_save(self, *args, **kwargs):
        raise NotImplementedError
