define(['arches', 'knockout', 'uuid'], function (arches, ko, uuid) {
    ko.components.register('domain-value-datatype-config', {
        viewModel: function(params) {
            var self = this;
            this.options = params.config.options;
            var setupOption = function(option) {
                option.remove = function () {
                    self.options.remove(option);
                };
            };
            this.options().forEach(setupOption);
            this.newOptionLabel = ko.observable('');
            this.addNewOption = function () {
                var option = {
                    id: uuid.generate(),
                    selected: false,
                    text: ko.observable(self.newOptionLabel())
                }
                setupOption(option);
                self.options.push(option);
                self.newOptionLabel('');
            }
        },
        template: { require: 'text!datatype-config-templates/domain-value' }
    });
    return name;
});
