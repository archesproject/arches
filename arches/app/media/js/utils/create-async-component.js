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

                injectionSite.insertAdjacentHTML('afterend', e.responseText);
                const injectionSiteNextSibling = injectionSite.nextElementSibling;  // gets rendered version of e.responseText

                if (hasAsyncViewModel === true) {
                    ko.cleanNode(injectionSiteNextSibling);
                    ko.applyBindings( params.asyncViewModel, injectionSiteNextSibling);
                }
                else if (viewModel) {
                    ko.cleanNode(injectionSiteNextSibling);
                    ko.applyBindings( new viewModel(ko.unwrap(params)), injectionSiteNextSibling);
                }

                const injectionSiteParent = injectionSite.parentNode;
                injectionSiteParent.removeChild(injectionSite);
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
                <div id=${htmlElementId}>
                    <div data-bind="click: $data.injectComponent()"></div>
                </div>
            `
        });
    }
});
