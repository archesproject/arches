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
    isAvailable: function() {
        return !!arches.urls.controlled_lists && !!arches.urls.controlled_list_filtered;
    },

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

    getPrefLabel: function(item) {
        const values = ko.unwrap(item?.values) || [];
        const label = values.find(function(value) {
            return value.language_id === arches.activeLanguage && value.valuetype_id === 'prefLabel';
        }) || values.find(function(value) {
            return value.valuetype_id === 'prefLabel';
        });
        return label?.value || arches.translations.unlabeledItem || '';
    },

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
