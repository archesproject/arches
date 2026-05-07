import ko from 'knockout';
import $ from 'jquery';
import 'bootstrap';

function escapeAttr(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

ko.bindingHandlers.carousel = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var value = valueAccessor();

        if (!value.content) {
            throw new Error('content option is required for carousel binding');
        }

        var id = element.id || ko.utils.uniqueId('ks-carousel-');
        element.id = id;

        var items = value.content.data;

        var render = function () {
            var data = ko.unwrap(items);
            if (!data || !data.length) {
                element.innerHTML = '';
                return;
            }

            var indicators = '<ol class="carousel-indicators">';
            var slides = '<div class="carousel-inner">';

            for (var i = 0; i < data.length; i++) {
                var item = data[i];
                var active = i === 0 ? ' active' : '';
                indicators += '<li data-target="#' + id + '" data-slide-to="' + i + '" class="' + active + '"></li>';
                slides += '<div class="item' + active + '">' +
                    '<img src="' + escapeAttr(ko.unwrap(item.src)) + '" alt="' + escapeAttr(ko.unwrap(item.alt)) + '">' +
                    '</div>';
            }

            indicators += '</ol>';
            slides += '</div>';

            var controls = '<a class="left carousel-control" href="#' + id + '" data-slide="prev"><span class="icon-prev"></span></a>' +
                '<a class="right carousel-control" href="#' + id + '" data-slide="next"><span class="icon-next"></span></a>';

            element.innerHTML = indicators + slides + controls;
            $(element).carousel(ko.unwrap(value.options) || {});
        };

        ko.computed(render, null, { disposeWhenNodeIsRemoved: element });
        $(element).addClass('carousel slide');

        return { controlsDescendantBindings: true };
    }
};
