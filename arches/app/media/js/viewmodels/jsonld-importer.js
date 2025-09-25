import _ from 'underscore';
import ko from 'knockout';
import ImporterViewModel from 'viewmodels/base-import-view-model';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone';


var JSONLDImportViewModel = function(params) {
    const self = this;

    this.loadDetails = params.load_details || ko.observable();
    this.state = params.state;
    this.loading = params.loading || ko.observable();
    this.data2 = ko.observable(false);
    this.moduleId = params.etlmoduleid;
    ImporterViewModel.apply(this, arguments);
    this.loadStatus = ko.observable('ready');
    this.downloadMode = ko.observable(false);
    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.validationErrors = params.validationErrors || ko.observable();
    this.validated = params.validated || ko.observable();
    this.getErrorReport = params.getErrorReport;
    this.getNodeError = params.getNodeError;

    this.toggleDownloadMode = () => {
        this.downloadMode(!this.downloadMode());
    };

    function getCookie(name) {
        if (!document.cookie) {
            return null;
        }
        const xsrfCookies = document.cookie.split(';')
            .map(c => c.trim())
            .filter(c => c.startsWith(name + '='));

        if (xsrfCookies.length === 0) {
            return null;
        }
        return decodeURIComponent(xsrfCookies[0].split('=')[1]);
    }

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
        if (response.ok) {
            const data = await response.json();
            self.loading(false);
            self.response(data);
            self.loadDetails(data);
        } else {
            self.loading(false);
            const data = await response.json();
            self.showAlert(data);
        }
    };

    this.start = async function(){
        self.loading(true);
        const response = await self.submit('start');
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
        self.loading(false);
        if (response.ok) {
            const data = await response.json();
            self.response(data);
        }
        else {
            const data = await response.json();
            self.showAlert(data);
        }
    };
};
export default JSONLDImportViewModel;
