define([
    'knockout', 
    'arches', 
    'js-cookie',
    'templates/views/components/datatypes/reference.htm',
    'views/components/simple-switch',
], function(ko, arches, Cookies, referenceDatatypeTemplate) {

    const viewModel = function(params) {
        const self = this;
        this.search = params.search;
        this.controlledList = params.config.controlledList;
        this.multiValue = params.config.multiValue;
        this.controlledLists = ko.observable();
        this.getControlledLists = async function() {
            const response = await fetch(arches.urls.controlled_lists, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
            });
            if (response.ok) {
                return await response.json(); 
            } else {
                console.error('Failed to fetch controlled lists');
            }
        };
        
        this.init = async function() {
            const lists = await this.getControlledLists();
            this.controlledLists(lists.controlled_lists);
        };

        this.init();
    };


    ko.components.register('reference-datatype-config', {
        viewModel: viewModel,
        template: referenceDatatypeTemplate,
    });
    
    return name;
});
