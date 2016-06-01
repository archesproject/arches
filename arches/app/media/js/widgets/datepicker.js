define(['knockout'], function (ko) {
    return ko.components.register('datepicker-widget', {
        viewModel: function(params) {
            this.value = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder;
        },
        template:
        '<div class="row mar-btm">\
            <div class="form-group">\
                <label class="col-xs-12 control-label widget-input-label" for="" data-bind="text:label"></label>\
                <div class="col-xs-12 col-md-9">\
                    <input type="text" data-bind="datepicker: value, placeholder: placeholder" class="form-control input-lg widget-input">\
                </div>\
            </div>\
        </div>'
    });
});
