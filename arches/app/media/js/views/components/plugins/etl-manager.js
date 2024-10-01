define([
    'jquery',
    'knockout',
    'js-cookie',
    'arches',
    'viewmodels/alert',
    'templates/views/components/plugins/etl-manager.htm',
    'utils/load-component-dependencies'
], function($, ko, Cookies, arches, AlertViewModel, ETLManagerTemplate, loadComponentDependencies) {
    return ko.components.register('etl-manager', {
        viewModel: function(params) {
            const self = this;
             
            this.loading = params.loading;
            this.alert = params.alert;
            this.loading(true);
            this.selectedModule = ko.observable();
            this.activeTab = ko.observable();
            this.activeModules = ko.observable('import');
            this.loadEvents = ko.observable();
            this.selectedLoadEvent = ko.observable();
            this.validated = ko.observable();
            this.validationErrors = ko.observableArray();
            this.paginator = ko.observable();

            this.selectedLoadEvent.subscribe(function(val){
                if (val) {
                    self.selectedModule(val.etl_module);
                    self.fetchValidation(val.loadid);
                } else {
                    if (self.loadEvents() && self.loadEvents().length) {
                        self.selectedLoadEvent(self.loadEvents()[0]);
                    }
                }
            });
            this.moduleSearchString = ko.observable('');
            this.taskSearchString = ko.observable('');
            this.tabs = [
                {id: 'start', title: 'Start'},
                {id: 'details', title: 'Task Details'},
                {id: 'import', title: 'Import Tasks'},
                {id: 'export', title: 'Export Tasks'},
            ];
            this.selectModule = function(etlmodule) {
                self.selectedModule(etlmodule);
                self.activeTab("details");
            };

            this.cancel = function() {
                self.selectedModule(null);
                self.activeTab("start");
            };

            this.activeTab.subscribe(val => {
                if (val == "import") {
                    self.loadEvents(null);
                    self.selectedLoadEvent(null);
                    setTimeout(function() {
                        self.fetchLoadEvent(1);
                    }, 300);
                }
            });

            this.fetchLoadEvent = function(page){
                if (self.activeTab() === 'import'){
                    if (!page) {
                        page = self.paginator()?.current_page ? self.paginator().current_page : 1;
                    }
                    const url = arches.urls.etl_manager + "?action=loadEvent&page=" + page;
                    window.fetch(url).then(function(response){
                        if(response.ok){
                            return response.json();
                        }
                    }).then(function(data){
                        data.events.map((event)=> {
                            event.loading = ko.observable(false);
                        });
                        
                        self.loadEvents(data.events);
                        self.paginator(data.paginator);
                        const newSelectedEventData = data.events.find(item => item.loadid === self.selectedLoadEvent().loadid);
                        if (newSelectedEventData && newSelectedEventData.status != self.selectedLoadEvent().status) {
                            self.selectedLoadEvent(newSelectedEventData);
                        } 
                    });
                }
            };

            this.loadEvents.subscribe(function(loadEvents) {
                if (loadEvents) {
                    const loadEventIds = loadEvents.map(loadEvent => loadEvent.loadid);
                    if (!loadEventIds.includes(self.selectedLoadEvent()?.loadid)) {
                        self.selectedLoadEvent(loadEvents[0]);
                    }    
                }
            });

            this.newPage = function(page) {
                if (page) {
                    self.fetchLoadEvent(page);
                }
            };

            this.cleanLoadEvent = function(loadid) {
                const url = `${arches.urls.etl_manager}?action=cleanEvent&loadid=${loadid}`;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data);
                    self.init();
                    self.activeTab("import");
                });
            };
            
            this.reverseTransactions = function(event, undoAlertTitle, undoAlertMessage) {
                this.alert(new AlertViewModel('ep-alert-red', undoAlertTitle, undoAlertMessage, function() {
                    return;
                }, function() {
                    event.loading(true);
                    const formData = new FormData();
                    const url = arches.urls.etl_manager;
                    event.status = 'reversing';
                    formData.append('loadid', event.loadid);
                    formData.append('module', event.etl_module.etlmoduleid);
                    formData.append('action', 'reverse');
                    window.fetch(url,{
                        method: 'POST',
                        body: formData,
                        credentials: 'include',
                        headers: {
                            "X-CSRFToken": Cookies.get('csrftoken')
                        },
                    }).then(function(response) {
                        return response.json();
                    }).then(function() {
                        self.fetchLoadEvent();
                        event.loading(false);
                    });
                }
                ));
            };

            this.fetchStagedData = function(loadid){
                const url = arches.urls.etl_manager + "?action=stagedData&loadid="+loadid;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data);
                });
            };

            this.stopEtl = function(loadid) {
                const url = arches.urls.etl_manager + "?action=stop&loadid="+loadid;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data);
                });
            };

            this.fetchValidation = function(loadid){
                const url = arches.urls.etl_manager + "?action=validate&loadid="+loadid;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    self.validated(true);
                    const errors = data.data;
                    errors.map(error => {
                        error.showDetails = ko.observable(false);
                        error.details = ko.observable();
                        error.nodeAlias = self.selectedLoadEvent()?.load_details?.mapping?.find( (x) => x.field.trim() == error.source.trim())?.node;
                    });
                    self.validationErrors(errors);
                });
            };

            this.getErrorReport = function(loadid){
                const url = arches.urls.etl_manager + "?action=errorReport&loadid="+loadid;
                window.open(url);
            };

            this.getNodeError = function(loadid, error){
                const url = `${arches.urls.etl_manager}?action=nodeError&nodeid=${error.nodeid}&error=${error.error}&loadid=${loadid}`;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    const sampleErrors = data?.data.slice(0,5);
                    self.validationErrors().map(error => {
                        if (error.nodeid === data.data[0].nodeid) {
                            error.details(sampleErrors);
                        }
                    });
                });
            };

            this.formatTime = function(timeString){
                if (timeString){
                    const timeObject = new Date(timeString);
                    return timeObject.toLocaleString();
                } else {
                    return null;
                }
            };

            this.timeDifference = function(endTime, startTime){
                let timeDiff = new Date(endTime) - new Date(startTime);
                const hours = Math.floor(timeDiff / 3600000);
                timeDiff -= hours * 3600000;
                const minutes = Math.floor(timeDiff / 60000);
                timeDiff -= minutes * 60000;
                const seconds = Math.floor(timeDiff / 1000);
                return `${hours}:${('0' + minutes).slice(-2)}:${('0' + seconds).slice(-2)}`;
            };

            this.init = function(){
                const url = arches.urls.etl_manager + "?action=modules";
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    self.etlModules = data.map(function(etl){
                        loadComponentDependencies([`${etl.component}`]);
                        return etl;
                    });
                    self.loading(false);
                });
                this.activeTab("start");
            };
            this.init();
            setInterval(this.fetchLoadEvent, 5000);
        },
        template: ETLManagerTemplate,
    });
});
