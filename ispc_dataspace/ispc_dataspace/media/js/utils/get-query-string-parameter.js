define(function(){
    return function(parameterName){
        let params = (new URL(document.location)).searchParams;
        return params.get(parameterName);
    }
})