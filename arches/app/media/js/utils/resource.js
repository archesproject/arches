define(['arches'], function(arches) {
    var resourceLookup = {};
    var resourceUtils = {
        /**
         * lookupResourceInstanceData - gets resource instance data from Elastic Search
         *
         * @param  {resourceid} the id of the Resouce Instance
         * @return {object}
         */
        lookupResourceInstanceData: function(resourceid) {
            if (resourceLookup[resourceid]) {
                return Promise.resolve(resourceLookup[resourceid]);
            } else {
                return window.fetch(arches.urls.search_results + "?id=" + resourceid)
                    .then(function(response) {
                        if (response.ok) {
                            return response.json();
                        }
                    })
                    .then(function(json) {
                        resourceLookup[resourceid] = json["results"]["hits"]["hits"][0];
                        return resourceLookup[resourceid];
                    });
            }
        }
    };
    return resourceUtils;
});