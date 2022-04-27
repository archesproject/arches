define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    function injectComponent(htmlElementId, params, viewModel, templatePath) {
        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                const injectionSite = document.querySelector(`#${htmlElementId}`);
                injectionSite.innerHTML = e.responseText;
                
                ko.cleanNode(injectionSite);
                ko.applyBindings( new viewModel(ko.unwrap(params)), injectionSite );
            }
        });
    }

    return function createAsyncComponent(componentName, viewModel, templatePath) {
        const htmlElementId = `${componentName}--injection-site`;

        return ko.components.register(componentName, {
            viewModel: function(params){
                this.injectComponent = function(){ injectComponent(htmlElementId, params, viewModel, templatePath) }
            },
            template: `
                <div style='display:none' data-bind="click: $data.injectComponent()"></div>
                <div style='width: 100%; height: 100%;' id=${htmlElementId}></div>
            `
        });
    }
});
