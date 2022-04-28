define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    function generateRandomString(spreadIntervalStart, spreadIntervalEnd) {
        return Math.random().toString(36).substring(spreadIntervalStart,spreadIntervalEnd);
    }

    function injectComponent(htmlElementId, params, viewModel, templatePath, hasAsyncViewModel) {
        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                const injectionSite = document.querySelector(`#${htmlElementId}`);
                injectionSite.innerHTML = e.responseText;

                if (hasAsyncViewModel === true) {
                    ko.cleanNode(injectionSite);
                    ko.applyBindings( params.asyncViewModel, injectionSite );
                }
                else if (viewModel) {
                    ko.cleanNode(injectionSite);
                    ko.applyBindings( new viewModel(ko.unwrap(params)), injectionSite );
                }
            }
        });
    }

    return function createAsyncComponent(componentName, viewModel, templatePath, hasAsyncViewModel) {
        const htmlElementId = `${componentName}--injection-site-${generateRandomString(2, 6)}`;

        return ko.components.register(componentName, {
            viewModel: function(params){
                this.injectComponent = function(){ injectComponent(htmlElementId, params, viewModel, templatePath, hasAsyncViewModel) }
            },
            template: `
                <div style='width: 100%; height: 100%;' id=${htmlElementId}>
                    <div style='display:none' data-bind="click: $data.injectComponent()"></div>
                </div>
            `
        });
    }
});
