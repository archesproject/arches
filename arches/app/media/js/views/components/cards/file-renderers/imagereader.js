define(['knockout', 'templates/views/components/cards/file-renderers/imagereader.htm'], function(ko, imageReaderTemplate) {
    return ko.components.register('imagereader', {
        viewModel: function(params) {
            this.params = params;
            this.url = "";
            this.type = "";
            this.displayContent = ko.unwrap(this.params.displayContent);
            if (this.displayContent) {
                this.url = this.displayContent.url;
                this.type = this.displayContent.type;
            }
            this.fileType = 'image/jpeg';
        },
        template: imageReaderTemplate,
    });
});
