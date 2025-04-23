import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import L from 'leaflet';

ko.bindingHandlers.leaflet = {
    init: function (element, valueAccessor, allBindings, viewModel) {
        var config = ko.unwrap(valueAccessor());
        var map = L.map(element, config);
        if (typeof config.afterRender === 'function') {
            config.afterRender(map);
        }

        $(element).mousedown(function (event) {
            event.stopPropagation();
        });
    }
};
ko.bindingHandlers.leaflet.init = ko.bindingHandlers.leaflet.init.bind(ko.bindingHandlers.leaflet);

export default ko.bindingHandlers.leaflet;
