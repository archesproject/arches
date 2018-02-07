require([
    'jquery',
    'arches',
    'easing',
    'plugins/layer_slider/jQuery/jquery-transit-modified',
    'plugins/layer_slider/js/layerslider.transitions',
    'plugins/layer_slider/js/layerslider.kreaturamedia.jquery',
    'flexslider'
], function($, arches) {
    $(document).ready(function() {
        $('#photo-flexslider').flexslider({
            animation: "slide",
            controlNav: false,
            animationLoop: false,
            itemWidth: 80,
            itemMargin: 0
        });

        $('#layerslider').layerSlider({
            skinsPath: arches.urls.media + 'plugins/layer_slider/skins/',
            skin: 'fullwidth',
            thumbnailNavigation: false,
            hoverPrevNext: true,
            responsive: true,
            responsiveUnder: 960,
            sublayerContainer: 960
        });
    });
});