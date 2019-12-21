define([
    'jquery',
    'underscore',
    'moment',
    'knockout',
    'arches',
    'views/list',
    'bindings/datepicker',
    'bindings/chosen',
    'views/components/simple-switch'
], function($, _, moment, ko, arches, ListView) {
    var NotificationsList = ListView.extend({
        /**
        * A backbone view to manage a list of notification records
        * @augments ListView
        * @constructor
        * @name NotificationsList
        */

        singleSelect: true,

        initialize: function(options) {
            var self = this;
            ListView.prototype.initialize.apply(this, arguments);

            this.updateList = function() {
                self.helploading(true);
                $.ajax({
                    type: 'GET',
                    url: arches.urls.get_notifications,
                    data: {"unread_only": true}
                }).done(function(data) {
                    self.items(_.filter(data.notifications, function(notif) {
                        notif.displaytime = moment(notif.created).format('dddd, DD MMMM YYYY | hh:mm A');
                        notif.info = ko.observable();
                        return notif.isread === false;
                    }));
                    self.helploading(false);
                });
            };

            this.dismiss = function(notifId) {
                var notifs, item;
                if (!notifId) { // i.e. dismissAll
                    notifs = self.items().map(function(notif) { return notif.id; });
                    self.items.removeAll();
                } else {
                    notifs = [notifId];
                    item = self.items().find(function(it) { return it.id === notifId; });
                    self.items.remove(item);
                }
                $.ajax({
                    type: 'POST',
                    url: arches.urls.dismiss_notifications,
                    data: {"dismissals": JSON.stringify(notifs)},
                });
            };

            this.getExportFile = function(item) {
                $.ajax({
                    type: 'GET',
                    url: arches.urls.get_export_file,
                    data: {"exportid": item.link}
                }).done(function(data) {
                    if (data.url) {
                        window.open(data.url);
                    } else {
                        item.info(data.message);
                    }
                });
            };

            this.items = options.items;
            this.helploading = options.helploading;
            this.dateRangeType = ko.observable('custom');
            this.format = 'YYYY-MM-DD';

        }

    });
    return NotificationsList;
});
