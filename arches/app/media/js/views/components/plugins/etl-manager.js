define([
    'knockout',
    'arches',
    'js-cookie'
], function(ko, arches, Cookies) {
    return ko.components.register('etl-manager', {
        viewModel: function(params) {
            const self = this;
            this.loading = params.loading;
            this.alert = params.alert;
            this.loading(true);
            this.selectedModule = ko.observable();
            this.activeTab = ko.observable();
            this.isImport = ko.observable(true);
            this.loadEvents = ko.observable();
            this.selectedLoadEvent = ko.observable();
            this.validated = ko.observable();
            this.validationError = ko.observableArray();

            this.selectedLoadEvent.subscribe(function(val){
                self.fetchValidation(val.loadid);
            })
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
            this.selectedModule.subscribe(val => console.log(val))

            this.fetchLoadEvent = function(){
                const url = arches.urls.etl_manager + "?action=loadEvent";
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    data.sort((a,b) => Date.parse(b.load_start_time) - Date.parse(a.load_start_time));
                    self.loadEvents(data);
                    self.selectedLoadEvent(data[0]);
                });
            };

            this.cleanLoadEvent = function(loadid) {
                const url = arches.urls.etl_manager + "?action=cleanEvent&loadid="+loadid;
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

            this.reverseTransactions = function(loadid) {
                self.loading(true);
                $.ajax({
                    type: "POST",
                    url: arches.urls.transaction_reverse(loadid)
                }).then(function() {
                    self.loading(false);
                });
            };

            this.formatUserName = function(event){
                if (event.first_name || event.last_name) {
                    return [event.first_name, event.last_name].join(" ");
                } else {
                    return event.username;
                }
            }

            this.fetchStagedData = function(loadid){
                const url = arches.urls.etl_manager + "?action=stagedData&loadid="+loadid;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data)
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
                    self.validationError(data.data);
                });
            };

            this.formatTime = function(timeString){
                if (timeString){
                    timeObject = new Date(timeString);
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
            }

            this.init = function(){
                const url = arches.urls.etl_manager + "?action=modules";
                window.fetch(url).then(function(response){
                        if(response.ok){
                            return response.json();
                    }
                    }).then(function(data){
                        self.etlModules = data.map(function(etl){
                            // etl.config.loading = self.loading;
                            etl.alert = self.alert;
                            require([etl.component]);
                            return etl;
                        });
                        self.loading(false);
                    });
                    this.activeTab("start");
            };

            this.init();
        },
        template: { require: 'text!templates/views/components/plugins/etl-manager.htm' }
    });
});
