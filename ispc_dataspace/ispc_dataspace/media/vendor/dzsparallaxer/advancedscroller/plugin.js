// ==ClosureCompiler==
// @output_file_name default.js
// @compilation_level SIMPLE_OPTIMIZATIONS
// ==/ClosureCompiler==

/*
 * Author: Digital Zoom Studio
 * Website: http://digitalzoomstudio.net/
 * Portfolio: http://codecanyon.net/user/ZoomIt/portfolio?ref=ZoomIt
 * This is not free software.
 * Advanced Scroller v1.44
 */


(function($) {
    var target_swiper;
    $.fn.advancedscroller = function(o) {
        var defaults = {
            settings_slideshowTime: '5' //in seconds
            , settings_autoHeight: 'on'
            , settings_autoHeight_proportional: 'off' // -- set proportional height of the image depending on the width
            , settings_autoHeight_proportional_max_height: 500 // -- the height on which shall not be passed
            , design_itemwidth: '200'
            , design_itemheight: '200'
            , design_arrowsize: 'default' // -- set the left and right arrow size, this is the size of an arrow
            , design_bulletspos: 'default' // --- set the bullets position top, bottom or default ( set by the skin ) or none
            , design_disableArrows: 'default'
            , design_forceitemwidth: ''
            ,settings_transition: 'slide' // slide or fade
            ,settings_direction: 'horizontal'
            ,settings_responsive: 'on'
            ,settings_mode: 'normal'//normal or onlyoneitem
            ,settings_swipe: "on"
            ,settings_swipeOnDesktopsToo: "off"
            ,settings_makeFunctional: true
            ,settings_centeritems: false
            ,settings_slideshow: 'off'
            ,settings_lazyLoading: 'off'
            ,settings_force_immediate_load: 'off' // -- force immediate load even if there are items to be loaded
            ,settings_slideshowDontChangeOnHover: 'on'
            ,settings_transition_only_when_loaded: 'off' // -- transition only when the image has fully loaded
            ,settings_wait_for_do_transition_call: 'off' // -- [advanced] set this when the transition is actually called from an outer function / api
            ,settings_secondCon: null
            ,mode_onlyone_autoplay_videos: 'on' // -- autoplay videos when scrolled to the video
        }

        if(typeof o =='undefined'){
            if(typeof $(this).attr('data-options')!='undefined'){
                var aux = $(this).attr('data-options');
                aux = 'var aux_opts = ' + aux;
                eval(aux);
                o = aux_opts;
            }
        }
        o = $.extend(defaults, o);

        //console.info(o);
        this.each(function() {
            var cthis = $(this)
                ;
            var nrItems = 0;
            var currNr = -1;
            var busy = true;
            var i = 0
                ,startIndex = 0
                ;
            var ww
                , wh
                , tw // total width of the container and h
                , th
                , cw // clip w and h
                , ch
                , realcw // clip w and h
                , realch
                ;
            var
                items_per_page = 0
                ;
            var
                _items
                ,_thumbsCon
                ,_thumbsClip
                ,_bulletsCon
                ,_arrowsCon
                ;
            var
                pag_total_thumbsizes = 0
                ,pag_total_thumbnr = 0 // = total number of thumbnails
                ,pag_total_pagenr = 0 // = total number of pages
                ,pag_excess_thumbnr = 0 // = the excess thumbs which go

                ;
            var currPage = -1
                ,currPageX = 0
                ,tempPage = 0
                ;
            //===slideshow vars
            var slideshowInter
                ,slideshowCount = 0
                ,slideshowTime
                ,inter_wait_loaded = null
                ;


            var sw_ctw = 0
                ,sw_tw = 0
                ;

            var loadedArray = []
                ,lazyLoadingArray = []
                ,itemsToBeArray = []
                ;


            var action_call_on_gotoItem = null;

            var inter_calculate_hard = 0;
            var is_over = false;
            var busy = false;
            var aux;
            var misc_has_height_same_as_width_elements = false;

            if(String(o.design_itemwidth)!='auto' && String(o.design_itemwidth).indexOf("%")==-1){
                o.design_itemwidth = parseInt(o.design_itemwidth, 10);
            }

            o.design_itemheight = parseInt(o.design_itemheight, 10);

            if(isNaN(Number(o.design_arrowsize))==false){
                o.design_arrowsize = Number(o.design_arrowsize);
            }

            o.settings_slideshowTime = parseInt(o.settings_slideshowTime, 10);
            o.design_forceitemwidth = parseInt(o.design_forceitemwidth, 10);
            slideshowTime = o.settings_slideshowTime;
            //console.info(cthis, o.design_forceitemwidth>0);
            init();



            if(document.addEventListener){
                document.addEventListener("fullscreenchange", handle_fs, false);
                document.addEventListener("webkitfullscreenchange", handle_fs, false);
                document.addEventListener("mozfullscreenchange", handle_fs, false);
            }



            function handle_fs(e){
                var fs = window.fullScreenApi.isFullScreen();
                if (fs) {
                }
                else {
                    setTimeout(function(){
                        handleResize();
                    },100);
                }
            }

            function init(){
                if(cthis.hasClass('inited')){
                    return;
                }

                //console.info('init()');

                th = cthis.outerHeight(false);

                if(cthis.attr('class').indexOf("skin-")==-1){
                    cthis.addClass(o.settings_skin);
                }
                if(cthis.hasClass('skin-default')){
                    o.settings_skin = 'skin-default';
                }
                if(cthis.hasClass('skin-inset')){
                    o.settings_skin = 'skin-inset';
                }
                if(cthis.hasClass('skin-agata-inset')){
                    o.settings_skin = 'skin-inset';
                    o.design_arrowsize = 0;
                }
                if(cthis.hasClass('skin-black')){
                    o.settings_skin = 'skin-black';
                    skin_tableWidth = 192;
                    skin_normalHeight = 158;
                }
                if(cthis.hasClass('skin-regen')){
                    o.settings_skin = 'skin-black';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }
                if(cthis.hasClass('skin-avanti-inset')){
                    o.settings_skin = 'skin-avanti-inset';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }
                if(cthis.hasClass('skin-whitefish')){
                    o.settings_skin = 'skin-whitefish';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                }
                if(cthis.hasClass('skin-bubble-inset')){
                    o.settings_skin = 'skin-bubble-inset';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }
                if(cthis.hasClass('skin-nonav')){
                    o.settings_skin = 'skin-nonav';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }

                if(cthis.hasClass('skin-giza')){
                    o.settings_skin = 'skin-giza';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }

                if(cthis.hasClass('skin-qcre')){
                    o.settings_skin = 'skin-qcre';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'none';
                    }
                }


                if(cthis.hasClass('skin-giza-bullets')){
                    o.settings_skin = 'skin-giza-bullets';
                    if(o.design_arrowsize=='default'){
                        o.design_arrowsize = 0;
                    }
                    if(o.design_bulletspos=='default'){
                        o.design_bulletspos = 'bottom';
                    }

                    if(o.design_disableArrows=='default'){
                        o.design_disableArrows='on';
                    }
                }

                if( !(is_ie() && version_ie<9) && (o.settings_swipeOnDesktopsToo=='on' || (o.settings_swipeOnDesktopsToo=='off'&& (is_ios() || is_android() ) && o.settings_swipe=='on' )) ){


                    o.settings_transition = 'slide';
                }


                cthis.addClass('mode-' + o.settings_mode);
                cthis.addClass('transition-' + o.settings_transition);

                if(o.design_arrowsize=='default'){
                    o.design_arrowsize = 40;
                }
                if(o.design_bulletspos=='default'){
                    o.design_bulletspos = 'bottom';
                }

                if(o.design_disableArrows=='default'){
                    o.design_disableArrows='off';
                }



                if(o.design_bulletspos=='top'){
                    cthis.append('<div class="bulletsCon"></div>');
                }
                cthis.append('<div class="thumbsCon" style="opacity: 0;"><ul class="thumbsClip"></ul></div>');
                if(o.design_bulletspos=='bottom'){
                    cthis.append('<div class="bulletsCon"></div>');
                }
                if(o.design_disableArrows!='on'){
                    cthis.append('<div class="arrowsCon"></div>');
                }

                _items = cthis.children('.items').eq(0);
                _bulletsCon = cthis.children('.bulletsCon').eq(0);
                _thumbsCon = cthis.children('.thumbsCon').eq(0);
                _thumbsClip = cthis.find('.thumbsClip').eq(0);
                _arrowsCon = cthis.find('.arrowsCon').eq(0);

                nrItems = _items.children().length;

                if(cthis.find('.js-height-same-as-width')){
                    misc_has_height_same_as_width_elements = true;
                }



                var ind = 0;
                itemsToBeArray = _items.children('.item-tobe');

                //console.info(_thumbsClip);
                _items.children('.item-tobe').each(function(){
                    var _t = $(this);
                    var ind2 = _t.parent().children().index(_t);


                    //console.log(_t, _t.parent().children(), ind);
                    aux = o.design_itemwidth;
                    //console.info(aux);
                    _t.addClass('item').removeClass('item-tobe');
                    if(aux!='auto' && aux!='' && cthis.hasClass('mode-onlyoneitem')==false){

                        _t.css({
                            'width' : aux
                        });
                    }
                    _thumbsClip.append(_t);

                    if(o.settings_lazyLoading=='on'){
                        if(_t.find('.imagediv').length==0 && _t.find('img').length==0){
                            lazyLoadingArray[ind] = 'tobeloaded';
                        }else{
                            lazyLoadingArray[ind] = 'loaded';
                        }
                    }

                    loadedArray[ind]=1;
                    ind++;


                });

                _arrowsCon.append('<div class="arrow-left"></div>');
                _arrowsCon.append('<div class="arrow-right"></div>');
                //console.log(cthis.find('.needs-loading'));

                if(o.settings_skin=='skin-avanti-inset'){
                    _arrowsCon.find('.arrow-left').eq(0).append('<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="17.153px" height="29.969px" viewBox="0 0 17.153 29.969" enable-background="new 0 0 17.153 29.969" xml:space="preserve"> <g> <g> <path fill="#CBCAC1" d="M14.566,0.316C9.947,4.933,5.329,9.55,0.709,14.167c-0.457,0.456,0.25,1.164,0.707,0.707 c4.619-4.617,9.238-9.233,13.857-13.85C15.729,0.567,15.022-0.14,14.566,0.316L14.566,0.316z"/> </g> </g> <g> <g> <path fill="#CBCAC1" d="M0.709,14.874c4.903,4.901,9.806,9.802,14.709,14.703c0.456,0.456,1.163-0.251,0.707-0.707 c-4.903-4.901-9.806-9.802-14.709-14.703C0.96,13.71,0.253,14.417,0.709,14.874L0.709,14.874z"/> </g> </g> </svg> ');
                    _arrowsCon.find('.arrow-right').eq(0).append('<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="17.153px" height="29.969px" viewBox="0 0 17.153 29.969" enable-background="new 0 0 17.153 29.969" xml:space="preserve"> <g> <g> <path fill="#CBCAC1" d="M1.538,1.061c4.661,4.617,9.323,9.233,13.983,13.85c0.459,0.454,1.166-0.252,0.707-0.707 c-4.66-4.617-9.322-9.233-13.983-13.85C1.787-0.1,1.08,0.607,1.538,1.061L1.538,1.061z"/> </g> </g> <g> <g> <path fill="#CBCAC1" d="M15.521,14.204c-4.947,4.9-9.896,9.801-14.844,14.703c-0.458,0.453,0.249,1.16,0.707,0.707 c4.948-4.9,9.896-9.803,14.844-14.704C16.688,14.458,15.98,13.75,15.521,14.204L15.521,14.204z"/> </g> </g> </svg>  ');
                }
                if(o.settings_skin=='skin-bubble-inset'){
                    _arrowsCon.find('.arrow-left').eq(0).append('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="43.625px" height="43.625px" viewBox="-13.236 -6.791 43.625 43.625" enable-background="new -13.236 -6.791 43.625 43.625" xml:space="preserve"> <g id="Layer_2"> <circle fill="#DB4343" cx="8.576" cy="15.021" r="21.812"/> </g> <g id="Layer_1"> <g> <g> <path fill="#CBCAC1" d="M11.428,5.492C8.42,8.5,5.412,11.507,2.403,14.514c-0.297,0.297,0.163,0.758,0.461,0.46 c3.009-3.007,6.017-6.014,9.025-9.021C12.186,5.656,11.725,5.195,11.428,5.492L11.428,5.492z"/> </g> </g> <g> <g> <path fill="#CBCAC1" d="M2.403,14.975c3.193,3.193,6.387,6.385,9.581,9.577c0.297,0.297,0.758-0.163,0.461-0.46 c-3.194-3.193-6.388-6.385-9.581-9.578C2.566,14.217,2.106,14.677,2.403,14.975L2.403,14.975z"/> </g> </g> </g> </svg> ');
                    _arrowsCon.find('.arrow-right').eq(0).append('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="43.625px" height="43.625px" viewBox="-13.236 -6.791 43.625 43.625" enable-background="new -13.236 -6.791 43.625 43.625" xml:space="preserve"> <g id="Layer_2"> <circle fill="#DB4343" cx="8.576" cy="15.021" r="21.812"/> </g> <g id="Layer_1"> <g> <g> <path fill="#CBCAC1" d="M5.54,25.236c3.032-3.031,6.063-6.062,9.097-9.094c0.3-0.3-0.164-0.764-0.464-0.464 c-3.033,3.03-6.064,6.062-9.097,9.093C4.777,25.072,5.241,25.535,5.54,25.236L5.54,25.236z"/> </g> </g> <g> <g> <path fill="#CBCAC1" d="M14.637,15.679c-3.218-3.219-6.438-6.436-9.656-9.653c-0.3-0.299-0.764,0.165-0.465,0.464 c3.22,3.219,6.438,6.435,9.657,9.653C14.473,16.443,14.937,15.979,14.637,15.679L14.637,15.679z"/> </g> </g> </g> </svg> ');
                }
                if(o.settings_skin=='skin-giza'){
                    _arrowsCon.find('.arrow-left').eq(0).append('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="30px" height="30px" viewBox="-1255.924 50.484 30 30" enable-background="new -1255.924 50.484 30 30" xml:space="preserve"> <g id="Layer_3"> <circle fill="#FFFFFF" cx="-1240.882" cy="65.443" r="13.958"/> </g> <g id="Layer_2"> <circle fill="#D1B87E" cx="-1240.903" cy="65.758" r="10.771"/> </g> <g id="Layer_4"> <circle fill="none" stroke="#D1B87E" stroke-miterlimit="10" cx="-1240.882" cy="65.443" r="13.958"/> </g> <g id="Layer_5"> <polygon fill="#FFFFFF" points="-1243.669,64.32 -1239.729,60.386 -1238.243,61.853 -1242.255,65.681 -1237.673,70.316 -1238.989,71.633 -1244.986,65.637 "/> </g> </svg>  ');
                    _arrowsCon.find('.arrow-right').eq(0).append('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="30px" height="30px" viewBox="-1255.924 50.484 30 30" enable-background="new -1255.924 50.484 30 30" xml:space="preserve"> <g id="Layer_3"> <circle fill="#FFFFFF" cx="-1240.882" cy="65.443" r="13.958"/> </g> <g id="Layer_2"> <circle fill="#D1B87E" cx="-1240.903" cy="65.758" r="10.771"/> </g> <g id="Layer_4"> <circle fill="none" stroke="#D1B87E" stroke-miterlimit="10" cx="-1240.882" cy="65.443" r="13.958"/> </g> <g id="Layer_5"> <polygon fill="#FFFFFF" points="-1238.109,67.508 -1242.34,71.734 -1243.736,70.359 -1239.439,66.234 -1243.736,61.881 -1242.322,60.467 -1236.695,66.094 "/> </g> </svg> ');
                }

                cthis.addClass('inited');



                //console.info('inited');
                cthis.get(0).api_set_action_call_on_gotoItem = function(arg){
                    //console.info(arg);
                    action_call_on_gotoItem = arg;
                }




                cthis.find('.imagediv').each(function(){
                    var _t = $(this);
//                    console.info(_t, _t.parent().hasClass('item'));

                    if(_t.parent().hasClass('item')){

                        if(_t[0].style.height=='' || _t[0].style.height=='auto'){
                            if(_t.parent().hasClass('type-inline')==false){

                                //console.info("ADD NEEDS-LOADING",o.settings_lazyLoading, _t.parent().hasClass('loaded'));
                                _t.parent().addClass('needs-loading');
                            }
                        }
                    }
                });

//                console.info(lazyLoadingArray);
                if(o.settings_lazyLoading=='on'){

//                    console.info(_thumbsClip);
                    prepareForLoad(startIndex);
                    if(_thumbsClip.children().eq(startIndex).hasClass('type-inline')==false) {
                        _thumbsClip.children().eq(startIndex).addClass('needs-loading');
                    }
                }else{
                    for(i=0;i<lazyLoadingArray.length;i++){
                        loadItem(lazyLoadingArray[i]);
                    }
                }

                //console.info('advancedscroller - init()');
                if(cthis.find('.item.needs-loading:not(.loaded)').length>0 && o.settings_force_immediate_load=='off'){
                    //console.log('ceva');
                    checkWhenLoaded();
                }else{
                    if(o.settings_force_immediate_load=='on'){

                        checkWhenLoaded();
                    }
                    init_setup();
                }

            }

            function checkWhenLoaded(){

                //console.log(cthis.find('.item.needs-loading'));

                cthis.find('.item.needs-loading:not(.loaded)').each(function(){
                    var _t = $(this);
                    var ind = _t.parent().children().index(_t);


                    if(_t.html()==''){
                        loadedArray[ind]=1;
                        return;
                    }
                    //console.info(_t,_t.find('.imagediv').length, _t.find('img').eq(0));

                    if(_t.find('.imagediv').length>0){
                        toload = _t.find('.imagediv').eq(0).get(0);

                        img = new Image();


                        var aux = _t.find('.imagediv').eq(0).css('background-image');

//                            console.info(o, th);

                        //console.info(o.settings_autoHeight);
                        if(o.settings_autoHeight=='off'){
//                                _t.find('.imagediv').eq(0).css('height', th);
                            _t.find('.imagediv').eq(0).css('height', '100%');
                            _t.css('height', '100%');
                            _thumbsClip.css('height', '100%')
                            _thumbsCon.css('height', '100%')
                        }
//                            console.info(aux);
                        aux = aux.replace('url("', '');
                        aux = aux.replace('")', '');
                        aux = aux.replace('url(', '');
                        aux = aux.replace(')', '');


                        //console.info("FROM IMAGE DIV");

                        img.onload = function(e){
                            // image  has been loaded
                            //console.info('realparent: ',e.target.realparent);


                            var args = {
                                dzsas_index: ind
                                ,target: e.target.realparent
                            }

                            loadedImage(args);
                        };


                        toload.dzsas_index = ind;
                        toload.realimg = img;
                        img.realparent = toload;

                        loadedArray[ind]=0;
                        img.src = aux;


                    }else{
                        toload = _t.find('img').eq(0).get(0);


                    }

//                        console.info(toload.style.height=='')
//                    console.info(toload);

                    if(typeof(toload)=="undefined"){

                        //console.info(_t, _t.find('.vplayer'),_t.find('.vplayer-tobe'))
                        if(_t.find('.vplayer').length>0){
                            toload = _t.find('.vplayer').eq(0);
                        }

                        var args = {
                            dzsas_index: ind
                            ,target: toload
                        }
                        //console.info("FROM SETTIMEOUT NONE FOUND",ind, args);
                        setTimeout(loadedImage, 500, args);
                    }else{
                        loadedArray[ind]=0;


                        var args = {
                            dzsas_index: ind
                            ,target: toload
                        }


                        toload.dzsas_index = ind;


                        //console.info(toload,toload.complete==true,toload.naturalWidth)


                        if(toload.complete==true && toload.naturalWidth != 0){
                            //console.info("FROM SET TIMEOUT LOADED");
                            setTimeout(loadedImage, 500, args);
                        }else{
                            $(toload).bind('load', loadedImage);
                        }
                    }
                });
            }

            function loadedImage(pargs){
                var ind = 0;
                var _t = $(this);
                var _con = null;


                var margs = {
                    dzsas_index : null
                    ,target : null
                }

                if(pargs){
                    margs = $.extend(margs,pargs);

                    if(pargs.currentTarget){
                        margs.target = pargs.currentTarget;

                        if(margs.target && margs.target.dzsas_index){
                            margs.dzsas_index = margs.target.dzsas_index;
                        }
                    }
                }



                //console.info('loadedImage', margs);

                if(margs.dzsas_index){
                    ind = margs.dzsas_index;
                }
                if(margs.target){
                    _t = $(margs.target);
                }

                //console.info(_t,ind);


                if(_t.hasClass('imagediv')){
                    //console.info(_t,ind);

                    if(_t.get(0).style.height=='' || _t.get(0).style.height=='auto'){
                        _t.height(_t.get(0).realimg.naturalHeight);

                    }

                    //console.info(_t,_t.get(0).realimg);

                    _t.data('natural_w',_t.get(0).realimg.naturalWidth);
                    _t.data('natural_h',_t.get(0).realimg.naturalHeight);
                }
                loadedArray[ind]=1;

                //console.info(loadedArray);


                if(_t.parent().hasClass('item')){
                    _con = _t.parent();

                }
                if(_t.parent().parent().hasClass('item')){
                    _con = _t.parent().parent();
                }
                if(_t.parent().parent().parent().hasClass('item')){
                    _con = _t.parent().parent().parent();
                }
                if(_t.parent().parent().parent().parent().hasClass('item')){
                    _con = _t.parent().parent().parent().parent();
                }

                if(_con){

                    var _img = _t.get(0);

                    //console.info(ind, _t);

                    if(_t.get(0).realimg){
                        _img = _t.get(0).realimg;
                    }
                    //console.info(_img,_img.naturalWidth);
                    if(_img.naturalWidth){
                        _con.data('naturalWidth' , _img.naturalWidth);
                    }
                    if(_img.naturalHeight){
                        _con.data('naturalHeight' , _img.naturalHeight);
                    }

                    //console.info(_t);
                    if(!(_img.naturalWidth)){
                        if(_t.hasClass('vplayer')){

                            _con.data('' , 500);
                            if(_t.attr('data-width-for-gallery')){

                                _con.data('naturalWidth' , _t.attr('data-width-for-gallery'));
                            }else{

                                _con.data('naturalWidth' , 800);
                            }

                            if(_t.attr('data-height-for-gallery')){

                                _con.data('naturalHeight' , _t.attr('data-height-for-gallery'));
                            }else{

                                _con.data('naturalHeight' , 800);
                            }
                        }

                        if(_t.parent().parent().hasClass('wipeout-wrapper')){
                            _t.parent().parent().addClass('is-video');
                        }
                    }

                    //console.info(_con,_img);

                    _con.addClass('loaded');
                }


                var sw = false
                for(i=0;i<loadedArray.length;i++){
                    if(loadedArray[i]!=1){
                        sw = true;
                    }
                }
                if(sw==false){
                    var args={
                        from_check_loaded : true
                    };
                    init_setup(args);
                }
            }
            function init_setup(pargs){



                var margs={
                    from_check_loaded : false
                };

                if(pargs){
                    margs = $.extend(margs,pargs);
                }

                if(o.settings_force_immediate_load=='on' && margs.from_check_loaded){
                    console.info("CHECK LOADED");
                    handleResize();
                }


                if(cthis.hasClass('loaded')){
                    return;
                }
                cthis.addClass('loaded');

                //console.info('advancedscroller - init_setup()');



                pag_total_thumbnr = _thumbsClip.children().length;
                _thumbsClip.children().each(function(){
                    var _t = $(this);
                    var ind = _t.parent().children().index(_t);
                    //console.log(_t, _t.parent().children(), ind);
                    if(ind==0){
                        //_t.addClass('first');
                    }
                    if(ind==_thumbsClip.children().length-1){
                        // _t.addClass('last');
                    }


                    if(o.design_forceitemwidth>0){
                        //_t.css('width', o.design_forceitemwidth);
                    }

                    //console.info(_t);

                    if(_t.find('.feed-description').length>0){
                        _t.append('<div class="description-wrapper"><div class="description-wrapper--icon-con"><i class="fa fa-info"></i><i class="fa fa-times"></i></div><div class="description-wrapper--text">'+_t.find('.feed-description').eq(0).html()+'</div></div>')
                    }

                    //console.log(_t.css('margin-left'));

                    //==== no margin for PERCENTAGE allowed
                    var ml = parseInt(_t.css('margin-left'), 10);
                    _t.css('margin-left', ml);
                    pag_total_thumbsizes+=_t.outerWidth(true);
                });
                tw = cthis.outerWidth(false);
                th = o.design_itemheight;
                //console.log(cthis, cthis.width(),  tw, th, cthis, pag_total_thumbsizes);

                _thumbsClip.css({
                    'width' : (pag_total_thumbsizes)
                });


                if(o.settings_mode=='onlyoneitem' && o.settings_transition=='testimonials_transition_1'){

                    _thumbsClip.css({
                        'width' : tw
                    });

                }

                //console.log(cthis);


                $(document).delegate('.bullet', 'click', click_bullet);

                _arrowsCon.children().bind('click', click_arrow);

                cthis.get(0).api_gotoNextPage = gotoNextPage;
                cthis.get(0).api_gotoPrevPage = gotoPrevPage;


                if(o.settings_swipe=='on'){
                    if( !(is_ie() && version_ie<9) && (o.settings_swipeOnDesktopsToo=='on' || (o.settings_swipeOnDesktopsToo=='off'&& (is_ios() || is_android() ))) ){
                        setupSwipe();
                        o.settings_transition = 'slide';
                        if(o.settings_transition=='fade' && o.settings_mode=='onlyoneitem'){
                            cthis.removeClass('transition-fade');
                            cthis.removeClass('transition-'+o.settings_transition);
                        }
                    }
                }



                if(o.settings_secondCon){
                    var xpos = 0;
                    $(o.settings_secondCon).find('.item').each(function(){
                        var _t = $(this);
                        _t.css('left', xpos+'%');
                        xpos+=100;
                    })
                }


                $(window).bind('resize', handleResize);

                cthis.get(0).api_force_resize = handleResize;
                //cthis.get(0).api_force_resize = handleResize;

                calculate_dims({'donotcallgotopage' : 'on'});

                if(o.settings_slideshow=='on'){
                    slideshowInter = setInterval(tick,1000);
                }

                cthis.unbind('mouseenter');
                cthis.bind('mouseenter', handle_mouseenter);
                cthis.unbind('mouseleave');
                cthis.bind('mouseleave', handle_mouseleave);



                setTimeout(init_allloaded, 300);
            }
            function init_allloaded(){

                //====handleLoaded aka

                cthis.addClass('all-loaded');

                cthis.children('.preloader, .preloader-semicircles').fadeOut('slow');
                _thumbsCon.animate({'opacity' : 1}, 500);




                var tempPage = 0;



                //console.info(tempPage);

                gotoPage(tempPage);

                cthis.get(0).api_goto_page = gotoPage;


                handleResize();

            }
            function handle_mouseenter(){
                is_over = true;
                //console.log(cthis);
            }
            function handle_mouseleave(){
                is_over = false;
                //console.log(cthis);
            }

            function calculate_dims(pargs){



                var margs = {
                    donotcallgotopage : 'off'
                };

                if(pargs){
                    margs = $.extend(margs,pargs);
                }

                //console.info('calculate_dims()',margs);

                if(o.settings_makeFunctional==false){
                    var allowed=false;

                    var url = document.URL;
                    var urlStart = url.indexOf("://")+3;
                    var urlEnd = url.indexOf("/", urlStart);
                    var domain = url.substring(urlStart, urlEnd);
                    //console.log(domain);
                    if(domain.indexOf('a')>-1 && domain.indexOf('c')>-1 && domain.indexOf('o')>-1 && domain.indexOf('l')>-1){
                        allowed=true;
                    }
                    if(domain.indexOf('o')>-1 && domain.indexOf('z')>-1 && domain.indexOf('e')>-1 && domain.indexOf('h')>-1 && domain.indexOf('t')>-1){
                        allowed=true;
                    }
                    if(domain.indexOf('e')>-1 && domain.indexOf('v')>-1 && domain.indexOf('n')>-1 && domain.indexOf('a')>-1 && domain.indexOf('t')>-1){
                        allowed=true;
                    }
                    if(allowed==false){
                        return;
                    }

                }

                /*
                 _thumbsClip.children().each(function(){
                 var _t = jQuery(this);

                 if(o.design_forceitemwidth>0){
                 _t.css('width', o.design_forceitemwidth);
                 }
                 console.log(_t.outerWidth(true));
                 pag_total_thumbsizes+=_t.outerWidth(true);
                 });
                 tw = cthis.outerWidth(false);
                 */
                th = cthis.outerHeight(false);

                _thumbsClip.css({
                    'width' : (pag_total_thumbsizes)
                });




                if(o.settings_centeritems==true){
                    _thumbsClip.addClass('center-it');
                    _thumbsClip.css({
                        'transform': 'translate('+(tw/2)+'px,0)'
                    })
                }


                _thumbsCon.find('.vplayer').width(_thumbsCon.width());

                //console.info(_thumbsClip.find('.vplayer'))

                cw = tw - o.design_arrowsize * 2;


                items_per_page = (Math.floor(cw / _thumbsClip.children().eq(0).outerWidth(true)));

                if(cthis.hasClass('debug-target')){
                    //console.info(items_per_page,cw,_thumbsClip.children().eq(0).outerWidth(true));
                }
                if(items_per_page<1){
                    items_per_page=1;
                }

                if(o.settings_mode=='onlyoneitem'){
                    items_per_page = 1;
                }

                //console.log(pag_total_thumbnr, items_per_page);
                realcw = items_per_page * _thumbsClip.children().eq(0).outerWidth(true);
                pag_total_pagenr = Math.ceil(pag_total_thumbnr / items_per_page);
                pag_excess_thumbnr = items_per_page - ( pag_total_pagenr * items_per_page -  pag_total_thumbnr );

                //if only one item, the real canvas width = total width
                if(o.settings_skin=='skin-inset' && o.settings_mode=='onlyoneitem'){
                    realcw = tw;

                }

                aux = tw - (tw - realcw);
                //console.log(cthis, tw, realcw, o.settings_skin, o.settings_mode)

                if(o.settings_mode=='onlyoneitem'){
                    aux = '100%';
                }

                if(o.settings_transition!='wipeoutandfade') {
                    _thumbsCon.css({
                        'left': (tw / 2 - realcw / 2)

                    })
                }

                if(_thumbsCon.hasClass('width-already-set')==false){

                    _thumbsCon.css({
                        'width' : aux
                    })
                }


                if(o.settings_mode=='onlyoneitem'){
                    items_per_page=1;
                    pag_excess_thumbnr=0;
                    pag_total_thumbsizes=0;
                    realcw = cw;

                    _thumbsClip.children().each(function(){
                        var _t = $(this);

                        if(o.settings_transition!='wipeoutandfade'){

                            _t.css({
                                'width' : realcw
                            });
                        }else{
                            if(_t.data('forced_width')!='on'){

                                _t.css({
                                    'width' : realcw
                                });
                            }
                        }
                        pag_total_thumbsizes+=_t.outerWidth(true);
                    });
                    _thumbsClip.css({
                        'width' : (pag_total_thumbsizes)
                    });


                    if(o.settings_mode=='onlyoneitem' && o.settings_transition=='testimonials_transition_1'){

                        _thumbsClip.css({
                            'width' : tw
                        });

                    }


                    sw_ctw = (pag_total_thumbsizes);
                    o.design_itemwidth = realcw;
                }
                //console.log(pag_excess_thumbnr);
                if(margs.donotcallgotopage=='on'){

                }else{
                    _bulletsCon.html('');
                    for(i=0;i<pag_total_pagenr;i++){
                        _bulletsCon.append('<span class="bullet"></span>')
                    }
                }

                if(misc_has_height_same_as_width_elements){
                    cthis.find('.js-height-same-as-width').each(function(){
                        var _t = $(this);

                        _t.height(_t.width());
                    })
                }

                //=====setting first-in-row and last-in-row
                for(i=0;i<pag_total_thumbnr;i++){
                    //console.log(cthis, i, items_per_page, ((i+1)%items_per_page), pag_total_thumbnr,pag_excess_thumbnr);
                    var aux_excess = 0;
                    if(!cthis.hasClass('islastpage') || pag_excess_thumbnr==0){
                        aux_excess = 0;

                        if(((i+1)%items_per_page)==0){
                            _thumbsClip.children().eq(i).addClass('last-in-row');
                        }else{
                            _thumbsClip.children().eq(i).removeClass('last-in-row');
                        }
                        if(((i+1)%items_per_page)==1){
                            _thumbsClip.children().eq(i).addClass('first-in-row');
                        }else{
                            _thumbsClip.children().eq(i).removeClass('first-in-row');
                        }
                    }else{
                        aux_excess = pag_excess_thumbnr;
                        //console.info(pag_total_thumbnr - ( pag_excess_thumbnr));
                        _thumbsClip.children().eq(pag_total_thumbnr - 1 - ( pag_excess_thumbnr)).removeClass('last-in-row');
                        _thumbsClip.children().eq(pag_total_thumbnr - 1 - ( pag_excess_thumbnr)).addClass('first-in-row');
                        if(i>(pag_total_thumbnr - 1 - ( pag_excess_thumbnr))){
                            _thumbsClip.children().eq(i).removeClass('first-in-row');
                            _thumbsClip.children().eq(i).removeClass('last-in-row');
                        }
                    }

                    if(i==pag_total_thumbnr-1){
                        _thumbsClip.children().eq(i).removeClass('first-in-row');
                        _thumbsClip.children().eq(i).addClass('last-in-row');

                    }
                };

                //console.log(pag_total_pagenr);
                if(pag_total_pagenr<2){
                    cthis.addClass('no-need-for-nav');
                }else{
                    cthis.removeClass('no-need-for-nav');
                };

                if(o.settings_transition=='fade'){
                    _thumbsClip.children().css({
                        'position':'absolute'
                    })
                }





                var tempPage = 0;




                //_bulletsCon.find('.bullet').bind('click', click_bullet);
                if(currPage==-1 || margs.donotcallgotopage=='on'){

                }else{
                    var args = {
                        'called_from_resize':true
                    }
                    gotoPage(currPage,args);
                }

            }


            function calculate_dims_hard(){



                sw_ctw = _thumbsClip.outerWidth() // --- swiper total width
                sw_tw = _thumbsCon.width() // --- swiper image width ( visible )


            }


            function tick(){
                slideshowCount++;
                //console.log(cthis, slideshowCount, slideshowTime);
                if(o.settings_slideshowDontChangeOnHover=='on'){
                    if(is_over==true){
                        return;
                    }
                }

                if(slideshowCount >= slideshowTime){
                    gotoNextPage();
                    slideshowCount = 0;
                }
            }

            function setupSwipe(){
                cthis.addClass('swipe-enabled');
                //console.log('setupSwipe');//swiping vars
                var down_x = 0
                    ,up_x = 0
                    ,screen_mousex = 0
                    ,dragging = false
                    ,def_x = 0
                    ,targetPositionX = 0
                    ,_swiper = _thumbsClip
                    ;



                var _t = cthis;
//                console.log(_t, sw_tw, sw_ctw);

                _swiper.bind('mousedown', function(e){

                    if(e.which==3){
                        return false;
                    }
                    target_swiper = cthis;
                    down_x = e.screenX;
                    def_x = 0;
                    dragging=true;
                    paused_roll=true;
                    cthis.addClass('closedhand');
                    return false;
                });

                $(document).bind('mousemove', function(e){
                    if(dragging==false){

                    }else{
                        screen_mousex = e.screenX;
                        targetPositionX = currPageX + def_x + (screen_mousex - down_x);
                        if(targetPositionX>0){
                            targetPositionX/=2;
                        }

                        if(targetPositionX<-sw_ctw+sw_tw){
                            //console.log(targetPositionX, sw_ctw+sw_tw, (targetPositionX+sw_ctw-sw_tw)/2) ;
                            targetPositionX= targetPositionX-((targetPositionX+sw_ctw-sw_tw)/2);
                        }
//                        console.log(sw_tw, sw_ctw);
                        _swiper.css('left', targetPositionX);
                    }
                });
                $(document).bind('mouseup', function(e){
                    //console.log(down_x);
                    cthis.removeClass('closedhand');
                    up_x = e.screenX;
                    dragging=false;
                    checkswipe();

                    paused_roll=false;
                    return false;
                    // down_x = e.originalEvent.touches[0].pageX;
                });
                _swiper.bind('click', function(e){
                    //console.log(up_x, down_x);
                    if(Math.abs((down_x-up_x))>50){
                        return false;
                    }
                });


                _swiper.bind('touchstart', function(e){
                    target_swiper = cthis;
                    down_x =  e.originalEvent.touches[0].pageX;
                    //console.log(down_x);
                    //def_x = base.currX;
                    dragging=true;
                    //return false;
                    paused_roll=true;
                    cthis.addClass('closedhand');
                });
                _swiper.bind('touchmove', function(e){
                    //e.preventDefault();
                    if(dragging==false){
                        return;
                    }else{
                        up_x = e.originalEvent.touches[0].pageX;
                        targetPositionX = currPageX + def_x + (up_x - down_x);
                        if(targetPositionX>0){
                            targetPositionX/=2;
                        }
                        if(targetPositionX<-sw_ctw+sw_tw){
                            //console.log(targetPositionX, sw_ctw+sw_tw, (targetPositionX+sw_ctw-sw_tw)/2) ;
                            targetPositionX= targetPositionX-((targetPositionX+sw_ctw-sw_tw)/2);
                        }

                        _swiper.css('left', targetPositionX);
                    }
                    if(up_x>50){
                        return false;
                    }
                });
                _swiper.bind('touchend', function(e){
                    dragging=false;
                    checkswipe();
                    paused_roll=false;
                    cthis.removeClass('closedhand');
                });

                function checkswipe(){
//                    console.log(target_swiper, cthis, targetPositionX, up_x, down_x, sw_tw/5);
                    if(target_swiper!=cthis){
                        return;
                    }
                    var sw=false;
                    if (up_x - down_x < -(sw_tw/5)){
                        //console.log('ceva');
                        slide_right();
                        sw=true;
                    }
                    if (up_x - down_x > (sw_tw/5)){
                        slide_left();
                        sw=true;
                    }

                    if(sw==false){
                        _swiper.css({left : currPageX});
                    }
                    target_swiper = undefined;
                }

                function slide_left(){
                    if(currPage<1){
                        _swiper.css({left : currPageX});
                        return;
                    }
                    gotoPrevPage();
                }
                function slide_right(){

                    if(currPage>pag_total_pagenr-2){
                        _swiper.css({left : currPageX});
                        return;
                    }
                    gotoNextPage();
                }
            }


            function handleResize(e, pargs) {



                var margs = {

                    calculate_auto_height: true
                    ,calculate_auto_height_default_h: 0
                };

                if(pargs){
                    margs = $.extend(margs, pargs);
                }



                ww = $(window).width();
                tw = cthis.width();
                //console.info('handleResize', tw);


                if(margs.calculate_auto_height){
                    //console.info(cthis.get(0).style.height);
                    if(o.settings_autoHeight=='on' || cthis.get(0).style.height=='auto'){


                        var _c = (_thumbsClip.children().eq(currPage));

                        var aux =  _c.outerHeight();

                        //console.info(aux, _c, _c.find('.imagediv').eq(0).data('natural_w'));

                        if(o.settings_autoHeight_proportional=='on'){
                            //console.info(_c.find('.imagediv').eq(0).data('natural_h'));
                            if(_c.find('.imagediv').eq(0).data('natural_w')){

                                var nw =Number(_c.find('.imagediv').eq(0).data('natural_w'));
                                var nh =Number(_c.find('.imagediv').eq(0).data('natural_h'));
                                var rat = nw/nh;

                                aux = tw*nh/nw;

                                //console.info(aux,tw, rat,o.settings_autoHeight_proportional_max_height);
                                if(aux> o.settings_autoHeight_proportional_max_height){
                                    aux = o.settings_autoHeight_proportional_max_height;
                                }


                                aux+='px';

                            }else{
                                if(o.settings_mode=='onlyoneitem' && margs.calculate_auto_height_default_h){

                                    var nw =tw;
                                    var nh =margs.calculate_auto_height_default_h;
                                    var rat = nw/nh;


                                    aux = tw*nh/nw;

                                    //console.info(aux,tw, rat,o.settings_autoHeight_proportional_max_height);
                                    if(aux> o.settings_autoHeight_proportional_max_height){
                                        aux = o.settings_autoHeight_proportional_max_height;
                                    }


                                    aux+='px';
                                }
                            }
                        }

                        if(margs.force_width && margs.force_width>0){
                            _c.find('img').eq(0).width(margs.force_width);
                            _c.find('img').eq(0).addClass('width-already-set');

                            _thumbsCon.width(margs.force_width);
                            _thumbsCon.addClass('width-already-set');
                        }

                        if(margs.force_height && margs.force_height>0){

                            aux = margs.force_height;
                        }

                        //console.info(aux);



                        if(aux){
                            _thumbsCon.css({
                                'height' : aux
                            });
                        }

                        /*

                        */


                    }
                }

                if(currPage>-1){

                    calculate_dims();
                }

                clearTimeout(inter_calculate_hard);
                inter_calculate_hard = setTimeout(calculate_dims_hard, 100);

                //console.log(tw);
            }

            function click_arrow(){
                var _t = $(this);
                // console.log(_t);
                if(_t.hasClass('arrow-left')){
                    gotoPrevPage();
                }
                if(_t.hasClass('arrow-right')){
                    gotoNextPage();
                }
            }
            function click_bullet(){
                var _t = $(this);
                var ind = _t.parent().children().index(_t);
                if(cthis.find(_t).length<1){
                    return;
                }

                gotoPage(ind);
            }

            function prepareForLoad(arg){
                var tempNextNr = arg+1;
                var tempPrevNr = arg-1;

                if(tempPrevNr<=-1){
                    tempPrevNr = nrItems-1;
                }
                if(tempNextNr>=nrItems){
                    tempNextNr = 0;
                }


                //console.info(tempPrevNr);

                loadItem(tempPrevNr);
                loadItem(arg);
                loadItem(tempNextNr);
            }

            function loadItem(arg){


//                console.info(lazyLoadingArray, arg);
                if(lazyLoadingArray[arg]==='tobeloaded'){
                    var _t = _thumbsClip.children().eq(arg);
//                    console.info(_t);
//                    _t.addClass('needs-loading');

                    if(_t.attr('data-source')){
//                        _t.append('<div class="imagediv" style="background-image:url('+_t.attr('data-source')+')"></div>');
                        _t.append('<img class="fullwidth" src="'+_t.attr('data-source')+'"/>');
                    }
                    if(_t.attr('data-divimage_source')){
//                        _t.append('<div class="imagediv" style="background-image:url('+_t.attr('data-source')+')"></div>');
                        _t.append('<div class="imagediv" style="background-image: url('+_t.attr('data-divimage_source')+');" ></div>');
                    }

                    lazyLoadingArray[arg] = 'loading';
                }


                checkWhenLoaded();

            }

            function gotoNextPage() {
                tempPage = currPage+1;
                if(tempPage>pag_total_pagenr-1){
                    tempPage = 0;
                }
                //console.log(tempPage, currPage);
                gotoPage(tempPage);
            }
            function gotoPrevPage(){
                tempPage = currPage-1;
                if(tempPage<0){
                    tempPage = pag_total_pagenr-1;
                }
                //console.log(tempPage);
                //console.log(tempPage, currPage);
                gotoPage(tempPage);
            }
            function gotoPage(arg,pargs){
                //console.log('gotoPage', cthis, currPage, arg, pag_total_pagenr);



                var margs = {

                    'called_from_resize':false

                };

                if(pargs){
                    margs = $.extend(margs,pargs);
                }

                //return false;

                if(arg>pag_total_pagenr-1){
                    arg = pag_total_pagenr-1;
                }



                if(o.settings_mode=='onlyoneitem' && o.settings_lazyLoading=='on'){
                    prepareForLoad(arg);
                }




                if(o.settings_transition_only_when_loaded=='on' && _thumbsClip.children().eq(arg).hasClass('needs-loading') && _thumbsClip.children().eq(arg).hasClass('loaded')==false){

                    //console.info('what');

                    inter_wait_loaded = setTimeout(function(){
                        gotoPage(arg,margs)
                    },500);

                    return false;
                }else{
                    //console.info('what wait');
                    clearTimeout(inter_wait_loaded);
                }

                //console.info('action_call_on_gotoItem', action_call_on_gotoItem);

                _bulletsCon.children().removeClass('active');
                _bulletsCon.children().eq(arg).addClass('active');
                if(arg!=pag_total_pagenr-1 || o.settings_mode=='onlyoneitem'){
                    currPageX = -((items_per_page) * arg) * _thumbsClip.children().eq(0).outerWidth(true);
                    cthis.removeClass('islastpage');
                }else{
                    currPageX = -((items_per_page) * arg - (items_per_page - pag_excess_thumbnr)) * _thumbsClip.children().eq(0).outerWidth(true);
                    cthis.addClass('islastpage');
                }
                calculate_dims({'donotcallgotopage' : 'on'});






                //console.log(cthis, o.settings_transition)

                var animation_time = 500;
                if(currPage > -1 && currPage!=arg && o.settings_mode=='onlyoneitem'){

                    var _c = _thumbsClip.children().eq(currPage);

                    if(o.settings_mode=='onlyoneitem'){
                        //console.info(_c);

                        if(_c.find('.vplayer').length>0){
                            var _cach = _c.find('.vplayer').eq(0);


                            //console.info(_cach);
                            if(_cach.get(0) && _cach.get(0).api_pauseMovie){
                                _cach.get(0).api_pauseMovie();
                            }
                        }
                    }

                    if(o.settings_transition=='wipeoutandfade'){



                        //console.info('thumbsCon.width()',_thumbsCon.width());
                        _c.css('width', _thumbsCon.width());
                        //_c.css('overflow', 'hidden');


                        //console.info(_c);

                        if(_c.children().eq(0).hasClass('wipeout-wrapper')==false){
                            //_c.wrapInner('<div class="wipeout-wrapper"><div class="wipeout-wrapper-inner"></div></div>');

                            if(_c.children('img').length>0){
                                _c.children('img').wrap('<div class="wipeout-wrapper"><div class="wipeout-wrapper-inner"></div></div>');
                            }else{

                                if(_c.find('.vplayer').length>0){

                                    _c.find('.vplayer').wrap('<div class="wipeout-wrapper"><div class="wipeout-wrapper-inner"></div></div>');
                                }
                            }




                            //console.info(_c);

                            //if(_c.find('.wipeout-wrapper .description-wrapper').length>0){
                            //    _c.append(_c.find('.description-wrapper'));
                            //}
                            _c.find('.wipeout-wrapper-inner').eq(0).width(_c.width());
                        }else{


                            //_c.children('.wipeout-wrapper').css('width','');
                        }

                        _c.find('.description-wrapper').removeClass('active').animate({
                            'opacity' : 0
                        }, {
                            queue:false
                            ,duration:300
                        })


                        //if(_c.children('img').eq(0).hasClass('width-already-set')==false){
                        //
                        //    _c.children('img,.imagediv').width(_c.width());
                        //    _c.children('.description-wrapper').width(_c.children('.description-wrapper').width());
                        //}



                        //console.info(_c.children().eq(0),_c.children().eq(0).hasClass('is-video'))
                        if(_c.children().eq(0).hasClass('is-video')){
                            //_c.find('.vplayer').eq(0).width(_c.find('.vplayer').eq(0).width);
                            var aux = 'width: ' + _c.find('.vplayer').eq(0).width() + 'px!important';
                            //console.info(aux);
                            _c.find('.vplayer').eq(0).attr('style',aux);
                        }

                        _c.children('.wipeout-wrapper').addClass('wipeout-wrapper-transitioning')
                        _c.children('.wipeout-wrapper').animate({

                            'width':'0'
                        },{
                            queue:false
                            ,duration : animation_time*1
                            ,complete:function(){
                                setTimeout(function(arg){

                                    //$(this).children().unwrap()
                                    $(arg).removeClass('wipeout-wrapper-transitioning');
                                    $(arg).find('.vplayer').eq(0).attr('style','');

                                    //console.info($(arg));
                                    //$(arg).children('.wipeout-wrapper-inner').css('width' ,'');
                                },150, this);
                            }
                        })

                        //_c.animate({
                        //    'width':'0'
                        //},{
                        //    queue:false
                        //    ,duration : animation_time
                        //})
                    }
                }



                if(o.settings_wait_for_do_transition_call!='on'){
                    if(o.settings_transition=='slide' || o.settings_transition=='fade' || o.settings_transition=='testimonials_transition_1'){
                        //console.info('do transition from here');
                        do_transition();
                    }
                    if(o.settings_transition=='wipeoutandfade'){

                        //console.info(currPage);
                        if(currPage==-1){
                            animation_time=-390;
                        }
                        setTimeout(function(){

                            _thumbsClip.children().removeClass("currItem");
                        },animation_time);

                        //console.info('do transition from hier');
                        setTimeout(do_transition,animation_time+200);
                    }
                }else{

                }

                if(margs.called_from_resize==false && action_call_on_gotoItem){
                    cthis.get(0).api_do_transition = do_transition;
                    //console.info('ceva');
                    action_call_on_gotoItem(cthis, _thumbsClip.children().eq(arg),{arg: arg});

                }


                //do_transition();


                function do_transition(pargs){

                    //console.info('do_transition()', cthis);
                    //console.info('do_transition()', arg, pargs);
                    var margs = {

                            'force_width' : 0
                            ,'force_height' : 0
                            ,'arg' : 0
                    }
                    ;

                    if(pargs){
                        margs = $.extend(margs,pargs);
                    }

                    //console.log(margs);

                    if(o.settings_mode=='onlyoneitem'){

                        //------- only one item
                        var _c = _thumbsClip.children().eq(arg);
                        //console.info(arg,_c);
                        _thumbsClip.children().removeClass("currItem");
                        //if(arg!=1){

                        if(o.settings_transition=='fade'||o.settings_transition=='wipeoutandfade'){

                            _c.addClass('currItem');


                            //console.info(_c.children().eq(0),_c.children().eq(0).hasClass('is-video'))
                            if(_c.children().eq(0).hasClass('is-video')){
                                //_c.find('.vplayer').eq(0).width(margs.force_width);
                                //_c.find('.vplayer').eq(0).height(margs.force_height);
                                //_c.data('wipeoutandfade_forced_sizes','on')
                            }
                        }

                        if(o.settings_transition=='testimonials_transition_1'){

                            setTimeout(function () {
                                _thumbsClip.children().eq(arg).addClass('currItem');
                            },500);

                        }


                        if(o.settings_mode=='onlyoneitem'){

                            if(_c.find('.vplayer').length>0){
                                var _cach = _c.find('.vplayer').eq(0);


                                if(o.mode_onlyone_autoplay_videos=='on'){

                                    if(_cach.get(0) && _cach.get(0).api_playMovie){
                                        _cach.get(0).api_playMovie();
                                    }
                                }


                                if(_cach.get(0) && _cach.get(0).api_handleResize){
                                    setTimeout(function(){

                                        _cach.get(0).api_handleResize();
                                    },1000)
                                }

                            }
                        }


                        _c.find('.description-wrapper').css({
                            'opacity' : 1
                        })



                        if(o.settings_transition=='wipeoutandfade'){


                            //console.info(cthis, o.settings_transition);
                            if(!cthis.hasClass('no-need-for-nav')){

                                var auxw = _thumbsClip.children().eq(0).outerWidth(true);
                                if(margs.force_width && margs.force_width>0){

                                    auxw = (margs.force_width);

                                    //console.info('auxw',auxw,pag_total_pagenr);
                                    _thumbsClip.width(auxw* pag_total_pagenr + 40);
                                    _thumbsClip.children().width(auxw);

                                    // -- i don't know if good idea.
                                    //_thumbsCon.width(auxw);


                                    _thumbsClip.children().data('forced_width','on');
                                }else{


                                    _thumbsClip.children().width(_thumbsCon.eq(0).width());
                                    _thumbsClip.children().data('forced_width','off');
                                }

                                //console.info(margs.arg,auxw);

                                currPageX = 0;

                                currPageX = -margs.arg * auxw;


                                //console.info(currPageX);
                                _thumbsClip.css({
                                    'left' : currPageX
                                });
                            };


                            //console.info(_c, _c.children().eq(0).hasClass('wipeout-wrapper'));
                            if(_c.children('.wipeout-wrapper').length>0){
                                _c.children('.wipeout-wrapper').css('width','');


                            }
                        }
                        if(o.settings_transition=='testimonials_transition_1'){


                            //console.info(cthis, o.settings_transition);
                            if(!cthis.hasClass('no-need-for-nav')){

                                var auxw = _thumbsClip.children().eq(0).outerWidth(true);


                                if(margs.force_width && margs.force_width>0){

                                    auxw = (margs.force_width);

                                    //console.info('auxw',auxw,pag_total_pagenr);
                                    _thumbsClip.width(auxw* pag_total_pagenr + 40);
                                    _thumbsClip.children().width(auxw);


                                    _thumbsClip.children().data('forced_width','on');
                                }else{


                                    _thumbsClip.children().width(_thumbsCon.eq(0).width());
                                    _thumbsClip.children().data('forced_width','off');
                                }

                                //console.info(margs.arg,auxw);

                                currPageX = 0;

                                currPageX = -margs.arg * auxw;


                                //console.info(currPageX);
                                _thumbsClip.css({
                                    'left' : 0
                                });
                            };


                            if(_c.children().eq(0).hasClass('wipeout-wrapper')){
                                _c.children('.wipeout-wrapper').css('width','');


                            }
                        }

                        //}

                        //console.info(o.settings_autoHeight, arg,_c,  _c.outerHeight());
                        if(o.settings_autoHeight=='on'){

                            var aux =  _c.outerHeight();



                            if(o.settings_autoHeight_proportional=='on'){
                                if(_c.find('.imagediv').eq(0).data('natural_w')){

                                    var nw =Number(_c.find('.imagediv').eq(0).data('natural_w'));
                                    var nh =Number(_c.find('.imagediv').eq(0).data('natural_h'));
                                    var rat = nw/nh;

                                    aux = tw*nh/nw;

                                    if(aux> o.settings_autoHeight_proportional_max_height){
                                        aux = o.settings_autoHeight_proportional_max_height;
                                    }


                                    aux+='px';

                                    //console.info(aux,tw, rat);
                                }
                            }


                            if(margs.force_width && margs.force_width>0){
                                _c.find('img').eq(0).width(margs.force_width);
                                _c.find('img').eq(0).addClass('width-already-set');

                                _thumbsCon.width(margs.force_width);
                                _thumbsCon.addClass('width-already-set');
                            }

                            if(margs.force_height && margs.force_height>0){

                                aux = margs.force_height;
                            }

                            _thumbsCon.css({
                                'height' : aux
                            });
                            cthis.css({
                                'height' : 'auto'
                            })


                            if(o.settings_autoHeight_proportional=='on'){
                                _thumbsClip.children().children('.imagediv').height(aux);
                            }
                        }


                        if(o.settings_transition=='slide'){

                            if(!cthis.hasClass('no-need-for-nav')){
                                _thumbsClip.css({
                                    'left' : currPageX
                                });
                            };
                        }


                        if(o.settings_transition=='fade'){

                        }


                    }else{
                        if(!cthis.hasClass('no-need-for-nav')){
                            _thumbsClip.css({
                                'left' : currPageX
                            });
                        };

                    }


                    if(o.settings_secondCon){
//                    console.info($(o.settings_secondCon).find('.item').eq(arg).outerHeight(false));
                        $(o.settings_secondCon).find('.item').removeClass('active');
                        $(o.settings_secondCon).find('.item').eq(arg).addClass('active');
                        $(o.settings_secondCon).find('.dzsas-second-con--clip').css(
                            {
                                'height': $(o.settings_secondCon).find('.item').eq(arg).outerHeight(false)
                                ,'left' : -(arg*100)+'%'
                            }
                        );
                    }

                    currPage = arg;
                    slideshowCount = 0;

                    //setTimeout(calculate_dims, 500);
                }




            }
            return this;
        })
    }


    window.dzsas_init = function(selector, settings) {
        if(typeof(settings)!="undefined" && typeof(settings.init_each)!="undefined" && settings.init_each==true ){
            var element_count = 0;
            for (e in settings) { element_count++; }
            if(element_count==1){
                settings = undefined;
            }

            $(selector).each(function(){
                var _t = $(this);
                _t.advancedscroller(settings)
            });
        }else{
            $(selector).advancedscroller(settings);
        }

    };
})(jQuery);


