import ko from 'knockout';
import BaseManagerView from 'views/base-manager';
import data from 'views/plugin-data';
import 'plugins';


if (!data.config) data.config = {};

data.config.loading = ko.observable(false);
data.config.alert = ko.observable(null);
data.config.plugin = data;

export default new BaseManagerView({
    viewModel: {
        loading: data.config.loading,
        alert: data.config.alert,
        plugin: data
    }
});
