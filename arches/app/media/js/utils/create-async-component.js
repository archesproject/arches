define(['knockout', 'arches'], function(ko, arches) {
    return function createAsyncComponent(componentName, viewModel, templatePath) {
        const htmlElementId = `${componentName}--injection-site`;
        const params = ko.observable();

        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                const injectionSite = document.querySelector(`#${htmlElementId}`);
                injectionSite.innerHTML = e.responseText;

                ko.cleanNode(injectionSite);
                ko.applyBindings( new viewModel(params()), injectionSite );
            }
        });
        return ko.components.register(componentName, {
            viewModel: function(e){params(e)},
            template: `<div id=${htmlElementId}></div>`
        });
    }
});
