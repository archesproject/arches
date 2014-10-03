require([
    'jquery',
    'bootstrap'
], function($) {
    setTimeout(function() {
        $("#login-failed-alert").alert('close');
    }, 1000);
});