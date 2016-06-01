define(['knockout'], function (ko) {
    return ko.components.register('switch-widget', {
        viewModel: function(params) {
            this.textValue = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder;
        },
        template:
            '<div class="row mar-btm">\
                <div class="form-group">\
                    <label class="col-xs-12 control-label widget-input-label">{{widget.label}}</label>\
                    <div class="col-xs-12 col-md-9 switch-container">\
                        <span class="switch switch-small" data-bind="css: {\'on\': value()}, click: function() { value(!value()); }"><small></small></span>\
                    </div>\
                </div>\
            </div>'
    });
});
