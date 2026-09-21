import ko from 'knockout';
import ImporterViewModel from 'viewmodels/base-import-view-model';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone';


const ArchesJsonImportViewModel = function(params) {
    const self = this;

    this.loadDetails = params.load_details || ko.observable();
    this.state = params.state;
    this.loading = params.loading || ko.observable();
    this.moduleId = params.etlmoduleid;
    ImporterViewModel.apply(this, arguments);
    this.loadStatus = ko.observable('ready');
    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.validationErrors = params.validationErrors || ko.observable();
    this.validated = params.validated || ko.observable();
    this.getErrorReport = params.getErrorReport;
    this.getNodeError = params.getNodeError;

    // Replaces resources that already exist rather than failing on them.
    this.overwrite = ko.observable(false);
    // Off writes the tiles but leaves them out of the search index until a
    // manage.py index_database run.
    this.index = ko.observable(true);

    this.showAlert = (data) => {
        self.alert(new AlertViewModel(
            'ep-alert-red',
            data["data"]["title"],
            data["data"]["message"],
            null,
            function(){}
        ));
    };

    // finally: a rejected fetch, or an error page that response.json() cannot
    // parse, would otherwise leave the spinner up with no way back.
    this.addFile = async function(file){
        self.loading(true);
        try {
            self.fileInfo({name: file.name, size: file.size});
            const formData = new window.FormData();
            formData.append('file', file, file.name);
            const response = await self.submit('read', formData);
            const data = await response.json();
            if (response.ok) {
                self.response(data);
                self.loadDetails(data);
            } else {
                self.showAlert(data);
            }
        } finally {
            self.loading(false);
        }
    };

    this.start = async function(){
        self.loading(true);
        try {
            // Posted on 'start' because read/write/celery are separate requests;
            // the server persists this onto the load event.
            const formData = new window.FormData();
            formData.append('overwrite', self.overwrite());
            formData.append('index', self.index());
            const response = await self.submit('start', formData);
            params.activeTab("import");
            if (response.ok) {
                const data = await response.json();
                self.response(data);
                self.write();
            }
        } finally {
            self.loading(false);
        }
    };

    this.write = async function(){
        self.loading(true);
        try {
            const formData = new window.FormData();
            formData.append('load_details', JSON.stringify(self.loadDetails()));
            const response = await self.submit('write', formData);
            const data = await response.json();
            if (response.ok) {
                self.response(data);
            } else {
                self.showAlert(data);
            }
        } finally {
            self.loading(false);
        }
    };
};
export default ArchesJsonImportViewModel;
