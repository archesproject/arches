define(['knockout', 'plugins/knockout-select2'], function (ko) {
    return ko.components.register('select-widget', {
        viewModel: function(params) {
            this.selectedValue = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder;
            this.options = params.config.options;
        },
        template:
            '<div class="row mar-btm">\
                <div class="form-group">\
                    <label class="col-xs-12 control-label widget-input-label" for="" data-bind="text:label"></label>\
                    <div class="col-xs-12 col-md-9">\
                        <input class="select2 arches-select2-crud-form" data-bind="select2: {value: selectedValue, select2Config: options, placeholder: placeholder}"></input>\
                    </div>\
                </div>\
            </div>'
    });
});
