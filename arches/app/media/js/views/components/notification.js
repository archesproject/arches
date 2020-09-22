define([
    'arches',
    'knockout',
    'moment',
], function(arches, ko, moment) {

    /** 
     * A generic component for displaying notifications
     * @name NotificationViewModel
     **/

    function NotificationViewModel(params) {
        var self = this;

        this.info = ko.observable();

        this.displaytime = moment(params.created).format('dddd, DD MMMM YYYY | hh:mm A');
        this.id = params.id;
        this.message = params.message;
        this.link = params.link;

        this.dismiss = function(parent) {
            $.ajax({
                type: 'POST',
                url: arches.urls.dismiss_notifications,
                data: {"dismissals": JSON.stringify([self.id])},
            }).done(function(data) {
                if (parent) {
                    item = parent.items().find(
                        function(item) { return item.id === self.id; }
                    );
                    parent.items.remove(item);
                }
            });
        };

        this.getExportFile = function() {
            $.ajax({
                type: 'GET',
                url: arches.urls.get_export_file,
                data: {"exportid": self.link}
            }).done(function(data) {
                if (data.url) {
                    window.open(data.url);
                } else {
                    self.info(data.message);
                }
            });
        };
    }

    ko.components.register('notification', {
        viewModel: NotificationViewModel,
        template: {
            require: 'text!templates/views/components/notification.htm'
        }
    });

    return NotificationViewModel;
});