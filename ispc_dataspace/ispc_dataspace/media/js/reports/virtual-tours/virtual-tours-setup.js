define([
    'module',
    'arches',
    'jquery',
    'utils/get-query-string-parameter'
], function (module, arches, $, getQueryStringParameter) {

    let currentUrl = module.uri;
    urlWithoutQueryString = currentUrl.split(/[?#]/)[0];
    urlWithoutFilename = urlWithoutQueryString.substr(0, urlWithoutQueryString.lastIndexOf('/'))

    var fullscreenImageOff = arches.urls.media + 'img/fullscreen_off_white.svg';
    var fullscreenImageOn = arches.urls.media + 'img/fullscreen_on_white.svg';

    function toggleFullscreen() {
        $('#virtual-tours-render-area').toggleClass('fullscreen');
        $('#fullscreen-button').toggleClass('fullscreen');
        $('#virtual-tours-container').toggleClass('fullscreen');
        
        let button = $('#fullscreen-button');
        if (button.attr('src').indexOf('fullscreen_off_white.svg') != -1) {
            button.attr('src', fullscreenImageOn);
        }
        else {
            button.attr('src', fullscreenImageOff) 
        }
    }

    return {
        setupVirtualTours: function (sourcePath) {

            $('#fullscreen-button').click(toggleFullscreen);

            let virtual_tours_render_area = $('#virtual-tours-render-area');
            virtual_tours_render_area.attr('src', sourcePath);

            // Run in fullscreen if requested through query string
            let fullscreenBool = getQueryStringParameter('fullscreen');
            if (fullscreenBool){
                if (fullscreenBool.toLowerCase() === "true"){
                    toggleFullscreen();
                }
            }
        }
    }

});