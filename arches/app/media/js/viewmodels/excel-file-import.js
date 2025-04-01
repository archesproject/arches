import ko from 'knockout';
import ImporterViewModel from 'viewmodels/base-import-view-model';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone'; 


var ExcelFileImportViewModel = function(params) {
    const self = this;
    
    this.loadDetails = params.load_details || ko.observable();
    this.state = params.state;
    this.loading = params.loading || ko.observable();
    this.data2 = ko.observable(false);
    this.moduleId = params.etlmoduleid;
    ImporterViewModel.apply(this, arguments);
    this.selectedTemplate = ko.observable();
    this.loadStatus = ko.observable('ready');
    this.downloadMode = ko.observable(false);
    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.validationErrors = params.validationErrors || ko.observable();
    this.validated = params.validated || ko.observable();
    this.getErrorReport = params.getErrorReport;
    this.getNodeError = params.getNodeError;
    this.templates = ko.observableArray(
        arches.resources.map(resource => ({text: resource.name, id: resource.graphid}))
    );

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

    this.downloadTemplate = async() => {
        const url = arches.urls.etl_manager;
        const formData = new window.FormData();
        formData.append("id", ko.unwrap(this.selectedTemplate));
        formData.append("format", "xls");
        formData.append("module", ko.unwrap(self.moduleId));
        formData.append("action", "download");
        
        const response = await window.fetch(url, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
            headers: {
                "Accept": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        });

        const blob = await response.blob();
        const urlObject = window.URL.createObjectURL(blob);
        const a = window.document.createElement('a');
        window.document.body.appendChild(a);
        a.href = urlObject;
        a.download = `${this.templates().filter(x => x.id == this.selectedTemplate())[0].text}.xlsx`;
        a.click();

        setTimeout(() => {
            window.URL.revokeObjectURL(urlObject);
            window.document.body.removeChild(a);
        }, 0);
        this.loading(false);
    };

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
export default ExcelFileImportViewModel;
