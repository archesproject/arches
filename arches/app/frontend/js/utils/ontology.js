define(['arches', 'knockout'], function(arches, ko) {
    var ontologyUtils = {
        /**
         * makeFriendly - makes a shortened name from an fully qalified name
         * (eg: "http://www.cidoc-crm.org/cidoc-crm/E74_Group")
         *
         * @param  {ontologyName} the request method name
         * @return {string}
         */
        makeFriendly: function(ontologyName) {
            ontologyName = ko.unwrap(ontologyName);
            if (!!ontologyName) {
                var parts = ontologyName.split("/");
                return parts[parts.length - 1];
            }
            return '';
        },

        getSelect2ConfigForOntologyProperties: function(value, domain, range, placeholder, allowClear) {
            return {
                value: value,
                clickBubble: false,
                placeholder: placeholder,
                closeOnSelect: true,
                allowClear: allowClear || false,
                ajax: {
                    url: function() {
                        return arches.urls.ontology_properties;
                    },
                    data: function(term, page) {
                        var data = {
                            'domain_ontology_class': domain,
                            'range_ontology_class': range,
                            'ontologyid': ''
                        };
                        return data;
                    },
                    dataType: 'json',
                    quietMillis: 250,
                    results: function(data, page, query) {
                        var ret = data;
                        if(query.term !== ""){
                            ret = data.filter(function(item){
                                return item.toUpperCase().includes(query.term.toUpperCase());
                            });
                        }
                        return {
                            results: ret
                        };
                    }
                },
                id: function(item) {
                    return item;
                },
                formatResult: ontologyUtils.makeFriendly,
                formatSelection: ontologyUtils.makeFriendly,
                initSelection: function(el, callback) {
                    callback(value());
                }
            };
        }
    };
    return ontologyUtils;
});
