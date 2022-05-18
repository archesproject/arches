
define('three-wrapped', ['three-official'], function (THREE) {
    window.THREE = THREE;
    return THREE;
});

define('proj4-wrapped', ['proj4'], function (proj4) {
    window.proj4 = proj4;
    return proj4;
});

define('ol-wrapped', ['ol'], function (ol) {
    window.ol = ol;
    return ol;
});

define([
    'module',
    'arches',
    'jquery',
    'jquery-ui',
    'proj4-wrapped',
    'spectrum',
    'perfect-scrollbar',
    'three-wrapped',
    'binary-heap',
    'tween',
    'd3',
    'ol-wrapped',
    'i18next',
    'jstree',
    'potree-official',
    'laslaz',
    'utils/get-query-string-parameter'
], function (module, arches, $, jqueryUi, proj4, spectrum, perfectScrollbar, three, binaryHeap, tween, d3, ol, i18next, jstree, Potree, laslaz, getQueryStringParameter) {

    let currentUrl = module.uri;
    urlWithoutQueryString = currentUrl.split(/[?#]/)[0];
    urlWithoutFilename = urlWithoutQueryString.substr(0, urlWithoutQueryString.lastIndexOf('/'));
    
    if (!isValidUrl(urlWithoutFilename)){
        if (urlWithoutFilename.startsWith('//')){
            urlWithoutFilename = location.protocol + urlWithoutFilename;
        }
        else {
            urlWithoutFilename = location.origin + urlWithoutFilename;
        }
    }

    potreePath = urlWithoutFilename + '/libs/potree'
    Potree.scriptPath = new URL(potreePath);
    Potree.resourcePath = Potree.scriptPath + '/resources';

    var fullscreenImageOff = arches.urls.media + 'img/fullscreen_off_white.svg';
    var fullscreenImageOn = arches.urls.media + 'img/fullscreen_on_white.svg';

    function toggleFullscreen() {
        $('#potree_render_area').toggleClass('fullscreen');
        $('#potree_sidebar_container').toggleClass('fullscreen');
        
        let button = $('#fullscreen-button');
        if (button.attr('src').indexOf('fullscreen_off_white.svg') != -1) {
            button.attr('src', fullscreenImageOn);
        }
        else {
            button.attr('src', fullscreenImageOff);
        }
    }

    return {
        setupPotree: function (sourcePath, pointcloudName) {

            viewer.setFOV(60);
            viewer.setPointBudget(10000000);
            viewer.useHQ = true;

            viewer.setEDLEnabled(false);
            viewer.setBackground('gradient'); // ["skybox", "gradient", "black", "white"];
            viewer.setDescription('');
            viewer.loadSettingsFromURL();

            let fullScreenToggle = document.createElement('img');
            fullScreenToggle.src = fullscreenImageOff;
            fullScreenToggle.id = 'fullscreen-button';
            fullScreenToggle.onclick = toggleFullscreen;
            fullScreenToggle.classList.add('potree_button');

            $('#message_listing').append(fullScreenToggle);

            viewer.loadGUI(() => {
                viewer.setLanguage('en');
                $('#menu_appearance').next().show();
                $('#menu_tools').next().show();
                $('#menu_scene').next().show();
            });

            Potree.loadPointCloud(sourcePath, pointcloudName, e => {
                let pointcloud = e.pointcloud;
                let material = pointcloud.material;
                viewer.scene.addPointCloud(pointcloud);
                material.pointColorType = Potree.PointColorType.RGB; // any Potree.PointColorType.XXXX 
                material.size = 0.1;
                material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
                material.shape = Potree.PointShape.SQUARE;
                viewer.fitToScreen();
                
                // Run in fullscreen if requested through query string
                let fullscreenBool = getQueryStringParameter('fullscreen');
                if (fullscreenBool){
                    if (fullscreenBool.toLowerCase() === "true"){
                        toggleFullscreen();
                    }
                }
            });
        }
    }

});

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    }
    catch (err) {
        return false;
    }
}
