from arches.app.search.base_index import BaseIndex


class ReferenceIndex(BaseIndex):
    def prepare_index(self):
        self.index_metadata = {
            "mappings": {
                "properties": {
                    "item_id": {"type": "keyword"},
                    "uri": {"type": "keyword"},
                    "label_id": {"type": "keyword"},
                    "label": {"type": "keyword"},
                    "label_type": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "list_id": {"type": "keyword"},
                    "list_name": {"type": "keyword"},
                }
            }
        }
        super(ReferenceIndex, self).prepare_index()

    def get_documents_to_index(self, resourceinstance, tiles):
        return None, None
