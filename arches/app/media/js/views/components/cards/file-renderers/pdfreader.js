import ko from 'knockout';
import pdfReaderTemplate from 'templates/views/components/cards/file-renderers/pdfreader.htm';

export default ko.components.register('pdfreader', {
    viewModel: function (params) {
        this.params = params;
        this.url = "";
        this.type = "";
        this.displayContent = ko.unwrap(this.params.displayContent);
        if (this.displayContent) {
            this.url = this.displayContent.url;
            this.type = this.displayContent.type;
        }
        this.fileType = 'application/pdf';
    },
    template: pdfReaderTemplate,
});
