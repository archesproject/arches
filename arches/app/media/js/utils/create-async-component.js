define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    function injectComponent(injectionSite, html, viewModel, params) {
        injectionSite.innerHTML = html;
                
        ko.cleanNode(injectionSite);
        ko.applyBindings( new viewModel(ko.unwrap(params)), injectionSite );
    }

    return function createAsyncComponent(componentName, viewModel, templatePath) {
        const htmlElementId = `${componentName}--injection-site`;
        const params = ko.observable();

        $.ajax({
            type: 'GET',
            url: arches.urls.root + templatePath,
            complete: function(e) {
                const injectionSite = document.querySelector(`#${htmlElementId}`);

                if (injectionSite){
                    injectComponent(injectionSite, e.responseText, viewModel, params());
                }
                else {
                    let intervalCount = 0;

                    const injectionInterval = setInterval(function() {
                        const injectionSite = document.querySelector(`#${htmlElementId}`);

                        if (injectionSite) {
                            injectComponent(injectionSite, e.responseText, viewModel, params());
                            clearInterval(injectionInterval);
                        }
                        else if (intervalCount >= 5) {
                            clearInterval(injectionInterval);
                        }

                        intervalCount += 1;
                    }, 200);
                }
            }
        });

        return ko.components.register(componentName, {
            viewModel: function(e){params(e)},
            template: `<div style='width: 100%; height: 100%;' id=${htmlElementId}></div>`
        });
    }
});
