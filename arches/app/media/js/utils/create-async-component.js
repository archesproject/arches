define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    function generateRandomString(spreadIntervalStart, spreadIntervalEnd) {
        return Math.random().toString(36).substring(spreadIntervalStart,spreadIntervalEnd);
    }

    function injectComponent(htmlElementId, params, viewModel, templatePath, hasAsyncViewModel) {
        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                const injectionSite = document.querySelector(`.${htmlElementId}`);

                injectionSite.innerHTML = e.responseText;
                injectionSite.style.display = 'contents';
                injectionSite.className = null;

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
        const cleanedComponentName = componentName.replace(/\//g, '-');
        const htmlElementId = `${cleanedComponentName}--injection-site-${generateRandomString(2, 6)}`;

        return ko.components.register(componentName, {
            viewModel: function(params){
                this.injectComponent = function(){ injectComponent(htmlElementId, params, viewModel, templatePath, hasAsyncViewModel) }
            },
            template: `
                <div class=${htmlElementId}>
                    <div data-bind="event: {load: $data.injectComponent()}"></div>
                </div>
            `
        });
    }
});
