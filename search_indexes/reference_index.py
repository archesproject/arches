from arches.app.search.base_index import BaseIndex


class ReferenceIndex(BaseIndex):
    def prepare_index(self):
        self.index_metadata = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "folding": {
                            "tokenizer": "whitespace",
                            "filter": ["lowercase", "asciifolding"],
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "item_id": {"type": "keyword"},
                    "uri": {"type": "keyword"},
                    "label_id": {"type": "keyword"},
                    "label": {
                        "analyzer": "whitespace",
                        "type": "text",
                        "fields": {
                            "raw": {"type": "keyword"},
                            "folded": {"analyzer": "folding", "type": "text"},
                        },
                    },
                    "label_type": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "list_id": {"type": "keyword"},
                    "list_name": {"type": "keyword"},
                }
            },
        }
        super(ReferenceIndex, self).prepare_index()

    def get_documents_to_index(self, resourceinstance, tiles):
        return None, None
