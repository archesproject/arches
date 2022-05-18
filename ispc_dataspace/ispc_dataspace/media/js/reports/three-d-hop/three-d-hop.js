define([
    'underscore',
    'knockout',
    'viewmodels/report',
    'arches',
    'reports/three-d-hop/three-d-hop-setup',
    'trackball_sphere',
    'trackball_turntable',
    'trackball_turntable_pan',
    'trackball_pantilt',
    'knockstrap',
    'bindings/chosen'
], function (_, ko, ReportViewModel, arches, threeDHopSetup) {

    var configurationMethodDictionary = {

        '1123258a-226e-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.type', getConceptValueAsConstructor(val)); },

        '4fef73c2-226e-11e9-9e1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startPhi', val); },
        '77472ef6-226e-11e9-8bd2-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startTheta', val); },
        '84a2c6fa-226e-11e9-b4cd-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startDistance', val); },
        '92d84f1a-226e-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startPanX', val); },
        'a4030654-226e-11e9-b29f-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startPanY', val); },
        'b772a67c-226e-11e9-ab9d-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.startPanZ', val); },
        '66227432-379f-11e9-aa45-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.startAngleX', val); },
        'a6e8ab62-379f-11e9-ab15-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.startAngleY', val); },
        '43195b86-26e7-11e9-b29f-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxDist', val, 0); },
        '67f05c8e-26e7-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxDist', val, 0); },
        '97b84d6e-26e7-11e9-ab9d-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPhi', val, 0); },
        'b18eb494-26e7-11e9-b4cd-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPhi', val, 1); },
        '1c873974-26e8-11e9-8bd2-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxTheta', val, 0); },
        '2d7ebcb6-26e8-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxTheta', val, 1); },
        '49977ba4-26e8-11e9-ad1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanX', val, 0); },
        '5ca61af2-26e8-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanX', val, 1); },
        '743bc66c-26ed-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanY', val, 0); },
        '8b10fdf8-26ed-11e9-8c52-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanY', val, 1); },
        'b1d2d47a-26ed-11e9-8c52-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanZ', val, 0); },
        'c00d79f0-26ed-11e9-b29f-0242ac170002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxPanZ', val, 1); },
        'e8e22836-379f-11e9-bd96-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxAngleX', val, 0); },
        'f7f8fd72-379f-11e9-bdc8-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxAngleX', val, 1); },
        '24c2900c-37a0-11e9-a987-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxAngleY', val, 0); },
        '37610f5e-37a0-11e9-bdc8-0242ac1d0002': function (config, val) { addProperty(config, 'trackball.trackOptions.minMaxAngleY', val, 1); },

        'af717052-2273-11e9-b4cd-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.centerMode', getConceptValue(val)); },
        '4badaf1c-2274-11e9-ad1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitCenter', val, 0); },
        '41e3ad9c-2274-11e9-ad1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitCenter', val, 1); },
        'cc736a92-2274-11e9-b29f-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitCenter', val, 2); },

        'd3843830-2273-11e9-b7c2-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.radiusMode', getConceptValue(val)); },
        '1553379c-2275-11e9-9e1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitRadius', val, 0); },
        '8954efdc-2275-11e9-b7c2-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitRadius', val, 1); },
        '97d7004a-2275-11e9-8bd2-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.explicitRadius', val, 2); },

        '0b40d042-2276-11e9-8bd2-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.cameraType', getConceptValue(val)); },
        '758debf6-2276-11e9-9e1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.cameraFOV', val); },
        'cb30e982-2276-11e9-ad1e-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.cameraNearFar', val, 0); },
        'da582a92-2276-11e9-b4cd-0242ac170002': function (config, val) { addProperty(config, 'trackball.space.cameraNearFar', val, 1); },

        'd316cfe2-27c9-11e9-8639-0242ac170002': function (config, val) { addProperty(config, 'space.sceneLighting', val); },

        'dd705904-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.translation', val, 0); },
        'dd706228-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.translation', val, 1); },
        'dd70605c-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.translation', val, 2); },

        'dd705468-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.rotation', val, 0); },
        'dd705ae4-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.rotation', val, 1); },
        'dd7055d0-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.rotation', val, 2); },

        'dd70515c-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.scale', val, 0); },
        'dd7052f6-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.scale', val, 1); },
        'dd705ca6-77ec-11e9-85bb-0242c0a84002': function (config, val) { addProperty(config, 'space.transform.scale', val, 2); },
    };

    function getConceptValue(valueid) {
        var val;
        $.ajax({
            type: 'GET',
            url: arches.urls.concept_value,
            data: {
                valueid: valueid
            },
            async: false,
            success: function (response) {
                val = response.value;
            }
        });
        return val;
    }

    function getConceptValueAsConstructor(value) {
        var conceptValue = getConceptValue(value);
        return window[conceptValue];
    }

    function addProperty(object, key, value, index) {
        var keys = key.split('.');
        object = initializeParentProperties(object, keys);

        if (index != null) {
            addArrayProperty(object, keys, value, index)
        } else {
            object[keys[0]] = value;
        }
    }

    function initializeParentProperties(object, keys) {
        while (keys.length > 1) {
            var k = keys.shift();
            if (!object.hasOwnProperty(k)) {
                object[k] = {};
            }

            object = object[k];
        }
        return object;
    }

    function addArrayProperty(object, keys, value, index) {
        var arrayPropertyName = keys[0];
        initializeArrayIfNotExists(object, arrayPropertyName);
        object[arrayPropertyName][index] = value;
    }

    function initializeArrayIfNotExists(object, propertyName) {
        if (!object.hasOwnProperty(propertyName)) {
            object[propertyName] = [];
        }
    }

    function removeDotsFromString(string) {
        return string.replace('.', '-');
    }

    function getExtension(path) {
        return path.split('.').pop();
    }

    function cleanEmptyProperties(object) {
        let parent = object;
        Object.keys(parent).forEach(function (key) {
            const property = parent[key];
            if (property && typeof property === 'object') {
                cleanEmptyProperties(property);
            }
            if (property == null || property === "" || (Array.isArray(property) && property.length === 0)) {
                if (Array.isArray(parent)) {
                    parent.splice(parent[key], 1);
                } else {
                    delete parent[key];
                }
            }
        })
    }

    function addValueToConfiguration(configurationMethodDictionary, configObject, key, value) {
        var addConfigurationMethod = configurationMethodDictionary[key];

        if (addConfigurationMethod) {
            addConfigurationMethod(configObject, value);
        }
    }

    function addMeshProperty(configObject, item) {
        var mesh = {
            url: item.url
        };

        var meshName = removeDotsFromString(item.name);
        addProperty(configObject, `meshes.${meshName}`, mesh);

        return meshName;
    }

    function addInstanceProperty(configObject, meshName){
        var instance = {
            mesh: meshName
        }

        addProperty(configObject, `modelInstances.${meshName}`, instance)
    }

    return ko.components.register('three-d-hop-report', {
        viewModel: function (params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            self.threeDHopFileCount = ko.observable(0);

            if (self.report.get('tiles')) {
                let configObject = {}
                let tiles = self.report.get('tiles');
                tiles.forEach(function (tile) {
                    _.each(tile.data, function (val, key) {

                        if (val == null) {
                            return;
                        }

                        // 3D model file
                        if (Array.isArray(val)) {
                            val.forEach(function (item) {

                                if (item.name) {
                                    var fileExtension = getExtension(item.name);
                                }

                                if (item.status &&
                                    item.status === 'uploaded' &&
                                    (fileExtension == 'ply' || fileExtension == 'nxs')
                                ) {

                                    var meshName = addMeshProperty(configObject, item);
                                    addInstanceProperty(configObject, meshName);
                                }
                            });
                            return;
                        }

                        addValueToConfiguration(configurationMethodDictionary, configObject, key, val)

                    }, self);
                }, self);


                cleanEmptyProperties(configObject);

                if (configObject.meshes) {
                    var threeDHopFileCount = Object.keys(configObject.meshes).length;
                    if (threeDHopFileCount > 0) {
                        self.threeDHopFileCount(threeDHopFileCount);
                        threeDHopSetup.setup3DHOP(configObject);
                    }
                }
            }

            var widgets = [];
            var getCardWidgets = function (card) {
                widgets = widgets.concat(card.model.get('widgets')());
                card.cards().forEach(function (card) {
                    getCardWidgets(card);
                });
            };
            ko.unwrap(self.report.cards).forEach(getCardWidgets);

            this.nodeOptions = ko.observableArray(
                widgets.map(function (widget) {
                    return widget.node
                }).filter(function (node) {
                    return ko.unwrap(node.datatype) === 'file-list';
                })
            );
        },
        template: {
            require: 'text!report-templates/three-d-hop'
        }
    });
});