function is_ios() {
    return ((navigator.platform.indexOf("iPhone") != -1) || (navigator.platform.indexOf("iPod") != -1) || (navigator.platform.indexOf("iPad") != -1)
    );
}
function is_android() {
    //return true;
    return (navigator.platform.indexOf("Android") != -1);
}

function is_ie(){
    if (navigator.appVersion.indexOf("MSIE") != -1){
        return true;
    };
    return false;
};
function is_firefox(){
    if (navigator.userAgent.indexOf("Firefox") != -1){
        return true;
    };
    return false;
};
function is_opera(){
    if (navigator.userAgent.indexOf("Opera") != -1){
        return true;
    };
    return false;
};
function is_chrome(){
    return navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
};
function is_safari(){
    return navigator.userAgent.toLowerCase().indexOf('safari') > -1;
};
function version_ie(){
    return parseFloat(navigator.appVersion.split("MSIE")[1]);
};
function version_firefox(){
    if (/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent)){
        var aversion=new Number(RegExp.$1);
        return(aversion);
    };
};
function version_opera(){
    if (/Opera[\/\s](\d+\.\d+)/.test(navigator.userAgent)){
        var aversion=new Number(RegExp.$1);
        return(aversion);
    };
};


jQuery(document).ready(function($){
    dzsas_init('.advancedscroller.auto-init', {init_each: true})
});