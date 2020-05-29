define([], function() {
    var ontologyUtils = {
        /**
         * makeFriendly - makes a shortened name from an fully qalified name 
         * (eg: "http://www.cidoc-crm.org/cidoc-crm/E74_Group")
         *
         * @param  {ontolgoyName} the request method name
         * @return {string}
         */
        makeFriendly: function(ontolgoyName) {
            if (!!ontolgoyName) {
                var parts = ontolgoyName.split("/");
                return parts[parts.length - 1];
            }
            return '';
        }
    };
    return ontologyUtils;
});