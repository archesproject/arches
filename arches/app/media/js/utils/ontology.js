define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
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
                    url: arches.urls.ontology_properties,
                    data: function(requestParams) {
                        var data = {
                            'domain_ontology_class': domain,
                            'range_ontology_class': range,
                            'ontologyid': ''
                        };
                        return data;
                    },
                    dataType: 'json',
                    quietMillis: 250,
                    processResults: function(data, params) {
                        var ret = data;
                        if(!!params.term && params.term !== ""){
                            ret = data.filter(function(item){
                                return item.toUpperCase().includes(params.term.toUpperCase());
                            });
                        }
                        ret = ret.map((item) => {
                            return {id: item, text: item};
                        });
                        return {
                            results: ret
                        };
                    }
                },
                templateResult: function(item) {
                    return ontologyUtils.makeFriendly(item.text);
                },
                templateSelection: function(item) {
                    return ontologyUtils.makeFriendly(item.text);
                },
                initSelection: function(el, callback) {
                    if(!!value()){
                        var data = {id: value(), text: value()};
                        var option = new Option(data.text, data.id, true, true);
                        $(el).append(option);
                        callback([data]);
                    }else{
                        callback([]);
                    }
                }
            };
        }
    };
    return ontologyUtils;
});
