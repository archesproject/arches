def sync_es(search_engine, index="test_resources"):
    search_engine.es.indices.refresh(index=index)
