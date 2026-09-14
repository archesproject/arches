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

    this.showAlert = (data) => {
        self.alert(new AlertViewModel(
            'ep-alert-red',
            data["data"]["title"],
            data["data"]["message"],
            null,
            function(){}
        ));
    };

    this.addFile = async function(file){
        self.loading(true);
        self.fileInfo({name: file.name, size: file.size});
        const formData = new window.FormData();
        formData.append('file', file, file.name);
        const response = await self.submit('read', formData);
        const data = await response.json();
        self.loading(false);
        if (response.ok) {
            self.response(data);
            self.loadDetails(data);
        } else {
            self.showAlert(data);
        }
    };

    this.start = async function(){
        self.loading(true);
        // Posted on 'start' because read/write/celery are separate requests;
        // the server persists this onto the load event.
        const formData = new window.FormData();
        formData.append('overwrite', self.overwrite());
        const response = await self.submit('start', formData);
        self.loading(false);
        params.activeTab("import");
        if (response.ok) {
            const data = await response.json();
            self.response(data);
            self.write();
        }
    };

    this.write = async function(){
        self.loading(true);
        const formData = new window.FormData();
        formData.append('load_details', JSON.stringify(self.loadDetails()));
        const response = await self.submit('write', formData);
        const data = await response.json();
        self.loading(false);
        if (response.ok) {
            self.response(data);
        } else {
            self.showAlert(data);
        }
    };
};
export default ArchesJsonImportViewModel;
