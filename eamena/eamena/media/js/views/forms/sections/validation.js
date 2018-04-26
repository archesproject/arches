define(['jquery', 
    'underscore',], function ($, _) {
        
    return Backbone.View.extend({
        
        // much of this adapted from code found on stack exchange
        isValidDate: function(nodes, node_name){
            
            var valid = true;
            _.each(nodes, function(node){
                if (node["entitytypeid"] == node_name) {
                    
                    var date_string = node["value"];
                    justDate = date_string.split("T")[0];
                    
                    // Deal with empty dates (they're ok!)
                    if(justDate == ""){
                        return;
                    }
                    
                    // Return false if the date has / or \ in it
                    if (justDate.indexOf('/') > -1){
                        valid = false;
                    }
                    if (justDate.indexOf('\\') > -1){
                        valid = false;
                    }

                    // The following was used before to replace / with -, but the new text was
                    // never passed on, and therefore this was a misleading test (/ fails on save)
                    //var replaceDate = justDate.replace(/\//g,"-");

                    // First check for the pattern
                    if(!/^\d{4}\-\d{1,2}\-\d{1,2}$/.test(justDate)){
                        valid = false;
                    }

                    // Parse the date parts, rebuild justDate
                    var parts = justDate.split("-");
                    for (i=1; i==2; i++) {
                        if (parts[i].length == i) {
                            parts[i] = "0"+parts[i];
                        }
                    }
                    justDate = parts.join("-");
                    
                    // make parts into integers for processing
                    var day = parseInt(parts[2], 10);
                    var month = parseInt(parts[1], 10);
                    var year = parseInt(parts[0], 10);

                    // Check the ranges of month and year
                    if(year > 3000 || month == 0 || month > 12){
                        valid = false;
                    }
                    var monthLength = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

                    // Adjust for leap years
                    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0)){
                        monthLength[1] = 29;
                    }
                        
                    // Check the range of the day
                    valid = day > 0 && day <= monthLength[month - 1];
                }
            });
            return valid;
        },
        
        nodesHaveValues: function(nodes, node_names) {
            vals_good = true;
            _.each(nodes, function(node) {
                if (node_names.indexOf(node["entitytypeid"]) > -1) {
                    if (node["value"] === "") {
                        vals_good = false;
                    }
                }
            });
            return vals_good;
        }
    });
});