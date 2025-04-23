import ko from 'knockout';

/**
* A base viewmodel for functions
*
* @constructor
* @name CardMultiSelect
*
* @param  {string} params - a configuration object
*/
var CardMultiSelect = function() {
    this.card.staging = ko.observableArray();
    this.staging = this.card.staging;
    var self = this;
    this.card.stageTile = function(tile, e){
        e.preventDefault(e); 
        if (self.staging.indexOf(tile.tileid) < 0) {
            self.staging.push(tile.tileid);
        } else {
            self.staging.remove(tile.tileid);
        }
    };
};
export default CardMultiSelect;
