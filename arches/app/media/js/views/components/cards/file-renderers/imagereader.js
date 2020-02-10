define(['knockout'], function(ko) {
    return ko.components.register('imagereader', {
        viewModel: function(params) {
            this.params = params;
            this.url = "";
            this.type = "";
            if (this.params.displayContent) {
                this.url = this.params.displayContent.url;
                this.type = this.params.displayContent.type;
            }
            this.fileType = 'image/jpeg';
        },
        template: { require: 'text!templates/views/components/cards/file-renderers/imagereader.htm' }
    });
});
