import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';

/**
 * Utilities for reading controlled lists (provided by the arches_controlled_lists
 * application) without taking a hard dependency on it. Everything here is routed
 * through arches.urls, which that application contributes, so callers must check
 * isAvailable() before offering a controlled list as an option.
 */

const listCache = {};
let controlledListsPromise;

const controlledListUtils = {
    /**
     * isAvailable - whether the controlled list api is present in this install
     *
     * @return {boolean}
     */
    isAvailable: function() {
        return !!arches.urls.controlled_lists && !!arches.urls.controlled_list_filtered;
    },

    /**
     * getControlledLists - the lists a user can choose from, cached for the
     * lifetime of the page
     *
     * @return {Promise} resolves to a list of {id, name} objects
     */
    getControlledLists: function() {
        if (!controlledListsPromise) {
            controlledListsPromise = window.fetch(arches.urls.controlled_lists)
                .then(function(response) {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error(arches.translations.reNetworkReponseError);
                })
                .then(function(json) {
                    return json.controlled_lists || [];
                });
        }
        return controlledListsPromise;
    },

    /**
     * getListItems - the items of a single list, flattened into hierarchical
     * order, cached per list
     *
     * @param  {listId} the controlled list id
     * @return {Promise} resolves to a list of items
     */
    getListItems: function(listId) {
        listId = ko.unwrap(listId);
        if (!listId) {
            return Promise.resolve([]);
        }
        if (!listCache[listId]) {
            listCache[listId] = window.fetch(arches.urls.controlled_list_filtered(listId) + '?flat=true')
                .then(function(response) {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error(arches.translations.reNetworkReponseError);
                })
                .then(function(json) {
                    return json.items || [];
                });
        }
        return listCache[listId];
    },

    /**
     * getPrefLabel - the label of a list item in the active language
     *
     * @param  {item} a controlled list item
     * @return {string}
     */
    getPrefLabel: function(item) {
        const values = ko.unwrap(item?.values) || [];
        const label = values.find(function(value) {
            return value.language_id === arches.activeLanguage && value.valuetype_id === 'prefLabel';
        }) || values.find(function(value) {
            return value.valuetype_id === 'prefLabel';
        });
        return label?.value || arches.translations.unlabeledItem || '';
    },

    /**
     * getSelect2ConfigForControlledListItems - a select2 config for choosing a
     * single item of a controlled list. The item's uri is what gets stored, so
     * that the value remains a plain string like an ontology property.
     *
     * @param  {value} observable holding the selected item's uri
     * @param  {listId} the controlled list to choose from
     * @param  {placeholder} placeholder text
     * @param  {allowClear} whether the selection can be cleared
     * @return {object} a select2 config
     */
    /**
     * findItemByUri - locate an item by its uri. A list item's uri is generated from
     * PUBLIC_SERVER_ADDRESS (or supplied by an import), so a uri stored in a node config
     * can be stale or belong to another environment. Fall back to matching the item id,
     * which is the trailing segment of a generated uri.
     *
     * @param  {items} the list's items
     * @param  {uri} the stored value
     * @return {object} the matching item, or undefined
     */
    findItemByUri: function(items, uri) {
        if (!uri) {
            return undefined;
        }
        const match = items.find(function(item) {
            return item.uri === uri;
        });
        if (match) {
            return match;
        }
        const trailingSegment = String(uri).split('/').pop();
        return items.find(function(item) {
            return item.id === trailingSegment;
        });
    },

    getSelect2ConfigForControlledListItems: function(value, listId, placeholder, allowClear) {
        return {
            value: value,
            clickBubble: false,
            placeholder: placeholder,
            closeOnSelect: true,
            allowClear: allowClear || false,
            escapeMarkup: function(markup) {
                return markup;
            },
            ajax: {
                transport: function(params, success, failure) {
                    controlledListUtils.getListItems(listId)
                        .then(success)
                        .catch(failure);
                    // selectWoo inspects the returned request for a status property
                    return {};
                },
                data: function(requestParams) {
                    return { term: requestParams.term || '' };
                },
                processResults: function(items, params) {
                    let ret = items || [];
                    const term = (params?.term || '').toLowerCase();
                    if (term !== '') {
                        ret = ret.filter(function(item) {
                            return !item.guide
                                && controlledListUtils.getPrefLabel(item).toLowerCase().includes(term);
                        });
                    }
                    return {
                        results: ret.map(function(item) {
                            return {
                                id: item.uri,
                                text: controlledListUtils.getPrefLabel(item),
                                depth: term === '' ? item.depth : 0,
                                parentPath: term === '' ? '' : item.parent_path,
                                disabled: !!item.guide
                            };
                        })
                    };
                }
            },
            templateResult: function(item) {
                if (item.loading) {
                    return item.text;
                }
                if (item.parentPath) {
                    return item.text
                        + '<span style="display:block;font-size:0.85em;opacity:0.6;">('
                        + item.parentPath + ')</span>';
                }
                return '&nbsp;&nbsp;&nbsp;&nbsp;'.repeat(item.depth || 0) + item.text;
            },
            templateSelection: function(item) {
                return item.text;
            },
            initSelection: function(el, callback) {
                if (!value()) {
                    callback([]);
                    return;
                }
                controlledListUtils.getListItems(listId)
                    .then(function(items) {
                        const item = controlledListUtils.findItemByUri(items, value());
                        const data = {
                            id: value(),
                            text: item ? controlledListUtils.getPrefLabel(item) : value()
                        };
                        $(el).append(new Option(data.text, data.id, true, true));
                        callback([data]);
                    })
                    .catch(function() {
                        const data = { id: value(), text: value() };
                        $(el).append(new Option(data.text, data.id, true, true));
                        callback([data]);
                    });
            }
        };
    }
};

export default controlledListUtils;
