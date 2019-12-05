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
                    url: arches.urls.get_notifications
                }).done(function(data) {
                    console.log(data);
                    self.items(_.filter(data.notifications, function(notif) {
                        notif.displaytime = moment(notif.created).format('DD-MM-YYYY hh:mm a');
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

            this.items = options.items;
            this.helploading = options.helploading;
            this.dateRangeType = ko.observable('custom');
            this.format = 'YYYY-MM-DD';

        }

    });
    return NotificationsList;
});
