define([
    'arches',
    'knockout'
], function(arches, ko) {
    const standardizeNode = (obj) => {
        if(obj){
            const keys = Object.keys(obj);
            keys.forEach(x => {
                obj[x.toLowerCase().trim()] = obj[x];
            });
        }
    };

    const getRawNodeValue = (resource, ...args) => {
        let rootNode = resource;
        let testPaths = undefined;

        if(typeof(args?.[0]) == 'object'){
            testPaths = args[0]?.testPaths;
        } else {
            testPaths = [args];
        }

        for(path of testPaths){
            let node = rootNode;
            for(let i = 0; i < path.length; ++i){
                standardizeNode(node);
                const pathComponent = path[i];
                node = node?.[pathComponent];
            }
            if(node){
                return node;
            }
        }
    };

    const deleteTile = async (tileid, card) => {
        const tile = card.tiles().find(y => tileid == y.tileid);
        if(tile){
            return $.ajax({
                type: "DELETE",
                url: arches.urls.tile,
                data: JSON.stringify(tile.getData())
            }).success(() => {
                const tiles = card.tiles();
                const tileIndex = tiles.indexOf(tile);
                tiles.splice(tileIndex, 1);
                card.tiles(tiles);
            });
        }
        throw Error("Couldn't delete; tile was not found.")
    };
    const removedTiles = ko.observableArray();

    const checkNestedData = (resource, ...args) => {
        if(!resource) { return false; }
        for (key of Object.keys(resource)){
            if(args.includes(key)){ continue; }
            const rawValue = getRawNodeValue(resource, key);
            if(!rawValue || (typeof (rawValue) !== 'object')) { continue; }
            if(processRawNodeValue(rawValue) != '--'){
                return true;
            } else {
                try{
                if(checkNestedData(rawValue)) {
                    return true;
                }}
                catch(e){
                    console.log(e);
                }
            }
        }
        return false;
    };

    const processRawNodeValue = (rawValue) => {
        if(typeof rawValue === 'string') {
            return rawValue;
        } else if(!rawValue) {
            return '--';
        }
        const nodeValue = rawValue?.['@display_value'] || rawValue?.['display_value'];
        const geojson = rawValue?.geojson;
        if(geojson){
            return geojson;
        }
        
        //strict checks here because some nodeValues (0, false, etc.) should be rendered differently.
        if(nodeValue !== undefined && nodeValue !== null && nodeValue !== ''){
            return $(`<span>${nodeValue}</span>`).text();
        } else {
            return '--';
        }
    };

    return {
        // default table configuration - used for display
        defaultTableConfig: {
            responsive: {
                breakpoints: [
                    {name: 'infinity', width: Infinity},
                    {name: 'bigdesktop', width: 1900},
                    {name: 'meddesktop', width: 1480},
                    {name: 'smalldesktop', width: 1280},
                    {name: 'medium', width: 1188},
                    {name: 'tabletl', width: 1024},
                    {name: 'btwtabllandp', width: 848},
                    {name: 'tabletp', width: 768},
                    {name: 'mobilel', width: 480},
                    {name: 'mobilep', width: 320}
                ]
            },
            paging: false,
            searching: false,
            scrollCollapse: true,
            info: false,
            columnDefs: [{
                orderable: false,
                targets: -1
            }],
        },

        removedTiles: removedTiles,

        // used to collapse sections within a tab
        toggleVisibility: (observable) => { observable(!observable()) },

        deleteTile: async(tileid, card, ...params) => {
            try {
                await deleteTile(tileid, card);
            }
            catch(e) {
                console.log(e);
                return;
            }
            const eventTarget = params?.[1]?.target;
            if(eventTarget) {
                const table = $(eventTarget).closest("table").DataTable();
                removedTiles.push(tileid);
                table.row($(eventTarget).closest("tr")).remove().draw();
            }
        },

        editTile: function(tileid, card){
            if(card){
                const tile = card.tiles().find(y => tileid == y.tileid)
                if(tile){
                    tile.selected(true);
                }
            }
        },

        // Used to add a new tile object to a given card.  If nested card, saves the parent tile for the
        // card and uses the same card underneath the parent tile.
        addNewTile: async (card) => {
            let currentCard = card;
            if(card.parentCard && !card.parent?.tileid){
                await card.parentCard.saveParentTile();
                currentCard = card.parentCard.tiles()?.[0].cards.find(x => x.nodegroupid == card.nodegroupid)
            }
            currentCard.canAdd() ? currentCard.selected(true) : currentCard.tiles()[0].selected(true);
            if(currentCard.cardinality == 'n' || (currentCard.cardinality == '1' && !currentCard.tiles().length)) {
                const currentSubscription = currentCard.selected.subscribe(function(){
                    currentCard.showForm(true);
                    currentSubscription.dispose();
                });
            }
        },

        // builds an object-based dictionary for cards
        createCardDictionary: (cards) => {
            if(!cards){
                return;
            }
            const dictionary = {};
            for(card of cards){
                dictionary[card.model.name()] = card;
            }
            standardizeNode(dictionary)
            return dictionary;
        },

        // extract a value from a resource graph given a specific path (args)
        getRawNodeValue: getRawNodeValue,

        processRawValue: processRawNodeValue,

        getResourceLink: (node) => {
            if(node) {
                const resourceId = node.resourceId;
                if(resourceId){
                    return `${arches.urls.resource}\\${resourceId}`;
                }
            }
        },   
        
        getTileId: (node) => {
            if(node){
                return node?.['@tile_id'];
            }
        },

        getNodeValue: (resource, ...args) => {
            const rawValue = getRawNodeValue(resource, ...args);
            return processRawNodeValue(rawValue);
        },

        // see if there's any node with a valid displayable value.  If yes, return true.
        // potentially useful for deeply nested resources
        nestedDataExists: checkNestedData
    } 
});
