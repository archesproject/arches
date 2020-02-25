from arches.app.search.base_index import BaseIndex


class SampleIndex(BaseIndex):
    def prepare_index(self):
        self.index_metadata = {"mappings": {"_doc": {"properties": {"tile_count": {"type": "keyword"}, "graph_id": {"type": "keyword"}}}}}
        super(SampleIndex, self).prepare_index()

    def get_documents_to_index(self, resourceinstance, tiles):
        return ({"tile_count": len(tiles), "graph_id": resourceinstance.graph_id}, str(resourceinstance.resourceinstanceid))
