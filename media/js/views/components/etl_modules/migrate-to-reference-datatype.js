import ko from 'knockout';
import $ from 'jquery';
import uuid from 'uuid';
import arches from 'arches';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import migrateTemplate from 'templates/views/components/etl_modules/migrate-to-reference-datatype.htm';


const ViewModel = function(params) {
    const self = this;
    this.config = params.config;
    this.state = params.state;
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.load_details = params.load_details ?? {};
    this.loadId = params.loadId || uuid.generate();
    this.moduleId = params.etlmoduleid;
    this.formData = new window.FormData();

    this.dropdowngraph = ko.observableArray();
    this.selectedGraph = ko.observable();
    this.origin = ko.observable();
    this.languageCode = ko.observable(arches.activeLanguage);
    this.languages = ko.observableArray(
        (arches.languages || [{ code: arches.activeLanguage, name: arches.activeLanguage }])
            .map(language => ({
                code: language.code,
                name: language.default_direction
                    ? `${language.name} (${language.code})`
                    : language.name || language.code,
            })),
    );

    this.previewing = ko.observable(false);
    this.showPreview = ko.observable(false);
    this.candidateNodes = ko.observableArray([]);

    this.showStatusDetails = ko.observable(false);
    this.formatTime = params.formatTime;
    this.timeDifference = params.timeDifference;
    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.statusDetails = this.selectedLoadEvent()?.load_description?.split('|') ?? [];
    this.alert = params.alert || ko.observable();

    this.canPreview = ko.computed(() => {
        return !!self.selectedGraph() && !!self.origin() && !self.previewing();
    });

    this.canWrite = ko.computed(() => {
        return self.canPreview() && self.showPreview() && self.candidateNodes().length > 0;
    });

    const inputsChanged = ko.computed(() => {
        return [self.selectedGraph(), self.origin(), self.languageCode()].join('|');
    });
    inputsChanged.subscribe(() => {
        self.showPreview(false);
        self.candidateNodes([]);
    });

    this.addAllFormData = () => {
        self.formData = new window.FormData();
        self.formData.append('load_id', self.loadId);
        self.formData.append('module', self.moduleId);
        if (self.selectedGraph()) { self.formData.append('graph_id', self.selectedGraph()); }
        if (self.origin()) { self.formData.append('origin', self.origin()); }
        if (self.languageCode()) { self.formData.append('language_code', self.languageCode()); }
    };

    this.submit = function(action) {
        self.addAllFormData();
        self.formData.append('action', action);
        return $.ajax({
            type: 'POST',
            url: arches.urls.etl_manager,
            data: self.formData,
            cache: false,
            processData: false,
            contentType: false,
        });
    };

    this.fetchGraphs = function() {
        self.dropdowngraph.removeAll();
        self.submit('get_graphs').then(data => {
            data.result.forEach(graph => {
                self.dropdowngraph.push({ graphName: graph.name, graphid: graph.graphid });
            });
        }).fail(err => {
            self.alert(new JsonErrorAlertViewModel('ep-alert-red', err.responseJSON?.data, null, () => {}));
        });
    };

    this.previewCandidates = function() {
        if (!self.canPreview()) { return; }
        self.previewing(true);
        self.submit('get_candidate_nodes').then(data => {
            self.candidateNodes(data.result || []);
            self.showPreview(true);
        }).fail(err => {
            self.alert(new JsonErrorAlertViewModel('ep-alert-red', err.responseJSON?.data, null, () => {}));
        }).always(() => {
            self.previewing(false);
        });
    };

    this.write = function() {
        if (!self.canWrite()) { return; }
        self.showPreview(false);
        params.activeTab('import');
        self.submit('write').fail(err => {
            self.alert(new JsonErrorAlertViewModel('ep-alert-red', err.responseJSON?.data, null, () => {}));
        });
    };

    this.fetchGraphs();
};

ko.components.register('migrate-to-reference-datatype', {
    viewModel: ViewModel,
    template: migrateTemplate,
});

export default ViewModel;
