import ko from 'knockout';

/**
* from http://www.knockmeout.net/2014/10/knockout-cleaning-up.html
* little helper that handles being given a value or prop + value
*
* @param  {string} the request method name
* @return {boolean} true if the method is CSRF safe
*/
const disposeOne = function(propOrValue, value) {
    const disposable = value || propOrValue;

    if (disposable && typeof disposable.dispose === "function") {
        disposable.dispose();
    }
};

const dispose = function(obj) {
    if (!!obj.disposables) {
        ko.utils.arrayForEach(obj.disposables, disposeOne);
    } else {
        ko.utils.objectForEach(obj, disposeOne);
    }
};

export default dispose;
