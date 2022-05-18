define([
    'underscore',
    'jquery',
    'knockout',
    'knockout-mapping',
    'viewmodels/report',
    'arches',
    'imagesloaded',
    'twentytwenty',
    'twentytwenty-move',
    'knockstrap',
    'bindings/chosen'
], function(_, $, ko, koMapping, ReportViewModel, arches) {

    function getValue(valueid){
        var val;
        $.ajax({
            type: 'GET',
            url: arches.urls.concept_value,
            data: { valueid: valueid },
            async: false,
            success: function(response){
                val = response.value;
            }
        });
        return val;
    }

    function displayThrobber() {
        $('.loading-mask').css("display", "block");
    }
    
    function hideThrobber() {
        $('.loading-mask').css("display", "none");
    }
    
    return ko.components.register('before-after-image-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            var defaultOffsetPct;
            var orientation;
            var beforeLabel;
            var afterLabel;
            var noOverlay;

            self.imgs = ko.computed(function() {
                var imgs = [];
                var nodes = self.nodes();

                self.tiles().forEach(function(tile) {
                    _.each(tile.data, function(val, key) {

                        val = koMapping.toJS(val);

                        if (key === "2d3a1734-1cb4-11e9-869d-0242ac140002") {
                            defaultOffsetPct = val;
                            return;
                        }

                        if (key === "5f0c5b12-1cb1-11e9-88c3-0242ac140002") {
                            orientation = getValue(val);
                            return;
                        }

                        if (key === "2d908f60-1c0f-11e9-9ce8-0242ac120004") {
                            afterLabel = val;
                            return;
                        }

                        if (key === "10443880-1c0f-11e9-9ce8-0242ac120004") {
                            beforeLabel = val;
                            return;
                        }

                        if (key === "9516a19c-1cb4-11e9-b140-0242ac140002") {
                            noOverlay = val;
                            return;
                        }

                        if (Array.isArray(val)) {
                            val.forEach(function(item) {
                                if (item.status &&
                                    item.type &&
                                    item.status === 'uploaded' &&
                                    item.type.indexOf('image') > -1 &&
                                    _.contains(nodes, key)
                                ) {
                                    var img = {
                                        src: item.url,
                                        alt: item.name
                                    }

                                    if (key === "780108d0-1661-11e9-bf95-0242ac140004"){
                                        img.type = "before"
                                    }
                                    else if (key === "8ce12c52-1662-11e9-bf95-0242ac140004"){
                                        img.type = "after"
                                    }

                                    imgs.push(img);
                                }
                            });
                            return;
                        }
                    }, self);
                }, self);
                if (imgs.length === 0) {
                    imgs = [{
                        src: arches.urls.media + 'img/photo_missing.png',
                        alt: ''
                    }];
                }
                return imgs;
            });

            if (self.imgs().length > 1) {
                var beforeImg = self.imgs().find(img => {
                    return img.type === 'before'
                });
                var afterImage = self.imgs().find(img => {
                    return img.type === 'after'
                });

                $('#before-image').attr('src', beforeImg.src);
                $('#before-image').attr('alt', beforeImg.alt);

                $('#after-image').attr('src', afterImage.src);
                $('#after-image').attr('alt', afterImage.alt);

                $('#before-after-image-container')
                    .imagesLoaded()
                    .progress(function () {
                        displayThrobber();
                    })
                    .done(function () {
                        hideThrobber();
                        $('#before-after-image-container').twentytwenty({
                            default_offset_pct: defaultOffsetPct,
                            orientation: orientation.toLowerCase(),
                            before_label: beforeLabel,
                            after_label: afterLabel,
                            no_overlay: noOverlay
                        });

                        $(window).resize();
                    });
            }
            
            var widgets = [];
            var getCardWidgets = function(card) {
                widgets = widgets.concat(card.model.get('widgets')());
                card.cards().forEach(function(card) {
                    getCardWidgets(card);
                });
            };
            ko.unwrap(self.report.cards).forEach(getCardWidgets);
            this.nodeOptions = ko.observableArray(
                widgets.map(function(widget) {
                    return widget.node;
                }).filter(function(node) {
                    return ko.unwrap(node.datatype) === 'file-list';
                })
            );
        },
        template: {
            require: 'text!report-templates/before-after-image'
        }
    });
});