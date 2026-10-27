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

    /**
     * getSelect2ConfigForOntologyProperties - select2 config for an ontology property
     *
     * @param  {observable} value - the stored property (an ontology URI, or the id
     *     of a relationship type concept such as Arches' default)
     * @param  {string} domain - domain ontology class
     * @param  {string} range - range ontology class
     * @param  {string} placeholder
     * @param  {boolean} allowClear
     * @param  {string|observable} label - optional label of the stored value,
     *     shown instead of the raw value until another property is chosen
     * @return {object}
     */
    getSelect2ConfigForOntologyProperties: function(value, domain, range, placeholder, allowClear, label) {
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
                    const data = { id: value(), text: ko.unwrap(label) || value() };
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
