from arches.app.functions.base import BaseFunction

class LocalFileStorageFunction(BaseFunction):
    def run(self):
        self.save(None, None)

    def save(self, resource, config):
        print 'save file'
        pass