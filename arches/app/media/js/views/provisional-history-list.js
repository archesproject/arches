import $ from 'jquery';
import _ from 'underscore';
import moment from 'moment';
import ko from 'knockout';
import arches from 'arches';
import ListView from 'views/list';
import dp from 'bindings/datepicker';
import ch from 'bindings/chosen';
import ss from 'views/components/simple-switch';


var ProvisionalHistoryList = ListView.extend({
    /**
    * A backbone view to manage a list of graph nodes
    * @augments ListView
    * @constructor
    * @name ProvisionalHistoryList
    */

    singleSelect: true,

    /**
    * initializes the view with optional parameters
    * @memberof ProvisionalHistoryList.prototype
    * @param {object} options
    */
    initialize: function(options) {
        var self = this;
        var defaultDateRange = "last-30";
        ListView.prototype.initialize.apply(this, arguments);

        this.updateList = function() {
            self.helploading(true);
            self.items.removeAll();
            $.ajax({
                type: 'GET',
                url: arches.urls.tile_history,
                data: {start: this.start(), end: this.end()}
            }).done(function(data) {
                self.helploading(false);
                self.items(_.map(data, function(edit) {
                    edit.displaytime = moment(edit.lasttimestamp).format('DD-MM-YYYY hh:mm a');
                    return edit;
                }));
                if (self.sortDescending() === false) {
                    self.sortAsc();
                }
            });
        };

        this.updateRange = function(value) {
            var today = moment();
            var from = today.format(this.format);
            var to = today.add(1, 'days').format(this.format);
            // Note: for DateTimeFields the end (to) date is non-inclusive in a
            // range query. Therefore the range must be one day longer than would
            // seem necessary.
            // (https://docs.djangoproject.com/en/2.0/ref/models/querysets/#range)
            switch (value) {
            case 'today':
                break;
            case 'last-7':
                from = today.subtract(7, 'days').format(this.format);
                break;
            case 'last-30':
                from = today.subtract(30, 'days').format(this.format);
                break;
            case 'this-week':
                from = today.day(0).format(this.format);
                to = today.day(7).format(this.format);
                break;
            case 'this-month':
                from = today.date(1).format(this.format);
                to = moment().month(today.month() + 1).date(1).format(this.format);
                break;
            case 'this-quarter':
                from = moment().date(1).quarter(today.quarter()).format(this.format);
                to = moment().date(1).quarter(today.quarter() + 1).format(this.format);
                break;
            case 'this-year':
                var first = today.dayOfYear(1);
                from = first.format(this.format);
                to = first.add(1, 'years').format(this.format);
                break;
            default:
                return;
            }
            return {
                start: from,
                end: to
            };
        };

        var dateRange = this.updateRange(defaultDateRange);

        this.items = options.items;
        this.helploading = options.helploading;
        this.start = ko.observable(dateRange.start);
        this.end = ko.observable(dateRange.end);
        this.dateRangeType = ko.observable('custom');
        this.format = 'YYYY-MM-DD';
        this.dateRangeType = ko.observable();
        this.sortDescending = ko.observable(true);

        this.sortAsc = function() {
            self.items.sort(function(a, b) {
                return a.lasttimestamp === b.lasttimestamp ? 0 : (a.lasttimestamp < b.lasttimestamp ? -1 : 1);
            });
        };

        this.sortDesc = function() {
            self.items.sort(function(a, b) {
                return a.lasttimestamp === b.lasttimestamp ? 0 : (a.lasttimestamp > b.lasttimestamp ? -1 : 1);
            });
        };

        this.editResource = function(resourceinstanceid){
            window.open(arches.urls.resource_editor + resourceinstanceid);
        },

        this.sortDescending.subscribe(function(val) {
            if (val === true) {
                self.sortDesc();
            } else {
                self.sortAsc();
            }
        });

        this.dateRangeType(defaultDateRange);

        this.dateRangeType.subscribe(function(value){
            var range = this.updateRange(value);
            this.start(range.start);
            this.end(range.end);
            this.updateList();
        }, this);

    }

});
export default ProvisionalHistoryList;
