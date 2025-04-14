import ko from 'knockout';
import arches from 'arches';
import Cookies from 'js-cookie';
import referenceDatatypeTemplate from 'templates/views/components/datatypes/reference.htm';

const viewModel = function(params) {
    const self = this;
    this.search = params.search;

    if (this.search) {
        params.config = ko.observable({
            controlledList:[],
            placeholder: arches.translations.selectAnOption,
            multiValue: true
        });
    }

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
        this.controlledLists(lists?.controlled_lists);
    };

    this.init();
};


export default ko.components.register('reference-datatype-config', {
    viewModel: viewModel,
    template: referenceDatatypeTemplate,
});