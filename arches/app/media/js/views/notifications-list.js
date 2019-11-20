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
        * A backbone view to manage a list of graph nodes
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
                    var dismissed;
                    self.helploading(false);
                    if (self.items().length == 0) {
                        self.items(_.filter(data.notifications, function(notif) {
                            notif.displaytime = moment(notif.created).format('DD-MM-YYYY hh:mm a');
                            return notif.is_read === false;
                        }));
                    } else {
                        dismissed = data.notifications.filter(function(n) { return n.is_read === true; });
                        dismissed.forEach(function(notif){
                            item = self.items().find(function(it) { return it.id === notif.id; });
                            self.items.remove(item);
                        });
                    }
                });
            };

            this.dismiss = function(notifId=false) {
                var notifs;
                if (!notifId) {
                    notifs = self.items().map(function(notif) { return notif.id; });
                } else { notifs = [notifId]; }
                $.ajax({
                    type: 'POST',
                    url: arches.urls.dismiss_notifications,
                    data: {"dismissals": JSON.stringify(notifs)},
                }).done(function(data) {
                    self.updateList();
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
