import $ from 'jquery';
import arches from 'arches';
import ListView from 'views/list';
import 'bindings/datepicker';
import 'bindings/chosen';
import 'views/components/simple-switch';
import 'views/components/notification';


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

        this.items = options.items;
        this.helploading = options.helploading;

        
        ListView.prototype.initialize.apply(this, arguments);
        
        this.updateList = function() {
            self.helploading(true);
            
            $.ajax({
                type: 'GET',
                url: arches.urls.get_notifications,
                data: {"unread_only": true}
            }).done(function(data) {
                self.items(data.notifications);
                self.helploading(false);
            });
        };

        this.dismissAll = function() {
            var notifs = self.items().map(function(notif) { return notif.id; });
            
            $.ajax({
                type: 'POST',
                url: arches.urls.dismiss_notifications,
                data: {"dismissals": JSON.stringify(notifs)},
            }).done(function() {
                self.items.removeAll();
            });
        };
    }
});

export default NotificationsList;
