import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import ListView from 'views/list';
import GraphModel from 'models/graph';


var BranchList = ListView.extend({
    /**
    * A backbone view to manage a list of branch graphs
    * @augments ListView
    * @constructor
    * @name BranchList
    */

    /**
    * initializes the view with optional parameters
    * @memberof BranchList.prototype
    * @param {object} options
    * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
    * @param {boolean} options.branches - an observableArray of branches
    */
    initialize: function(options) {
        var self = this;
        ListView.prototype.initialize.apply(this, arguments);

        this.loading = options.loading || ko.observable(false);
        this.disableAppendButton = options.disableAppendButton || ko.observable(false);
        this.graphModel = options.graphModel;
        this.selectedNode = this.graphModel.get('selectedNode');
        options.branches.forEach(function(branch) {
            branch.selected = ko.observable(false);
            branch.filtered = ko.observable(false);
            branch.graphModel = new GraphModel({
                data: branch,
                selectRoot: false
            });
            this.items.push(branch);
        }, this);
        this.loadingBranchDomains = ko.observable(false);

        this.filtered_items = ko.pureComputed(function() {
            var filtered_items = _.filter(this.items(), function(item){ 
                return !item.filtered() && !item.source_identifier_id; 
            }, this);
            filtered_items.sort(function(a,b) {
                return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1;});
            return filtered_items;
        }, this);

        // update the list of items in the branch list 
        // when any of these properties change
        var valueListener = ko.computed(function() {
            var node = self.selectedNode;
            if(!!node()){
                var oc = node().ontologyclass();
                var datatype = node().datatype();
                var collector = node().isCollector();
                return oc + datatype + collector;
            }
            return false;
        }, this).extend({ deferred: true });

        valueListener.subscribe(function(){
            this.loadDomainConnections();
        }, this);

    },

    /**
    * Downloads domain connection data for each branch (usually an expensive operation)
    * @memberof BranchList.prototype
    */
    loadDomainConnections: function(){
        var self = this;
        var domainConnections = [];

        this.loadingBranchDomains(true);
        this.items().forEach(function(branch, i){
            domainConnections.push(branch.graphModel.loadDomainConnections());
        }, this);

        $.when(...domainConnections)
            .then(function(){
                self.loadingBranchDomains(false);
                self.filterFunction();
            });

    },

    /**
    * Callback function called every time a user types into the filter input box
    * @memberof ListView.prototype
    */
    filterFunction: function(){
        var filter = this.filter().toLowerCase();
        this.items().forEach(function(item){
            var name = typeof item.name === 'string' ? item.name : item.name();
            if (!item.filtered) {
                item.filtered = ko.observable();
            }
            item.filtered(true);
            if(name.toLowerCase().indexOf(filter) !== -1 && this.graphModel.canAppend(item.graphModel)){
                item.filtered(false);
            }
        }, this);
    },


    /**
    * Appends the currently selected branch onto the currently selected node in the graph
    * @memberof BranchList.prototype
    * @param {object} item - the branch object the user selected
    * @param {object} evt - click event object
    */
    appendBranch: function(item, evt){
        var self = this;
        if(this.selectedNode()){
            this.loading(true);
            this.graphModel.appendBranch(this.selectedNode(), null, item.graphModel, function(response, status){
                // this.loading(false); // TODO: @cbyrd 8842 disable page refresh on branch append
                _.delay(_.bind(function(){
                    if(status === 'success'){
                        document.dispatchEvent(
                            new Event('appendBranch')
                        );
                        window.location.reload();  // TODO: @cbyrd 8842 disable page refresh on branch append
                        this.closeForm();
                    }
                }, this), 300, true);
            }, this);
        }
    },

    /**
    * Closes the form and deselects the currently selected branch
    * @memberof BranchList.prototype
    */
    closeForm: function(){
        this.clearSelection();
        this.trigger('close');
    },


});
export default BranchList;
