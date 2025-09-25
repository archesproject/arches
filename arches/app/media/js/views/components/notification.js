import $ from 'jquery';
import ko from 'knockout';
import moment from 'moment';
import arches from 'arches';
import notificationTemplate from 'templates/views/components/notification.htm';


/** 
 * A generic component for displaying notifications
 * @name NotificationViewModel
 **/

function NotificationViewModel(params) {
    var self = this;

        
    this.info = ko.observable();

    this.displaytime = moment(params.created).format('dddd, DD MMMM YYYY | hh:mm A');
    this.id = params.id;
    this.loadedResources = params.loaded_resources;
    this.link = params.link;
    this.message = params.message;
    this.files = params.files;
    this.translations = arches.translations;

    this.dismiss = function(parent) {
        $.ajax({
            type: 'POST',
            url: arches.urls.dismiss_notifications,
            data: {"dismissals": JSON.stringify([self.id])},
        }).done(function() {
            if (parent) {
                var item = parent.items().find(
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
    template: notificationTemplate,
});

export default NotificationViewModel;
