define(['jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'bindings/plotly',
    'bindings/select2-query'
], function($, _, ko) {
    /**
    * A viewmodel used for generic AFS instrument files
    *
    * @constructor
    * @name AfsInstrumentViewModel
    *
    * @param  {string} params - a configuration object
    */
    var AfsInstrumentViewModel = function(params) {
        var self = this;
        this.params = params;
        this.fileType = 'text/plain';
        this.url = "";
        this.type = "";
        this.loading = ko.observable(true);
        this.commonData = params.state;
        this.fileViewer = params.fileViewer;
        this.filter = ko.observable('');
        this.displayContent = ko.unwrap(this.params.displayContent);
        var localStore = window.localStorage;

        var renderer = this.displayContent.renderer.id;

        var formatDefaults = {
            'title': localStore.getItem(renderer + 'title') || '',
            'titlesize': localStore.getItem(renderer + 'titlesize') || 24, 
            'xaxislabel': localStore.getItem(renderer + 'xaxislabel') || "",
            'xaxislabelsize': localStore.getItem(renderer + 'xaxislabelsize') || 17,
            'yaxislabel': localStore.getItem(renderer + 'yaxislabel') || "",
            'yaxislabelsize': localStore.getItem(renderer + 'yaxislabelsize') || 17,
        };

        if ('chartData' in params.state === false) {
            this.commonData.chartData = ko.observable();
            this.commonData.seriesData = ko.observableArray([]);
            this.commonData.stagedSeries = ko.observableArray([]);
            this.commonData.seriesStyles = ko.observableArray([]);
            this.commonData.compatibleSeries = ko.pureComputed(function(){
                if (self.fileViewer) {
                    var compat = self.fileViewer.card.tiles().filter(function(tile){
                        return self.fileViewer.getUrl(tile).renderer &&
                        self.fileViewer.getUrl(tile).renderer.id === self.fileViewer.displayContent().renderer.id &&
                        self.fileViewer.selected().tileid !== tile.tileid
                    }).map(function(t){return {text: self.fileViewer.getUrl(t).name, id: t.tileid }});
                    return compat;
                }
            });
        }

        if ('chartTitle' in params.state === false) {
            this.commonData.chartTitle = ko.observable(formatDefaults['title']);
            this.commonData.titleSize = ko.observable(formatDefaults['titlesize']);
            this.commonData.xAxisLabel = ko.observable(formatDefaults['xaxislabel']);
            this.commonData.xAxisLabelSize = ko.observable(formatDefaults['xaxislabelsize']);
            this.commonData.yAxisLabel = ko.observable(formatDefaults['yaxislabel']);
            this.commonData.yAxisLabelSize = ko.observable(formatDefaults['yaxislabelsize']);
            this.commonData.selectedSeriesTile = ko.observable(null);
            this.commonData.colorHolder = ko.observable('#ff00ff');
        }

        this.parsedData = this.commonData.parsedData;
        this.chartData = this.commonData.chartData;
        this.chartTitle = this.commonData.chartTitle;
        this.titleSize = this.commonData.titleSize;
        this.xAxisLabel = this.commonData.xAxisLabel;
        this.xAxisLabelSize = this.commonData.xAxisLabelSize;
        this.yAxisLabel = this.commonData.yAxisLabel;
        this.yAxisLabelSize = this.commonData.yAxisLabelSize;
        this.seriesData = this.commonData.seriesData;
        this.stagedSeries = this.commonData.stagedSeries;
        this.selectedSeriesTile = this.commonData.selectedSeriesTile;
        this.seriesStyles = this.commonData.seriesStyles;
        this.colorHolder = this.commonData.colorHolder;
        this.compatibleSeries = this.commonData.compatibleSeries;
        this.primarySeriesColor = this.fileViewer ? JSON.parse(localStore.getItem(renderer + 'series' + this.fileViewer.tile.tileid))?.color : "#3333ff";


        this.selectedSeriesTile.subscribe(function(tile){
            if(tile) {
                var existing = self.seriesStyles().find(function(el){
                    return el["tileid"] === tile.tileid;
                });
                if (existing) { self.colorHolder(existing["color"]); }
            }
        });

        this.colorHolder.subscribe(function(val){
            var existing; 
            var updated;
            var tile;
            if (self.selectedSeriesTile()) {
                tile = self.selectedSeriesTile();
                existing = self.seriesStyles().find(function(el){
                    return el["tileid"] === tile.tileid;
                });
                if (existing && val) {
                    updated = existing;
                    updated["color"] = val;
                    self.seriesStyles.replace(existing, updated);
                    var seriesConfig = JSON.parse(localStore.getItem(renderer + 'series' + tile.tileid));
                    seriesConfig.color = val;
                    localStore.setItem(renderer + 'series' + tile.tileid, JSON.stringify(seriesConfig));
                }
            }
        });

        this.toggleSelected = function(tile) {
            var selectable = (self.seriesData().filter(function(t){return t.tileid === tile.tileid}).length === 1);
            if(!tile || tile == self.selectedSeriesTile()) {
                self.selectedSeriesTile(null);
            } else if (selectable || tile) {
                self.selectedSeriesTile(tile);
            }
        };

        var chartFormattingDetails = {
            'title': this.chartTitle,
            'titlesize': this.titleSize, 
            'xaxislabel': this.xAxisLabel,
            'xaxislabelsize': this.xAxisLabelSize,
            'yaxislabel': this.yAxisLabel,
            'yaxislabelsize': this.yAxisLabelSize
        };

        _.each(chartFormattingDetails, function(val, key) {
            val.subscribe(function(val){
                localStore.setItem(renderer + key, val);
            });
        });

        this.addAllToChart = function(tiles){
            tiles = self.fileViewer ? self.fileViewer.card.tiles() : tiles;
            if (tiles) {
                tiles.forEach(function(tile){
                    if (self.stagedSeries().indexOf(tile.tileid) > -1) {
                        self.addData(tile);
                    }
                });
            }
        }

        this.addData = function(tile) {
            var seriesStyle = {
                "tileid": tile.tileid,
                "color": self.colorHolder()
            };
            var existing = self.seriesStyles().find(function(el){
                return el["tileid"] === tile.tileid;
            });
            var localStoreSeriesConfig = localStore.getItem(renderer + 'series' + tile.tileid);
            if (!localStoreSeriesConfig) {
                localStore.setItem(renderer + 'series' + tile.tileid, JSON.stringify({color: self.colorHolder()}));
            } else {
                seriesStyle.color = JSON.parse(localStoreSeriesConfig).color;
            }
            if (!existing) {
                self.seriesStyles.push(seriesStyle);
            }
            var fileInfo = this.fileViewer.getUrl(tile);
            this.getChartingData(tile.tileid, fileInfo.url, fileInfo.name);
            self.toggleSelected(tile);
        };

        this.removeData = function(tileid) {
            if (!self.selectedSeriesTile()) {
                self.selectedSeriesTile(null);
            } else if (self.selectedSeriesTile().tileid === tileid) {
                self.selectedSeriesTile(null);
            }
            var existing = self.seriesStyles().find(function(el){
                return el["tileid"] === tileid;
            });
            this.seriesData().forEach(function(series) {
                if (series.tileid === tileid) {
                    this.seriesData.remove(series);
                    this.stagedSeries.remove(series.tileid);
                    localStore.removeItem(renderer + 'series' + series.tileid);
                    if (existing) { self.seriesStyles.remove(existing); }
                }
            }, this);
        };

        this.getChartingData = function(tileid, url, name) {
            var notYetLoaded;
            var series = {
                'value': [],
                'count': []
            };
            notYetLoaded = this.seriesData().filter(function(t){return t.tileid === tileid;}).length === 0;
            if (notYetLoaded) {
                $.ajax({
                    url : url,
                    dataType: "text"})
                    .done(function(data) {
                        self.parse(data, series);
                        self.seriesData.push({tileid: tileid, data: series, name: name});
                    }, this);
            }
        };

        this.loadSeriesDataFromLocalStorage = function(){
            var addToChart = [];
            this.compatibleSeries().forEach(function(tile){
                var fullTile;
                var tileMap = self.params.card.tiles().reduce(function(result, item) {
                    result[item.tileid] = item;
                    return result;
                }, {}) ;  
                var item = localStore.getItem(renderer + 'series' + tile.id);
                if (item) {
                    fullTile = tileMap[tile.id];
                    self.stagedSeries.push(fullTile.tileid);
                    addToChart.push(fullTile);
                }
            });
            this.addAllToChart(addToChart);
        };

        this.render  = function() {
            var series = {
                'value': [],
                'count': [],
                'name': this.displayContent.name
            };
            $.ajax({
                url : this.displayContent.url,
                dataType: "text"})
                .done(function(data) {
                    try {
                        self.parse(data, series);
                        // clear the data before you add new data, this fixes a bug in the 
                        // afs file-interpretation step where data wouldn't be updated until 
                        // the file was selected a second time
                        self.chartData(undefined);  
                        self.chartData(series);
                        if(self.fileViewer){
                            self.loadSeriesDataFromLocalStorage();
                        } else {
                            self.seriesData.push({data: series, name: self.displayContent.name});
                        }
                    } catch(e) {
                        self.displayContent.validRenderer(false);
                    }
                    self.loading(false);
                }, this);
        };        

        this.isFiltered = function(t){
            return self.fileViewer.getUrl(t).name.toLowerCase().includes(self.filter().toLowerCase());
        };
            
        this.chartOptions = {
            axis: {
                x: {
                    tick: {
                        count: 5
                    }
                }
            },
            zoom: {
                enabled: true
            }
        };

        if (this.displayContent) {
            this.url = this.displayContent.url;
            this.type = this.displayContent.type;
            if (self.params.context === 'render') {
                self.render();
            }
        }

    };

    return AfsInstrumentViewModel;
});
