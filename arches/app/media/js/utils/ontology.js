import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';

const ontologyUtils = {
    /**
     * makeFriendly - makes a shortened name from a fully qualified name
     * (eg: "http://www.cidoc-crm.org/cidoc-crm/E74_Group")
     *
     * @param  {ontologyName} the request method name
     * @return {string}
     */
    makeFriendly: function(ontologyName) {
        ontologyName = ko.unwrap(ontologyName);
        if (!!ontologyName) {
            const parts = ontologyName.split("/");
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
                    const data = {
                        'domain_ontology_class': domain,
                        'range_ontology_class': range,
                        'ontologyid': ''
                    };
                    return data;
                },
                dataType: 'json',
                quietMillis: 250,
                processResults: function(data, params) {
                    let ret = data;
                    if (!!params.term && params.term !== "") {
                        ret = data.filter(function(item) {
                            return item.toUpperCase().includes(params.term.toUpperCase());
                        });
                    }
                    ret = ret.map((item) => {
                        return { id: item, text: item };
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
                if (!!value()) {
                    const data = { id: value(), text: value() };
                    const option = new Option(data.text, data.id, true, true);
                    $(el).append(option);
                    callback([data]);
                } else {
                    callback([]);
                }
            }
        };
    }
};

export default ontologyUtils;
