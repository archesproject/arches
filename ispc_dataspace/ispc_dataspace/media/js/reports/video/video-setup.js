define([
    'module',
    'arches',
    'jquery',
    'utils/get-query-string-parameter'
], function (module, arches, $, getQueryStringParameter) {

    let currentUrl = module.uri;
    urlWithoutQueryString = currentUrl.split(/[?#]/)[0];
    urlWithoutFilename = urlWithoutQueryString.substr(0, urlWithoutQueryString.lastIndexOf('/'))

    function toggleFullscreen() {
        $('#video-render-area').toggleClass('fullscreen');
        $('#fullscreen-button').toggleClass('fullscreen');
        $('#video-container').toggleClass('fullscreen');
    }

    function getEmbedUrlForVideoPlayerType(videoUrl, videoPlayerType){
        if (videoPlayerType === "YouTube"){
            return '//www.youtube.com/embed/' + getVideoIdFromYoutubeUrl(videoUrl) +'?modestbranding=1&rel=0';
        }
    }

    function getVideoIdFromYoutubeUrl(youtubeUrl){
        let matches = youtubeUrl.match(/^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/)
        if (matches && matches[2].length == 11){
            return matches[2];
        }
        else {
            throw "Could not read YouTube video id from provided URL"
        }
    }

    return {
        setupVideo: function (videoUrl, videoPlayerType) {

            let embedUrlForVideoPlayerType = getEmbedUrlForVideoPlayerType(videoUrl, videoPlayerType)

            let videoRenderArea = $('#video-render-area');
            videoRenderArea.attr('src', embedUrlForVideoPlayerType);

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