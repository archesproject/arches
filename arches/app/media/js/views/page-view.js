import $ from 'jquery';
import _ from 'underscore';
import Backbone from 'backbone';
import ko from 'knockout';
import arches from 'arches';
import viewData from 'view-data';
import 'bootstrap';
import 'jquery-ui';

class PageView extends Backbone.View {
    initialize(options) {
        options = options || {};

        this.viewModel = options.viewModel ? options.viewModel : {};
        this.viewModel.helploaded = ko.observable(false);
        this.viewModel.helploading = ko.observable(false);
        this.viewModel.helpOpen = ko.observable(false);
        this.viewModel.editsOpen = ko.observable(false);
        this.viewModel.notifsOpen = ko.observable(false);
        this.viewModel.provisionalHistoryList = {};
        this.viewModel.notifsList = {};

        _.defaults(this.viewModel, {
            helpTemplate: ko.observable(viewData.help),
            alert: ko.observable(null),
            loading: ko.observable(false),
            showTabs: ko.observable(false),
            tabsActive: ko.observable(false),
            menuActive: ko.observable(false),
            recentsActive: ko.observable(false),
            unreadNotifs: ko.observable(false),
            dirty: ko.observable(false),
            showConfirmNav: ko.observable(false),
            navDestination: ko.observable(''),
            handleEscKey: () => { },
            shiftFocus: () => { },
            backToTopHandler: null,
            urls: arches.urls,
            navigate: (url, bypass) => {
                if (!bypass && this.viewModel.dirty()) {
                    this.viewModel.navDestination(url);
                    return;
                }
                this.viewModel.alert(null);
                this.viewModel.loading(true);
                window.location.assign(url);
            },
            getHelp: (template) => {
                this.viewModel.helploading(true);
                var el = document.createElement('div');
                $('.ep-help-content').empty();
                $('.ep-help-content').append(el);
                $.ajax({
                    type: "GET",
                    url: arches.urls.help_template,
                    data: { 'template': template }
                }).done((data) => {
                    $(el).html(data);
                    this.viewModel.helploading(false);
                    $(el).find('.ep-help-topic-toggle').click(function () {
                        var sectionEl = $(this).closest('div');
                        var iconEl = $(this).find('i');
                        if (iconEl.hasClass("fa-chevron-right")) {
                            iconEl.removeClass("fa-chevron-right").addClass("fa-chevron-down");
                        } else {
                            iconEl.removeClass("fa-chevron-down").addClass("fa-chevron-right");
                        }
                        var contentEl = $(sectionEl).find('.ep-help-topic-content').first();
                        let contentExpanded = contentEl.css('display');
                        if (contentExpanded) {
                            if (contentExpanded === 'none') {
                                $(this).attr('aria-expanded', 'true');
                            } else if (contentExpanded === 'block') {
                                $(this).attr('aria-expanded', 'false');
                            }
                        }
                        contentEl.slideToggle();
                    });
                    $(el).find('.reloadable-img').click(function () {
                        $(this).attr('src', $(this).attr('src'));
                    });
                });
            },
            getProvisionalHistory: function () { },
            getNotifications: function () { },
            openNotifs: (openButton, escListenScope, closeButton) => {
                this.viewModel.getNotifications();
                this.viewModel.notifsOpen(!this.viewModel.notifsOpen());
                setTimeout(() => { this.viewModel.handleEscKey(openButton, escListenScope, closeButton); }, 500);
            },
            openEdits: (openButton, escListenScope, closeButton) => {
                this.viewModel.getProvisionalHistory();
                this.viewModel.editsOpen(!this.viewModel.editsOpen());
                setTimeout(() => { this.viewModel.handleEscKey(openButton, escListenScope, closeButton); }, 500);
            },
            openHelp: (helpTemplates, openButton, escListenScope, closeButton) => {
                helpTemplates.forEach(template => this.viewModel.getHelp(template));
                this.viewModel.helpOpen(!this.viewModel.helpOpen());
                setTimeout(() => { this.viewModel.handleEscKey(openButton, escListenScope, closeButton); }, 500);
            },
            closeNotifs: () => {
                this.viewModel.getNotifications();
                this.viewModel.notifsOpen(false);
                this.viewModel.shiftFocus('#ep-notifs-button');
            },
            closeEdits: () => {
                this.viewModel.editsOpen(false);
                this.viewModel.shiftFocus('#ep-edits-button');
            },
            closeHelp: () => {
                let el = $('.ep-help-content');
                el.empty();
                this.viewModel.helpOpen(false);
                this.viewModel.shiftFocus('#ep-help-button');
            }
        });

        this.viewModel.translations = arches.translations;

        window.addEventListener('beforeunload', () => {
            this.viewModel.loading(true);
        });

        ko.applyBindings(this.viewModel);
        this.viewModel.getNotifications();
        $('[data-toggle="tooltip"]').tooltip();
    }
}

export default PageView;
