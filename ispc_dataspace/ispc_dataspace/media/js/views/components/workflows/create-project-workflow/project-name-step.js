define([
    'arches',
    'uuid',
    'knockout',
    'viewmodels/card',
], function(arches, uuid, ko) {
   
    function viewModel(params) {

        var self = this;
        const nameNodeGroupId = '0b926359-ca85-11e9-ac9c-a4d18cec433a';
        const typeNodeGroupId = '0b92b8c0-ca85-11e9-adef-a4d18cec433a';

        const getProp = function(key, prop) {
            if (ko.unwrap(params.value) && params.value()[key]) {
                return prop ? params.value()[key][prop] : params.value()[key];
            } else {
                return null;
            } 
        };

        let typeTileId = getProp('type', 'tileid');
        let nameTileId = getProp('name', 'tileid');

        this.projectResourceId = ko.observable(getProp('projectResourceId'));
        this.typeValue = ko.observable(getProp('type', 'value'));
        this.nameValue = ko.observable(getProp('name', 'value'));

        const snapshot = {
            typeValue: self.typeValue(),
            nameValue: self.nameValue(),
        };

        this.updatedValue = ko.pureComputed(function(){
            return {
                projectResourceId: self.projectResourceId(),
                name: {value: self.nameValue(), tileid: nameTileId},
                type: {value: self.typeValue(), tileid: typeTileId},
            };
        });

        this.updatedValue.subscribe(function(val){
            params.value(val);
        });

        this.buildTile = function(data, nodeGroupId, resourceid, tileid) {
            let res = {
                "tileid": tileid || "",
                "nodegroup_id": nodeGroupId,
                "parenttile_id": null,
                "resourceinstance_id": resourceid,
                "sortorder": 0,
                "tiles": {},
                "data": {},
                "transaction_id": params.form.workflowId
            };
            res.data = data;

            return res;
        };

        this.saveTile = function(data, nodeGroupId, resourceid, tileid) {
            let tile = self.buildTile(data, nodeGroupId, resourceid, tileid);
            return window.fetch(arches.urls.api_tiles(tileid || uuid.generate()), {
                method: 'POST',
                credentials: 'include',
                body: JSON.stringify(tile),
                headers: {
                    'Content-Type': 'application/json'
                },
            }).then(function(response) {
                if (response.ok) {
                    return response.json();
                }
            });
        };

        params.form.reset = function(){
            self.typeValue(snapshot.typeValue);
            self.nameValue(snapshot.nameValue);
            // params.form.hasUnsavedData(false);
        };

        params.form.save = function() {
            params.form.complete(false);
            if (!self.nameValue()){
                params.form.error(new Error("Missing Required Value"));
                params.pageVm.alert(new params.form.AlertViewModel('ep-alert-red', "Missing Required Value", "Name is required."));
                return;
            }
    
            const nameTileData = {
                "0b92cf5c-ca85-11e9-95b1-a4d18cec433a": self.nameValue(),
                "0b92d5a3-ca85-11e9-8ea8-a4d18cec433a": null,
                "0b92de3d-ca85-11e9-affe-a4d18cec433a": null,
                "0b92f8cc-ca85-11e9-8c26-a4d18cec433a": [
                    "bc35776b-996f-4fc1-bd25-9f6432c1f349"
                ],
                "0b930757-ca85-11e9-a268-a4d18cec433a": [
                    "7d069762-bd96-44b8-afc8-4761389105c5"
                ]
            };

            const typeTileData = {
                "0b92b8c0-ca85-11e9-adef-a4d18cec433a": self.typeValue()
            };

            return self.saveTile(nameTileData, nameNodeGroupId, self.projectResourceId(), nameTileId)
                .then(function(data) {
                    nameTileId = data.tileid;
                    self.projectResourceId(data.resourceinstance_id);
                    return self.saveTile(typeTileData, typeNodeGroupId, data.resourceinstance_id, typeTileId);
                })
                .then(function(data) {
                    typeTileId = data.tileid;
                    params.form.savedData(params.form.value());
                    params.form.complete(true);
                    params.form.dirty(false);
                    params.pageVm.alert("");
                });
        };
    }

    ko.components.register('project-name-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/create-project-workflow/project-name-step.htm'
        }
    });

    return viewModel;
});
