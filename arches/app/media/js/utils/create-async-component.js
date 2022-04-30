define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    function generateRandomString(spreadIntervalStart, spreadIntervalEnd) {
        return Math.random().toString(36).substring(spreadIntervalStart,spreadIntervalEnd);
    }

    function injectComponent(injectionSite, componentName, params, viewModel, templatePath, hasAsyncViewModel) {
        const cleanedComponentName = componentName.replace(/\//g, '-');
        const htmlElementId = `${cleanedComponentName}--injection-site-${generateRandomString(2, 6)}`;

        injectionSite.style.display = 'contents';
        injectionSite.id = htmlElementId;

        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                injectionSite.innerHTML = e.responseText;

                if (hasAsyncViewModel === true) {
                    ko.cleanNode(injectionSite);
                    ko.applyBindings( params.asyncViewModel, injectionSite);
                }
                else if (viewModel) {
                    ko.cleanNode(injectionSite);
                    ko.applyBindings( new viewModel(ko.unwrap(params)), injectionSite);
                }
            }
        });
    }

    return function createAsyncComponent(componentName, viewModel, templatePath, hasAsyncViewModel) {
        return ko.components.register(componentName, {
            viewModel: function(params){
                this.injectComponent = function(injectionSite){ injectComponent(injectionSite, componentName, params, viewModel, templatePath, hasAsyncViewModel) }
            },
            template: `
                <div>
                    <div data-bind="event: {load: $data.injectComponent($element.parentElement)}"></div>
                </div>
            `
        });
    }
});
