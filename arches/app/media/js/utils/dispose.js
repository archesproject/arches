define(['knockout'], function(ko) {
    /**
    * from http://www.knockmeout.net/2014/10/knockout-cleaning-up.html
    * little helper that handles being given a value or prop + value
    *
    * @param  {string} the request method name
    * @return {boolean} true if the method is CSRF safe
    */
    var disposeOne = function(propOrValue, value) {
        var disposable = value || propOrValue;
        //console.log('disposing ' + disposable);

        if (disposable && typeof disposable.dispose === "function") {
            disposable.dispose();
        }
    };

    var dispose = function(obj) {
        if(!!obj.disposables){
            ko.utils.arrayForEach(obj.disposables, disposeOne);
        } else {
            ko.utils.objectForEach(obj, disposeOne);
        }
    };

    return dispose;
});
