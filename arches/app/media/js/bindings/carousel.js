import ko from 'knockout';

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

            var indicators = '<div class="carousel-indicators">';
            var slides = '<div class="carousel-inner">';

            for (var i = 0; i < data.length; i++) {
                var item = data[i];
                var active = i === 0 ? ' active' : '';
                var ariaCurrent = i === 0 ? ' aria-current="true"' : '';
                indicators += '<button type="button" data-bs-target="#' + id + '" data-bs-slide-to="' + i + '" class="' + active + '"' + ariaCurrent + '></button>';
                slides += '<div class="carousel-item' + active + '">' +
                    '<img class="d-block w-100" src="' + escapeAttr(ko.unwrap(item.src)) + '" alt="' + escapeAttr(ko.unwrap(item.alt)) + '">' +
                    '</div>';
            }

            indicators += '</div>';
            slides += '</div>';

            var controls =
                '<button class="carousel-control-prev" type="button" data-bs-target="#' + id + '" data-bs-slide="prev">' +
                '<span class="carousel-control-prev-icon" aria-hidden="true"></span></button>' +
                '<button class="carousel-control-next" type="button" data-bs-target="#' + id + '" data-bs-slide="next">' +
                '<span class="carousel-control-next-icon" aria-hidden="true"></span></button>';

            element.innerHTML = indicators + slides + controls;

            import('bootstrap').then(function (bootstrap) {
                new bootstrap.Carousel(element, ko.unwrap(value.options) || {});
            });
        };

        ko.computed(render, null, { disposeWhenNodeIsRemoved: element });
        element.classList.add('carousel', 'slide');

        return { controlsDescendantBindings: true };
    }
};
