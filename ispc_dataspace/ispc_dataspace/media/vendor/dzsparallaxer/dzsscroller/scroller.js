/*
 * Author: Digital Zoom Studio
 * Website: http://digitalzoomstudio.net/
 * Portfolio: http://codecanyon.net/user/ZoomIt/portfolio
 *
 * Version: 5.01
 */

"use strict";

window.dzsscr_self_options = {};

(function(window,document) {

    var prefix = "", _addEventListener, onwheel, support;

    // detect event model
    if ( window.addEventListener ) {
        _addEventListener = "addEventListener";
    } else {
        _addEventListener = "attachEvent";
        prefix = "on";
    }

    // detect available wheel event
    support = "onwheel" in document.createElement("div") ? "wheel" : // Modern browsers support "wheel"
        document.onmousewheel !== undefined ? "mousewheel" : // Webkit and IE support at least "mousewheel"
            "DOMMouseScroll"; // let's assume that remaining browsers are older Firefox

    window.addWheelListener = function( elem, callback, useCapture ) {
        _addWheelListener( elem, support, callback, useCapture );

        // handle MozMousePixelScroll in older Firefox
        if( support == "DOMMouseScroll" ) {
            _addWheelListener( elem, "MozMousePixelScroll", callback, useCapture );
        }
    };

    function _addWheelListener( elem, eventName, callback, useCapture ) {
        elem[ _addEventListener ]( prefix + eventName, support == "wheel" ? callback : function( originalEvent ) {
            !originalEvent && ( originalEvent = window.event );

            // create a normalized event object
            var event = {
                // keep a ref to the original event object
                originalEvent: originalEvent,
                target: originalEvent.target || originalEvent.srcElement,
                type: "wheel",
                deltaMode: originalEvent.type == "MozMousePixelScroll" ? 0 : 1,
                deltaX: 0,
                deltaZ: 0,
                preventDefault: function() {
                    originalEvent.preventDefault ?
                        originalEvent.preventDefault() :
                        originalEvent.returnValue = false;
                }
            };

            // calculate deltaY (and deltaX) according to the event
            if ( support == "mousewheel" ) {
                event.deltaY = - 1/40 * originalEvent.wheelDelta;
                // Webkit also support wheelDeltaX
                originalEvent.wheelDeltaX && ( event.deltaX = - 1/40 * originalEvent.wheelDeltaX );
            } else {
                event.deltaY = originalEvent.detail;
            }

            // it's time to fire the callback
            return callback( event );

        }, useCapture || false );
    }

})(window,document);

(function($) {
    $.fn.scroller = function(o) {

        var defaults = {
            type: 'normal', // -- normal or scrollTop
            totalWidth: undefined,
            totalwidth: undefined,
            settings_multiplier: 3, // -- scroll multiplier
            settings_skin: 'skin_default',
            settings_scrollbar: 'on',
            settings_scrollbyhover: 'off',
            settings_fadeoutonleave: 'off',
            settings_replacewheelxwithy: 'off',
            settings_refresh: 0// -- refresh dimensions  every x secs
            ,settings_autoheight: 'default'
            ,settings_autoheight_from_first_item: 'off',
            settings_forcesameheight: 'off',
            settings_fullwidth: 'off',
            settings_hidedefaultsidebars: 'off',
            settings_dragmethod: 'drag',//drag or normal - dra is more natural feeling
            settings_autoresizescrollbar: 'off',
            settings_slideshow: '0', // -- slideshow until a user interaction is detected
            scrollBg: 'off',
            force_onlyy: 'off',
            objecter: undefined
            , secondCon: null // provide a second container that the scrollbar moves, nifty stuff
            , secondCon_tw: null
            , secondCon_cw: null
            , secondCon_enable_mouse_scroll: "off"
            , settings_scrollTop_height_indicator: null
            , settings_scrollTop_animate_top_instead_of_scroll: "off"
            , settings_comHeight_surplus: 0
            , settings_show_sidebar_on_right_side_mouse: "on" // -- do not hide the scrollbar when mouse is on the right side
            , enable_easing: 'off' // -- enable easing
            , enable_easing_for_second_con: 'off' // -- enable easing
            , easing_duration: '1.8' // -- easing Duration
            , easing_type: 'easeInCirc' // -- easing Duration
            , settings_disableSpecialIosFeatures: 'off'
            , touch_leave_native_scrollbar: 'off'
            , settings_enable_drag_on_desktops_too: 'off' // -- by default drag drop scrolling only works on mobile, enable this to make it work on desktops too
            , settings_makeFunctional: false
            , settings_chrome_multiplier: 0.10 //scrollmultiplier for chrome
            , settings_safari_multiplier: 0.20 //scrollmultiplier for safari
            , settings_opera_multiplier: 0.002 //scrollmultiplier for opera
            , settings_ie_multiplier: 0.08 //scrollmultiplier for ie
            , settings_edge_multiplier: 0.08 //scrollmultiplier for edge
            , settings_firefox_multiplier: -1 //scrollmultiplier for ff
            , replace_window_object: null // -- use a element from the DOM instead of the window element
            , extra_html_scrollbarx: '' // -- use a element from the DOM instead of the window element
        };

        if(typeof o =='undefined'){
            if(typeof $(this).attr('data-options')!='undefined' && $(this).attr('data-options')!=''){
                var aux = $(this).attr('data-options');
                aux = 'window.dzsscr_self_options = ' + aux;
                eval(aux);
                o = $.extend({},window.dzsscr_self_options);
                window.dzsscr_self_options = $.extend({}, {});
            }
        }
        o = $.extend(defaults, o);


        if(typeof o =='undefined'){
            if(typeof $(this).attr('data-options')!='undefined'  && $(this).attr('data-options')!=''){
                var aux = $(this).attr('data-options');
                aux = 'var aux_opts = ' + aux;
                eval(aux);
                o = aux_opts;
            }
        }



        o.settings_refresh = parseInt(o.settings_refresh, 10);
        o.settings_multiplier = parseFloat(o.settings_multiplier);
        o.settings_chrome_multiplier = parseFloat(o.settings_chrome_multiplier);
        o.settings_firefox_multiplier = parseFloat(o.settings_firefox_multiplier);
        o.settings_slideshow = parseFloat(o.settings_slideshow);


        Math.linearTween = function (t, b, c, d) {
            return c*t/d + b;
        };
        Math.easeIn = function(t, b, c, d) {

            return -c *(t/=d)*(t-2) + b;

        };

        Math.easeOutQuad = function (t, b, c, d) {
            //console.info('ceva');
            t /= d;
            return -c * t*(t-2) + b;
        };
        Math.easeInOutSine = function (t, b, c, d) {
            return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
        };


        Math.easeInCirc = function (t, b, c, d) {
            t /= d;
            return -c * (Math.sqrt(1 - t*t) - 1) + b;
        };

        Math.easeInQuart = function (t, b, c, d) {
            t /= d;
            return c*t*t*t*t + b;
        };


        this.each(function() {

            //console.log(this);
            var totalWidth = 0
                ,totalWidth_for_scrollbar = 0 // -- the scrollbar might be aligned by a different height
                ;
            //total width of the container, this is usually taken from the css of the div
            var totalHeight = 0;
            var comWidth = 0;
            // total width of the real element
            var comHeight = 0;


            var last_totalHeight = 0
                ,last_comHeight = 0
                ;

            var ww = 0
            var wh = 0;
            //subdiv of the container ( real content )
            var _outer = null
                ,_scrollbar = null
                ,_inner = null
                ;
            var _inner_autoheight = false;
            var cthis_autoheight = false;
            // subdiv of the container
            var auxdeltax = 0;
            var auxdeltay = 0;
            var viewIndexWidth = 0;
            var scrollIndexY = 0;
            var scrollIndexX = 0;
            var cthis_touch_left_last = 0;
            var cthis_touch_top_last = 0;
            var inner_dragging = false;
            var sc_dragging = false;
            var sc_touch_left_last = 0;
            var sc_touch_top_last = 0;
            var scrollbar_height = 0;
            var scrollbary = undefined;
            var scrollbary_bg = undefined;
            var scrollbarx = undefined;
            var scrollbarx_bg = undefined;
            var cthis = $(this);
            var mousex = 0;
            var mousey = 0;
            var scrollbary_pressed = false;
            var scrollbarx_pressed = false;
            var scrolling_blocked = false;
            var scrollbary_psize = 0;
            var scrollbarx_psize = 0;
            var scrollbarx_dragx = 0;
            var scrollbarx_draglocalx = 0;
            var scrollbary_dragy = 0;
            var scrollbary_draglocaly = 0;

            var _window_object = $(window)
                ,_scrollTop_height_indicator = null
                ,comHeight_surplus = 0

                ;

            var viewIndexX = 0;
            var viewIndexY = 0;

            var lastNonNaNX = 0; // -- we use this to track the last valid integer
            var lastNonNaNX_sc = 0; // -- we use this to track the last valid integer
            var lastNonNaNY = 0; // -- we use this to track the last valid integer

            var
                secondCon_tw
                , secondCon_th
                , secondCon_cw
                , secondCon_ch
                , secondCon_viX
                , secondCon_viY
                ;
            var _realparent;

            var scrollbufferX = false;
            var scrollbufferY = false;

            var dir_hor = true;
            var dir_ver = true;
            var percomWidth = 0;

            var iOuter;

            var duration_smoothing = 60;

            var inter_reset
                ,inter_hidescrollbar
                ;


            var action_handle_frame = null
                ,action_handle_wheel_end = null
                ,action_animate_scrollbar_end = null
                ;

            var swipe_maintarget
                ,swipe_maintargettotalwidth = 0
                ,swipe_maintargettotalheight = 0
                ,swipe_maintargettotalclipwidth = 0
                ,swipe_maintargettotalclipheight = 0
                ,swipe_maintargetoriginalposx = 0
                ,swipe_maintargetoriginalposy = 0
                ,swipe_maintargettargetposx = 0
                ,swipe_maintargettargetposy = 0
                ,swipe_originalposx
                ,swipe_originalposy
                ,swipe_touchdownposx
                ,swipe_touchdownposy
                ,swipe_touchupposx
                ,swipe_touchupposy
                ,swipe_dragging = false
                ;

            var debug_var = true;

            var slideshow_reachedend = false;
            var slideshow_operation = "plus";

            var stop_enter_frame = false
                ,suspend_enter_frame = false
                ,inter_suspend_enter_frame
                ;


            // --- easing params

            var duration_viy = 1.8
                ,duration_vix = 20
                ;

            var target_viy = 0
                ,target_vix = 0
                ,target_vix_sc = 0
                ,target_bo = 0
                ;

            var begin_viy = 0
                ,begin_vix = 0
                ,begin_vix_sc = 0
                ,begin_bo = 0
                ;

            var finish_viy = 0
                ,finish_vix = 0
                ,finish_vix_sc = 0
                ,finish_bo = 0
                ;

            var change_viy = 0
                ,change_vix = 0
                ,change_vix_sc = 0
                ,change_bo = 0
                ;


            var backup_duration_viy = 0;
            var mode_scrollTop_sw_middlemousescrolling = false;


            var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
            var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);




            if(cthis.hasClass('dzsscr-inited')){
                return false;
            }


            init();
            //return;

            function init() {


                //console.log(totalWidth, cthis, cthis.width()); return;
                if(o.totalWidth==undefined){
                    totalWidth = cthis.width();
                }else{
                    totalWidth = o.totalWidth;
                }
                if(o.totalHeight==undefined){
                    totalHeight = cthis.height();
                }else{
                    totalHeight = o.totalHeight;
                }

                totalWidth_for_scrollbar = totalWidth;

                if(o.settings_skin=='skin_luna'){
                    totalWidth_for_scrollbar-=4;
                }


                if(o.replace_window_object){
                    _window_object = o.replace_window_object;
                }


                if(o.settings_scrollTop_height_indicator && o.settings_scrollTop_height_indicator.outerHeight){
                    _scrollTop_height_indicator = o.settings_scrollTop_height_indicator;
                }

                if(o.settings_comHeight_surplus && o.settings_comHeight_surplus>0){
                    comHeight_surplus = o.settings_comHeight_surplus;
                }

                duration_viy = parseFloat(o.easing_duration);



                if(o.type=='normal') {
                    _inner = cthis.find('.inner').eq(0);
                }

                var cclass=String(cthis.attr('class'));


                if(cclass.indexOf("skin_")==-1){
                    cthis.addClass(o.settings_skin);
                }
                cclass=String(cthis.attr('class'));

                var regex_skin = new RegExp('(skin_.*?)\\b');
                var regex_skin_arr = regex_skin.exec(cclass);

                //console.info(cclass,regex_skin_arr);

                if(regex_skin_arr && regex_skin_arr[1]){
                    o.settings_skin = regex_skin_arr[1];

                }

                //console.info(o.settings_skin);

                if(o.type=='normal'){
                    if(_inner.parent().hasClass('scroller')==false){

                        _inner.wrap('<div class="scroller"></div>')
                    }
                    _outer = cthis.find('.scroller').eq(0);
                }


                if(o.settings_skin=='skin_luna'){

                }



                //console.info(cthis, _outer, is_ios(), is_android(), is_touch_device(), o.settings_disableSpecialIosFeatures);
                if ( (is_touch_device()) && o.settings_disableSpecialIosFeatures != 'on') {
//                    console.info('hmm');

                    //-- we dont need easing scrolling on mobiles as the scrolling is already eased
                    if(o.type=='scrollTop'){
                        return false;
                    }
                    if(_outer){
                        _outer.css('overflow', 'auto');
                    }

                    if(o.touch_leave_native_scrollbar=='on'){
                        return false;
                    }

                    //_outer.css('--webkit', 'auto');
                    if(o.secondCon){
                        //o.secondCon.parent() is the clip
                        o.secondCon.parent().css('overflow', 'auto');
                    }
                    cthis.addClass('is-touch');
                    //return
                } else {
                }

                if(o.type=='scrollTop'){
                    //console.info(cthis, cthis.scrollTop);
                    cthis.addClass('scroller-con type-scrollTop');
                    $('html').css('overflow-y', 'hidden');

                    setTimeout(function(){
                        //cthis.scrollTop(300);
                        //$(window).scrollTop(300);
                    },1000)

                    $(document).delegate('a[href^=#]','click', function(){

                        var _t23 = $(this);
                        if($(_t23.attr('href')).length>0){
                            //console.log($(_t23.attr('href')));

                            if($('.scroller-con.type-scrollTop').get(0) && $('.scroller-con.type-scrollTop').get(0).api_scrolly_to){

                                var aux = $(_t23.attr('href')).offset().top-100;
                                $('.scroller-con.type-scrollTop').get(0).api_scrolly_to(aux);
                            }
                        }

                        return false;
                    })

                    cthis.bind('mousedown',function(e){
                        if(e.which==2){
                            if(!mode_scrollTop_sw_middlemousescrolling){
                                mode_scrollTop_sw_middlemousescrolling = true;
                            }else{

                                mode_scrollTop_sw_middlemousescrolling = false;
                            }
                        }else{

                            mode_scrollTop_sw_middlemousescrolling = false;
                        }
                    })
                    cthis.bind('mousemove',function(e){
                        //console.info(e.clientY, cthis.height(),wh);

                        if(mode_scrollTop_sw_middlemousescrolling){
                            viewIndexY = -(e.clientY/wh * (cthis.height()-wh));
                            //console.info('animateScrollbar from handle_frame()');
                            animateScrollbar();
                        }


                    })



                    $('body').bind('keydown', function(e){
                        //console.info(e)

                        if(e.keyCode==38){

                            viewIndexY += 30;

                            animateScrollbar();
                        }

                        if(e.keyCode==40){

                            viewIndexY -= 30;

                            animateScrollbar();
                        }
                    })

                }

                //return false;
                //console.log(cthis, totalHeight);
                _realparent = cthis;


                _realparent.append('<div class="scrollbar"></div>');
                _scrollbar = _realparent.children('.scrollbar').eq(0);


                if(is_touch_device()){
                    _scrollbar.addClass('easing');
                }

                if(_inner && (_inner.get(0).style.height=='' || _inner.get(0).style.height=='auto')){
                    _inner_autoheight = true;
                }

                if(o.settings_autoheight=='auto'){
                    if(cthis.get(0).style.height=='' || cthis.get(0).style.height=='auto'){
                        cthis_autoheight = true;
                    }
                }
                if(o.settings_autoheight=='on'){
                    cthis_autoheight = true;
                }
                if(o.settings_autoheight=='off'){
                    cthis_autoheight = false;
                }


                //console.info(o.settings_autoheight, cthis_autoheight);



                calculateDims();


                if (cthis.css('opacity') == 0) {
                    //cthis.animate({
                    //    'opacity': 1
                    //}, 600)
                    cthis.parent().children('.preloader').fadeOut('slow');
                }



                if (percomWidth == 0) {
                    percomWidth = comWidth + 50;
                }
                if ( (cthis.hasClass('is-touch') ) && o.settings_disableSpecialIosFeatures == 'off') {
                    //console.log(cthis, totalWidth, percomWidth);
                    //console.log(cthis, totalWidth, percomWidth);
                    if(_outer){
                        _outer.css({
                            'overflow': 'auto'
                        })
                    }

                }
                //console.log('ceva', o.objecter);
                if (cthis.get(0) != undefined) {
                    //console.log('ceva', o.objecter.refreshIt);
                    cthis.get(0).reinit = reinit;
                    cthis.get(0).api_destroy = destroy;
                    cthis.get(0).scrollToTop = scrollToTop;
                    cthis.get(0).updateX = updateX;
                    cthis.get(0).fn_scrollx_to = scrollx_to;
                    cthis.get(0).api_scrolly_to = scrolly_to;
                    cthis.get(0).api_toggle_resize = calculateDims;
                    cthis.get(0).api_get_view_index_y = get_view_index_y;
                    cthis.get(0).api_set_action_handle_frame = function(arg){
                        action_handle_frame = arg;
                    };
                    cthis.get(0).api_set_action_animate_scrollbar_end = function(arg){
                        action_animate_scrollbar_end = arg;
                    };
                    cthis.get(0).api_block_scroll = function(arg){
                        scrolling_blocked = true;
                    };
                    cthis.get(0).api_unblock_scroll = function(arg){
                        scrolling_blocked = false;
                    };
                    cthis.get(0).api_set_action_handle_wheel_end = function(arg){
                        action_handle_wheel_end = arg;
                    };
                    cthis.get(0).api_set_window_object = function(arg){

                        _window_object = arg;
                    };
                    cthis.get(0).api_set_scrollTop_height_indicator = function(arg){

                        _scrollTop_height_indicator = arg;




                    };
                    cthis.get(0).api_comHeight_surplus = function(arg){

                        comHeight_surplus = arg;
                    };

                    /*
                     */
                }




                if (o.settings_refresh > 0) {
                    setInterval(reinit, o.settings_refresh);
                }


                if (cthis.find('.scrollbar').css('opacity') == '0') {
                    cthis.find('.scrollbar').animate({
                        'opacity': 1
                    }, 600);
                }

                $(window).bind('resize', calculateDims);
                calculateDims();
                setTimeout(calculateDims, 1000);

                handle_frame();


                cthis.addClass('dzsscr-inited');
            }

            function suspend_enter_frame_func(){
                //console.info('suspend_enter_frame_func()');
                suspend_enter_frame = true;
            }

            function get_view_index_y(){
                return viewIndexY;
            }

            function destroy(){

                //console.info(_inner);
                //if(o.type=='normal'){
                //    _inner.unwrap()
                //}


                stop_enter_frame = true;

                // -- continue DESTROY FUNCTION
            }

            function handle_frame(){



                if(suspend_enter_frame==false){
                    //console.info(suspend_enter_frame);
                    if(o.settings_slideshow>0){

                        viewIndexX=null;
                        if(slideshow_reachedend){
                            slideshow_reachedend=false;
                            if(slideshow_operation=='plus'){
                                slideshow_operation='minus';
                            }else{
                                slideshow_operation='plus';
                            }
                        }

                        if(slideshow_operation=='plus'){
                            scrollIndexX+= o.settings_slideshow;
                        }else{
                            scrollIndexX-= o.settings_slideshow;
                        }

                        //console.info('animateScrollbar from handle_frame()');
                        animateScrollbar();

                    }


                    if(o.enable_easing=='on'){

                        if(is_android() || is_ios()){

                        }else{

                            if (dir_ver) {
                                //console.info(target_viy);


                                begin_viy = target_viy;
                                change_viy = finish_viy - begin_viy;


                                //target_viy = Number(Math.easeIn(1, begin_viy, change_viy, duration_viy).toFixed(4));
                                //console.info(target_viy);

                                //console.log(o.easing_type);
                                if(o.easing_type=='easeIn'){

                                    target_viy = Number(Math.easeIn(1, begin_viy, change_viy, duration_viy).toFixed(4));
                                }
                                if(o.easing_type=='easeInCirc'){

                                    if(is_safari){
                                        target_viy = Number(Math.easeInCirc(1, begin_viy, change_viy, duration_viy).toFixed(0));
                                    }else{
                                        target_viy = Number(Math.easeInCirc(1, begin_viy, change_viy, duration_viy).toFixed(4));
                                    }

                                }

                                if(isNaN(target_viy)){
                                    target_viy = 0;
                                }


                                //console.info(target_viy);
                                //if(cthis.hasClass('debug-target')){ console.info(target_viy); };

                                if(o.type=='normal'){

                                    _inner.css({
                                        'top': parseInt(target_viy,10)
                                    })
                                }

                                if(o.type=='scrollTop'){


                                    //if(is_safari()){
                                    //    //console.log('safari');
                                    //    //console.log(target_viy,comHeight-totalHeight-100)
                                    //    if(target_viy< -(comHeight-totalHeight-100)){
                                    //        target_viy = -(comHeight-totalHeight-100);
                                    //    }
                                    //    //console.log(target_viy,comHeight-totalHeight-100)
                                    //}


                                    //console.log(-target_viy, totalHeight, comHeight, comHeight-totalHeight-100);
                                    //console.info(_window_object);



                                    if(o.settings_scrollTop_animate_top_instead_of_scroll=='on'){

                                        _window_object.css({
                                            'top': parseInt(target_viy,10)
                                        })

                                    }else{

                                        _window_object.scrollTop(-target_viy);
                                    }
                                    //cthis.scrollTop(-target_viy);
                                }

                            }
                            if (dir_hor) {
                                //console.info(finish_vix);


                                begin_vix = target_vix;
                                change_vix= finish_vix - begin_vix;


                                target_vix = Number(Math.easeIn(1, begin_vix, change_vix, duration_viy).toFixed(4));

                                //console.info(target_vix,duration_viy);
                                if(o.type=='normal'){

                                    _inner.css({
                                        'left': parseInt(target_vix,10)
                                    })
                                }



                                if(o.secondCon) {


                                    //console.info(finish_vix_sc);
                                    begin_vix_sc = target_vix_sc;
                                    change_vix_sc= finish_vix_sc - begin_vix_sc;
                                    target_vix_sc = Number(Math.easeIn(1, begin_vix_sc, change_vix_sc, duration_viy/1.5).toFixed(4));
                                    if(isNaN(target_vix_sc)){
                                        target_vix_sc = 0;
                                    }


                                    //console.info(target_vix_sc);

                                    if (o.enable_easing_for_second_con == 'on') {

                                        o.secondCon.css({
                                            'left': parseInt(target_vix_sc,10)
                                        })
                                    }
                                }

                                if(o.type=='scrollTop'){

                                    $(window).scrollTop(-target_vix);
                                }




                            }
                        }



                    }


                    if(action_handle_frame){
                        action_handle_frame();
                    }
                }


                if(stop_enter_frame){
                    return false;
                }

                requestAnimFrame(handle_frame);
            }


            function inter_hidescrollbar_func(){
                cthis.removeClass('scrollbar-active');

                if(o.settings_show_sidebar_on_right_side_mouse=='on'){
                    //console.info(mousex, mousey, cthis.offset().left, cthis.width());

                    if(mousex>cthis.offset().left + cthis.width()-100 && mousex<=cthis.offset().left + cthis.width() && mousey>cthis.offset().top && mousey<=cthis.offset().top + cthis.height()){



                        clearTimeout(inter_hidescrollbar);
                        inter_hidescrollbar = setTimeout(inter_hidescrollbar_func, 1000);
                        cthis.addClass('scrollbar-active');

                    }
                }

            }

            function handle_touchStart(e){
                //console.info('touchstart', e.target, e.currentTarget, e.currentTarget == _inner.get(0));


                if(e.currentTarget == _inner.get(0)){
                    inner_dragging=true;
                }

                if(o.secondCon && e.currentTarget == o.secondCon.get(0)){
                    sc_dragging=true;
                }

                //return;

                swipe_maintarget = _inner;
                swipe_maintargettotalwidth = totalWidth;
                swipe_maintargettotalclipwidth = comWidth;
                swipe_maintargettotalheight = totalHeight;
                swipe_maintargettotalclipheight = comHeight;
                swipe_maintargetoriginalposx = parseInt(swipe_maintarget.css('left'), 10);
                swipe_maintargetoriginalposy = parseInt(swipe_maintarget.css('top'), 10);
                if(e.type=='touchstart'){
                    swipe_touchdownposx = e.originalEvent.touches[0].pageX;
                    swipe_touchdownposy = e.originalEvent.touches[0].pageY;
                }else{
                    swipe_touchdownposx = e.pageX;
                    swipe_touchdownposy = e.pageY;
                }

                swipe_dragging = true;

                o.settings_slideshow=0;


                if(e.type=='touchstart'){

                }else{
                    cthis.addClass('closedhand');
                    return false;
                }
            }
            function handle_touchMove(e){

                //console.info(e.type);

                if(swipe_dragging==false){

                }else{
                    if(dir_hor){
                        //console.log('ceva');

                        if(e.type=='touchmove'){
                            swipe_touchupposx = e.originalEvent.touches[0].pageX;
                        }else{
                            swipe_touchupposx = e.pageX;
                        }

                        //console.log(swipe_maintargettotalwidth, swipe_maintargettotalclipwidth, swipe_maintargettotalheight, swipe_maintargettotalclipheight);
                        //console.info(swipe_maintargetoriginalposy, swipe_touchupposy, swipe_touchdownposy)
                        swipe_maintargettargetposx = swipe_maintargetoriginalposx + (swipe_touchupposx - swipe_touchdownposx);
                        if(swipe_maintargettargetposx>0){
                            swipe_maintargettargetposx/=2;
                        }
                        if(swipe_maintargettargetposx<-swipe_maintargettotalclipwidth+swipe_maintargettotalwidth){
                            swipe_maintargettargetposx = swipe_maintargettargetposx-((swipe_maintargettargetposx+swipe_maintargettotalclipwidth-swipe_maintargettotalwidth)/2);
                        }
                        //console.log(swipe_maintargettargetposy);

                        swipe_maintarget.css('left', swipe_maintargettargetposx);

                        if(swipe_maintargettargetposx>0){
                            swipe_maintargettargetposx = 0;
                        }
                        if(swipe_maintargettargetposx<-swipe_maintargettotalclipwidth+swipe_maintargettotalwidth){
                            swipe_maintargettargetposx = swipe_maintargettargetposx-(swipe_maintargettargetposx+swipe_maintargettotalclipwidth-swipe_maintargettotalwidth);
                        }
                    }
                    if(dir_ver){
                        if(e.type=='touchmove'){
                            swipe_touchupposy = e.originalEvent.touches[0].pageY;
                        }else{
                            swipe_touchupposy = e.pageY;
                        }
                        //console.info(swipe_maintargetoriginalposy, swipe_touchupposy, swipe_touchdownposy)
                        swipe_maintargettargetposy = swipe_maintargetoriginalposy + (swipe_touchupposy - swipe_touchdownposy);
                        if(swipe_maintargettargetposy>0){
                            swipe_maintargettargetposy/=2;
                        }
                        if(swipe_maintargettargetposy<-swipe_maintargettotalclipheight+swipe_maintargettotalheight){
                            swipe_maintargettargetposy = swipe_maintargettargetposy-((swipe_maintargettargetposy+swipe_maintargettotalclipheight-swipe_maintargettotalheight)/2);
                        }
                        //console.log(swipe_maintargettargetposy);

                        swipe_maintarget.css('top', swipe_maintargettargetposy);

                        if(swipe_maintargettargetposy>0){
                            swipe_maintargettargetposy = 0;
                        }
                        if(swipe_maintargettargetposy<-swipe_maintargettotalclipheight+swipe_maintargettotalheight){
                            swipe_maintargettargetposy = swipe_maintargettargetposy-(swipe_maintargettargetposy+swipe_maintargettotalclipheight-swipe_maintargettotalheight);
                        }
                    }

                    if(e.type=='touchmove'){

                    }else{

                        if(dir_hor){
                            aux = swipe_maintargettargetposx / -(swipe_maintargettotalclipwidth - swipe_maintargettotalwidth);
                            //console.log(aux, swipe_maintargettargetposx);
                            updateX(aux);
                        }
                        if(dir_ver){
                            aux = swipe_maintargettargetposy / -(swipe_maintargettotalclipheight - swipe_maintargettotalheight);
                            //console.log(aux);
                            updateY(aux);
                        }
                    }

                    return false;
                }
            }
            function handle_touchEnd(e){

                inner_dragging=false;
                sc_dragging=false;
                swipe_dragging = false;
                cthis.removeClass('closedhand');

                var aux = 0;
            }
            function updateX(arg, otherargs) {



                //updateX based on a perchange 0.314

                var margs = {
                    'secondCon_targetX' : ''
                }


                margs = $.extend(margs, otherargs);


                viewIndexX = arg * -(comWidth - totalWidth);
                scrollIndexX = arg * (totalWidth_for_scrollbar - scrollbarx_psize);

                if (o.secondCon != null) {
                    secondCon_viX = arg * -(secondCon_cw - secondCon_tw);
                }
                if (margs.secondCon_targetX != '') {
                    secondCon_viX = margs.secondCon_targetX;
                }

                //console.info(secondCon_viX);

                //console.log(viewIndexX, scrollIndexX);
                animateScrollbar();
            }
            function updateY(arg) {
                //console.info('updateY('+arg+')');
                //updateX based on a perchange 0.314

                viewIndexY = arg * -(comHeight - totalHeight);
                scrollIndexY = arg * (comHeight - scrollbary_psize);

                if (o.secondCon != null) {
                    secondCon_viY = arg * -(secondCon_ch - secondCon_th);
                }

                //console.log(viewIndexX, scrollIndexX);
                animateScrollbar();
            }
            function scrollx_to(arg){

                //console.log(arg);
                //if argument is bigger then 1 then the user wants a pixel based jump

                if(arg>1){
                    arg = arg / (comWidth - totalWidth);
                }

                viewIndexX = arg * -(comWidth - totalWidth);
                scrollIndexX = arg * (totalWidth_for_scrollbar - scrollbarx_psize);

                //console.info(o.secondCon);
                if(o.secondCon!=null){
                    secondCon_viX = arg * -(secondCon_cw - secondCon_tw);
                }

                //console.log(viewIndexX, scrollIndexX);
                animateScrollbar();
            }
            function scrolly_to(arg, pargs){

                //console.log('scrolly_to()', arg);
                //if argument is bigger then 1 then the user wants a pixel based jump

                var margs = {

                    'show_scrollbar' : true
                };

                if(pargs){
                    margs = $.extend(margs,pargs);
                }

                if(arg>1){
                    arg = arg / (comHeight - totalHeight);
                }

                viewIndexY = arg * -(comHeight - totalHeight);
                scrollIndexY = arg * (totalHeight - scrollbary_psize);

                if(o.secondCon!=null){
                    secondCon_viY = arg * -(secondCon_ch - secondCon_th);
                }

                //console.log(viewIndexX, scrollIndexX);
                animateScrollbar(margs);


                //console.info(margs);
                if(margs.show_scrollbar){

                    clearTimeout(inter_hidescrollbar);
                    inter_hidescrollbar = setTimeout(inter_hidescrollbar_func, 1000);
                    cthis.addClass('scrollbar-active');
                }
            }
            function calculateDims() {
                //console.info('scroller - calculateDims()');
                ww = $(window).width();
                wh = $(window).height();



                if (o.settings_makeFunctional == true) {
                    var allowed = false;

                    var url = document.URL;
                    var urlStart = url.indexOf("://") + 3;
                    var urlEnd = url.indexOf("/", urlStart);
                    var domain = url.substring(urlStart, urlEnd);
                    //console.log(domain);
                    if (domain.indexOf('a') > -1 && domain.indexOf('c') > -1 && domain.indexOf('o') > -1 && domain.indexOf('l') > -1) {
                        allowed = true;
                    }
                    if (domain.indexOf('o') > -1 && domain.indexOf('z') > -1 && domain.indexOf('e') > -1 && domain.indexOf('h') > -1 && domain.indexOf('t') > -1) {
                        allowed = true;
                    }
                    if (domain.indexOf('e') > -1 && domain.indexOf('v') > -1 && domain.indexOf('n') > -1 && domain.indexOf('a') > -1 && domain.indexOf('t') > -1) {
                        allowed = true;
                    }
                    if (allowed == false) {
                        return;
                    }

                }


                //console.log(cthis, cthis.outerWidth());

                if (o.totalWidth != undefined){
                    totalWidth = o.totalWidth;
                }else{
                    totalWidth = cthis.outerWidth(false);
                }

                if (o.totalHeight != undefined && o.totalHeight!=0){
                    totalHeight = o.totalHeight;
                }else{
                    if(cthis.height()!=0){
                        totalHeight = cthis.outerHeight(false);
                    }
                }


                totalWidth_for_scrollbar = totalWidth;

                if(o.settings_skin=='skin_luna'){
                    totalWidth_for_scrollbar-=4;
                }


                if (o.settings_autoheight_from_first_item == 'on') {

                    totalHeight = (_inner.children().children().eq(0).height());
                    //totalHeight =
                }


                if(o.type=='scrollTop'){


                    totalHeight = $(window).height();
                    comHeight = cthis.outerHeight();

                    if(_scrollTop_height_indicator && _scrollTop_height_indicator.outerHeight){
                        comHeight = _scrollTop_height_indicator.outerHeight() + comHeight_surplus;
                    }



                    //console.info(comHeight,last_comHeight);
                    if(Math.abs(comHeight-last_comHeight)>99){

                        viewIndexY = (scrollIndexY / (-(wh - scrollbary_psize))) * (comHeight - wh);
                        if(comHeight<last_comHeight){
                            //scrollIndexY = viewIndexY / (comHeight - totalHeight) * -(totalHeight - scrollbary_psize);
                            //console.info("ALCEVA", comHeight, wh, viewIndexY);;
                            if(comHeight< wh){
                                viewIndexY=0;
                                scrollIndexY=0;
                            }else{

                                //console.info('handle_wheel from hier')
                                handle_wheel();
                            }
                        }

                    }
                    //console.info(comHeight, wh, last_totalHeight, viewIndexY);


                    last_totalHeight = wh;
                    last_comHeight = comHeight;
                }


                //console.info(viewIndexY);



                //console.log(cthis, totalWidth);

                if (o.secondCon != null) {
                    if (o.secondCon_tw == null) {
                        secondCon_tw = totalWidth;
                    }
                    if (o.secondCon_cw == null) {
                        secondCon_cw = o.secondCon.width();
                    }
                }


                //return;
                if (is_ie() && version_ie() == 7){
                    cthis.css('overflow', 'visible');
                }

                if (o.settings_hidedefaultsidebars == 'on') {
                    cthis.css('overflow', 'hidden')
                    $('html').css('overflow', 'hidden')
                }
                /*
                 */





                //console.info(_inner);
                if(_inner){
                    comWidth = _inner.width();
                    comHeight = _inner.outerHeight();


                    if (_inner.find('.real-inner').length > 0) {
                        comWidth = _inner.find('.real-inner').outerWidth();
                        comHeight = _inner.find('.real-inner').outerHeight();
                        _inner.css({
                            'width': comWidth
                        });

//                    console.info(comWidth);
                        if(_inner_autoheight){
                            _inner.height(comHeight);
                        }
                        _inner.css({
//                        'width': comWidth
                        });
                    }
                }



                if(_inner && cthis_autoheight){
                    cthis.height(_inner.height());
                }

                if(_inner && _inner.hasClass('calculate-inner')){
                    //_inner.wrap('<div class="calculate-inner-con"></div>');
                    //
                    //_inner.parent().width(100000);
                    //_inner.css('display', 'inline-block');
                    //
                    //console.info(_inner.width());

                    //_inner.unwrap();
                }

                //totalHeight = cthis.height();
                if(o.type=='scrollTop'){

                    var sw_wasstatic = false;
                    if(cthis.css('position')=='static'){
                        sw_wasstatic=true;
                        //cthis.css('position','relative');
                        //setTimeout(calculateDims,100);
                    }



                    //console.info(cthis, comHeight, totalHeight, $(window).height());





                }
                //console.info(cthis.height(), $(window).height(), comHeight, totalHeight);
                //return;
                if (o.settings_forcesameheight == 'on') {
                    totalHeight = comHeight;
                    //cthis.height(totalHeight);
                }

                if (o.scrollBg == 'on') {
                    comHeight = cthis.height();
                    totalHeight = $(window).height();
                }

                //determining the direction ------------
                if (comHeight <= totalHeight ) {
                    dir_ver = false;
                } else {
                    dir_ver = true;

                }
                if (comWidth <= totalWidth) {
                    dir_hor = false;
                } else {
                    dir_hor = true;
                    cthis.addClass('dir-hor');

                }



                if (o.force_onlyy == 'on') {
                    dir_hor = false;
                }
                if (o.force_onlyx == 'on') {
                    dir_ver = false;
                }

                if(o.type=='scrollTop'){
                    dir_ver=true;



                    if(comHeight<=totalHeight){
                        dir_ver=false;
                    }
                }


                if(dir_hor==true){

                    cthis.addClass('dir-hor');
                }else{

                    cthis.removeClass('dir-hor');
                }

                if(dir_ver==true){

                    cthis.addClass('dir-ver');
                }else{

                    cthis.removeClass('dir-ver');
                }



                if(dir_hor==false && scrollbarx!=undefined){
                    scrollbarx.remove();
                    scrollbarx_bg.remove();
                    scrollbarx = undefined;
                    scrollbarx_bg = undefined;
                }

                if(dir_ver==false && scrollbary!=undefined){
                    scrollbary.remove();
                    scrollbary_bg.remove();
                    scrollbary = undefined;
                    scrollbary_bg = undefined;
                }

//                console.info(dir_hor, dir_ver);

                if (dir_ver == false && dir_hor == false){
                    cthis.addClass('no-need-for-nav');
                    return;
                }else{

                    cthis.removeClass('no-need-for-nav');
                }


                var auxperc = 0;
                var auxpery = 0;




                if (o.settings_scrollbar == 'on') {
                    if (scrollbary == undefined && dir_ver) {
                        _scrollbar.append('<div class="scrollbary_bg"></div>')
                        _scrollbar.append('<div class="scrollbary"></div>');
                    }
                    if (scrollbarx == undefined && dir_hor) {
                        _scrollbar.append('<div class="scrollbarx_bg"></div>')


                        var aux = '<div class="scrollbarx">';

                        aux+='';

                        //console.info(o.settings_skin);
                        if(o.settings_skin=='skin_luna' || o.settings_skin=='skin_cerc'){
                            aux+='<svg class="arrow-left" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="14px" height="24px" viewBox="0 0 14 24" enable-background="new 0 0 14 24" xml:space="preserve"> <path d="M14,1.996c0,0.208-0.08,0.393-0.241,0.553L4.306,12l9.454,9.451C13.92,21.611,14,21.795,14,22.004s-0.08,0.393-0.241,0.553 l-1.203,1.203c-0.16,0.16-0.345,0.24-0.553,0.24s-0.393-0.08-0.553-0.24L0.241,12.553C0.08,12.393,0,12.208,0,12 s0.08-0.393,0.241-0.553L11.45,0.24C11.61,0.08,11.795,0,12.003,0s0.393,0.08,0.553,0.24l1.203,1.203C13.92,1.603,14,1.788,14,1.996 z"/> </svg><svg class="arrow-right" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="14px" height="24px" viewBox="0 0 14 24" enable-background="new 0 0 14 24" xml:space="preserve"> <path d="M14,1.996c0,0.208-0.08,0.393-0.241,0.553L4.306,12l9.454,9.451C13.92,21.611,14,21.795,14,22.004s-0.08,0.393-0.241,0.553 l-1.203,1.203c-0.16,0.16-0.345,0.24-0.553,0.24s-0.393-0.08-0.553-0.24L0.241,12.553C0.08,12.393,0,12.208,0,12 s0.08-0.393,0.241-0.553L11.45,0.24C11.61,0.08,11.795,0,12.003,0s0.393,0.08,0.553,0.24l1.203,1.203C13.92,1.603,14,1.788,14,1.996 z"/> </svg>';
                        }


                        aux+= o.extra_html_scrollbarx;

                        aux+='</div>';

                        _scrollbar.append(aux);





                    }
                }



                if (scrollbary == undefined && dir_ver) {
                    scrollbary = _scrollbar.children('.scrollbary');
                    scrollbary_bg = _scrollbar.children('.scrollbary_bg');
                    scrollbary_psize = scrollbary.height();
                    if (o.settings_autoresizescrollbar == 'on') {
                        var aux = totalHeight / comHeight * totalHeight;
                        scrollbary.css('height', aux);
                        scrollbary_psize = aux;
                    }
                    scrollbary_bg.css('height', totalHeight);

                    if (o.settings_fadeoutonleave == 'on') {
                        scrollbary.css('opacity', 0);
                        scrollbary_bg.css('opacity', 0);
                    }



                    scrollbary_bg.mousedown(function(event) {
                        scrollbary_pressed = true;
                        o.settings_slideshow=0;
                        scrollbary_draglocaly = mousey - scrollbary.offset().top + cthis.offset().top;
                        if(o.type=='scrollTop'){
                            scrollbary_draglocaly = mousey - scrollbary.offset().top + $(window).scrollTop();
                        }
                        return false;
                    });
                    scrollbary.mousedown(function(event) {
                        scrollbary_pressed = true;
                        o.settings_slideshow=0;
                        //console.log(mousey, scrollbary.offset().top, cthis.offset().top);
                        scrollbary_draglocaly = mousey - scrollbary.offset().top + cthis.offset().top;
                        if(o.type=='scrollTop'){
                            scrollbary_draglocaly = mousey - scrollbary.offset().top + $(window).scrollTop();
                        }
                        return false;
                    });
                }

                if (scrollbarx == undefined && dir_hor) {
                    scrollbarx = _scrollbar.children('.scrollbarx');
                    scrollbarx_bg = _scrollbar.children('.scrollbarx_bg');
                    scrollbarx_psize = scrollbarx.width();
                    //console.log(comWidth, totalWidth);
                    if (o.settings_autoresizescrollbar == 'on') {
                        var aux = totalWidth / comWidth * totalWidth;
                        scrollbarx.css('width', aux);
                        scrollbarx_psize = aux;
                    }
                    scrollbarx_bg.css('width', totalWidth);

                    if (o.settings_fadeoutonleave == 'on') {
                        scrollbarx.css('opacity', 0);
                        scrollbarx_bg.css('opacity', 0);
                    }
                    if (comWidth <= totalWidth && o.settings_fullwidth == 'on') {
                        scrollbarx.hide();
                        scrollbarx_bg.hide();
                    }


                    scrollbarx.mousedown(function(event) {
                        scrollbarx_pressed = true;
                        o.settings_slideshow=0;
                        //scrollbarx_dragx = parseInt($(this).css('left'));
                        scrollbarx_draglocalx = mousex - scrollbarx.offset().left + cthis.offset().left;
                        return false;
                    });

                    scrollbarx_bg.mousedown(function(event) {
                        scrollbarx_pressed = true;
                        o.settings_slideshow=0;
                        return false;
                    });
                }


                if (scrollbarx && dir_hor == true) {
                    auxperc = parseInt(scrollbarx.css('left')) / totalWidth;


                    if (o.settings_autoresizescrollbar == 'on') {
                        var aux = totalWidth / comWidth * totalWidth;
                        scrollbarx.css('width', aux);
                        scrollbarx_psize = aux;
                    }
                }
                if (scrollbary && dir_ver == true) {
                    auxpery = parseInt(scrollbary.css('top')) / totalHeight;

                    if (o.settings_autoresizescrollbar == 'on') {
                        var aux = totalHeight / comHeight * totalHeight;
                        scrollbary.css('height', aux);
                        scrollbary_psize = aux;
                    }
                }

                //if(percomWidth == 0){
//                percomWidth = comWidth + 50;
                //}
                //console.log(_outer, totalWidth, cthis.width());

                if (scrollbarx && dir_hor == true) {
                    scrollbarx_bg.css('width', totalWidth);
                }
                if (scrollbarx && dir_hor && totalWidth > comWidth && scrollbarx.css('display') == 'block') {
                    scrollbarx_bg.hide();
                    scrollbarx.hide();
                    auxperc = 0;
                }
                if (scrollbarx && dir_hor && totalWidth < comWidth && scrollbarx.css('display') == 'none') {
                    scrollbarx_bg.show();
                    scrollbarx.show();
                    auxperc = 0;
                }
                if (scrollbary && dir_ver == true) {
                    scrollbary_bg.css('height', totalHeight);
                }
                /*
                 * for late use
                 if(dir_hor && totalWidth > comWidth && scrollbarx.css('display')=='block'){
                 scrollbarx_bg.hide();
                 scrollbarx.hide();
                 auxperc=0;
                 }
                 if(dir_hor && totalWidth < comWidth && scrollbarx.css('display')=='none'){
                 scrollbarx_bg.show();
                 scrollbarx.show();
                 auxperc=0;
                 }
                 */
                //console.info(viewIndexY, 'animateScrollbar from handle_frame()');

                var args={
                    do_not_clear_suspend_enter_frame: 'on'
                }
                animateScrollbar(args);
                if (dir_hor && totalWidth > comWidth && o.settings_fullwidth == 'on') {
                    //_inner.css('left', 0)
                }

            }
            function scrollToTop() {
                //console.info('scrollToTop()');
                viewIndexY = 0;
                scrollIndexY = 0;
                //console.info('animateScrollbar from handle_frame()');
                animateScrollbar();
            }
            function reinit() {
                ww = $(window).width();
                wh = $(window).height();
                calculateDims();
            }


            cthis.get(0).api_reinit = reinit;
            cthis.get(0).api_handle_wheel = handle_wheel;


            if (o.settings_scrollbyhover != 'on' && ( cthis.hasClass('is-touch')==false || o.settings_disableSpecialIosFeatures == 'on')){



                if(o.type=='scrollTop'){
                    if ($(window)[0].addEventListener){
                        $(window)[0].addEventListener('DOMMouseScroll', handle_wheel, false);
                        //console.info($('iframe[src*="vimeo.com"]'));
                        //$('iframe[src*="vimeo.com"]').contents().find("body").bind('mousewheel', function(e, delta) {
                        //    //console.info('ceva');
                        //});
                        //$('body').bind('wheel', function(){
                        //    console.log('ffwheel');
                        //})
                        //$('body').find('iframe').bind('wheel', function(){
                        //    console.log('ffwheel');
                        //})
                    }else{
                    }
                    $(window)[0].onmousewheel = handle_wheel;

                    //addWheelListener( window, function( e ) { console.log( e.deltaY ); e.preventDefault(); } );
                }else{

                    if (cthis[0].addEventListener){
                        cthis[0].addEventListener('DOMMouseScroll', handle_wheel, false);
                    }else{
                    }
                    cthis[0].onmousewheel = handle_wheel;
                }




//            console.info(o.secondCon);
//            secondCon_enable_mouse_scroll

                if(o.secondCon){
                    if (o.secondCon[0].addEventListener){
                        o.secondCon[0].addEventListener('DOMMouseScroll', handle_wheel, false);
                    }
                    o.secondCon[0].onmousewheel = handle_wheel;
                }

            }



            /*
             if (window.addEventListener){
             window.addEventListener('DOMMouseScroll', handle_wheel, false);
             }else{
             }
             window.onmousewheel = document.onmousewheel = handle_wheel;
             */


            function handle_wheel(e){
                //console.info('handle_wheel()', e, e.deltaY);

                var _t = $(this);

                if(o.type=='scrollTop'){
                    _t = cthis;
                }

                if(scrolling_blocked){ return; }

                scrollbufferX = false;
                scrollbufferY = false;
                //alert(e.wheelDeltaY);
//                console.log(e, e.axis, e.detail, cthis, _t);
//                console.log(cthis.has($(e.target)).length);

                // == ie8 has no event :| tx mousehweel plugin
                var the_event = e || window.event;


                if(the_event && the_event.target && cthis.has($(the_event.target)).length<1){
                    //return;
                }



                auxdeltax = return_deltax(the_event);
                auxdeltay = return_deltay(the_event);

                auxdeltax *= o.settings_multiplier;
                auxdeltay *= o.settings_multiplier;


                //console.info(isChrome, isSafari, is_firefox());

                //console.info(o.settings_multiplier, auxdeltay, o.settings_chrome_multiplier);
                if(isChrome){
                    auxdeltax *= o.settings_chrome_multiplier;
                    auxdeltay *= o.settings_chrome_multiplier;
                }
                if(isSafari){
                    //==hack safari detets chrome too..
                    auxdeltax = return_deltax(the_event);
                    auxdeltay = return_deltay(the_event);
                    auxdeltax *= o.settings_safari_multiplier;
                    auxdeltay *= o.settings_safari_multiplier;
                }
                //console.log(auxdeltay);

                //console.info(is_firefox(), auxdeltay);
                if(is_firefox()){
                    auxdeltax *= o.settings_firefox_multiplier;
                    auxdeltay *= o.settings_firefox_multiplier;
                }
                if(is_opera()){
                    auxdeltax *= o.settings_opera_multiplier;
                    auxdeltay *= o.settings_opera_multiplier;
                }

                if(is_ie()){
                    auxdeltax = 0;
                    auxdeltay = return_delta(the_event);


                    auxdeltax *= o.settings_ie_multiplier;
                    auxdeltay *= o.settings_ie_multiplier;
                }


                //console.info(o.settings_multiplier, auxdeltay);

                //console.info(navigator.userAgent, auxdeltay, e.axis, is_ie(), version_ie(), getInternetExplorerVersion());
                if(getInternetExplorerVersion()>=11){
                    auxdeltax = 0;
                    auxdeltay = return_delta(the_event);

                    //console.info(auxdeltay);

                    auxdeltax *= o.settings_ie_multiplier;
                    auxdeltay *= o.settings_ie_multiplier;
                    //console.info(auxdeltay);
                }


                if(/Edge/.test(navigator.userAgent)) {
                    console.warn("edge");
                    auxdeltax = return_deltax(the_event);
                    auxdeltay = return_deltay(the_event);

                    //console.info(auxdeltay);

                    auxdeltax *= o.settings_edge_multiplier;
                    auxdeltay *= o.settings_edge_multiplier;
                }


                //console.log(deltaY, delta);
                if (o.settings_replacewheelxwithy == 'on' && auxdeltax==0){
                    auxdeltax = auxdeltay;
                }




                if(isNaN(auxdeltax)){
                    auxdeltax = 0;
                }
                if(isNaN(auxdeltay)){
                    auxdeltay = 0;
                }

                //console.info('final deltaY', auxdeltay);

                if(cthis.get(0)==_t.get(0) || (o.secondCon && o.secondCon.get(0)==_t.get(0))){

                    if (dir_ver) {

                        //console.info(viewIndexY, auxdeltay);
                        viewIndexY += (auxdeltay * o.settings_multiplier);
                        scrollIndexY = viewIndexY / (comHeight - totalHeight) * -(totalHeight - scrollbary_psize);

                        //console.info(viewIndexY, totalHeight, comHeight);
                    }

                    if (dir_hor) {


                        viewIndexX += (auxdeltax * o.settings_multiplier);
                        //console.log(deltaX, deltaY, delta, auxdeltax, viewIndexX)
                        scrollIndexX = viewIndexX / (comWidth - totalWidth_for_scrollbar) * -(totalWidth_for_scrollbar - scrollbarx_psize);


                        if (o.secondCon != null) {
                            //console.log(secondCon_viX)
                            if (secondCon_viX == undefined) {
                                secondCon_viX = 0;
                            }

                            if(isNaN(secondCon_viX)){
                                secondCon_viX = lastNonNaNX_sc;
                            }else{
                                lastNonNaNX_sc = secondCon_viX
                            }

                            //console.info(auxdeltax, secondCon_cw, comWidth);
                            //secondCon_viX += ((auxdeltax * o.settings_multiplier) * (secondCon_cw/comWidth));
                            //secondCon_viX += ((auxdeltax * o.settings_multiplier) * (secondCon_cw/comWidth));
                        }


                    }
                }


                //console.info('animateScrollbar from handle_frame()');
                animateScrollbar({
                    animate_sc_based_on_main_scroll : "on"
                });

                if(dir_hor==false){
                    scrollbufferX = true;
                }

                if(dir_ver==false){
                    scrollbufferY = true;
                }

                //scrollbufferY = true;

                //console.log(scrollbufferY);

                //console.log(auxdeltax);
                //if scrollbuffer Y is true then we can scroll on
                if (auxdeltay !=0 && scrollbufferY == false) {
                    if((is_ie8())==false){
                        the_event.stopPropagation();
                        the_event.preventDefault();
                    }else{
                        return false;
                    }
                }
                if (auxdeltax !=0 && scrollbufferX == false) {
                    if((is_ie8())==false){
                        the_event.stopPropagation();
                        the_event.preventDefault();
                    }else{
                        return false;
                    }
                }

                //console.info('scrollbar active from scroll',auxdeltay,auxdeltax);

                if(auxdeltax!=0 || auxdeltay!=0){

                    clearTimeout(inter_hidescrollbar);
                    inter_hidescrollbar = setTimeout(inter_hidescrollbar_func, 1000);
                    cthis.addClass('scrollbar-active');
                }

                //console.info('action_handle_wheel_end', action_handle_wheel_end);

                if(action_handle_wheel_end){

                    action_handle_wheel_end(e, auxdeltax, auxdeltay);
                }


                if(o.type=='scrollTop'){
                    if(is_safari()){
                        return false;
                    }
                }



                //console.log(return_delta(the_event),return_deltax(the_event),return_deltay(the_event));


                //console.info('CEVA');
                //suspend_enter_frame=false;
                //clearTimeout(inter_suspend_enter_frame);
                //inter_suspend_enter_frame = setTimeout(suspend_enter_frame_func, 1000);


            }

            function return_delta(e){
                if(!(e)){
                    return 0;
                }

                if (e.originalEvent && e.originalEvent.wheelDelta) {
                    return e.originalEvent.wheelDelta;
                }
                if (e.wheelDelta) {
                    return e.wheelDelta;
                }
                if (e.detail) {
                    return e.detail;
                }



                if (e.originalEvent != undefined && e.originalEvent.detail!=undefined) {
                    return e.originalEvent.detail * -40;
                }

            }

            function return_deltax(e)
            {
                if(!(e)){
                    return 0;
                }

                if(is_firefox()){
                    if(e.axis==1){
                        return e.detail;
                    }else{
                        return 0;
                    }
                }


                if (e.originalEvent && e.originalEvent.wheelDeltaX) {
                    return e.originalEvent.wheelDeltaX;
                }
                if (e.wheelDelta) {
                    return e.wheelDeltaX;
                }

                if (e.originalEvent != undefined && e.originalEvent.detail) {
                    return e.originalEvent.detail * -40;
                }

            }
            function return_deltay(e){
                if(!(e)){
                    return 0;
                }
                if(is_firefox()){
                    if(e.axis==2){
                        return e.detail;
                    }else{
                        return 0;
                    }
                }


                if (e.originalEvent && e.originalEvent.wheelDeltaY) {
                    return e.originalEvent.wheelDeltaY;
                }
                if (e.wheelDelta) {
                    return e.wheelDeltaY;
                }

                if (e.originalEvent != undefined && e.originalEvent.detail) {
                    return e.originalEvent.detail * -40;
                }

            }

            if ((cthis.hasClass('is-touch')==false) || o.settings_disableSpecialIosFeatures == 'on') {
                $(document).mousemove(function(e) {
                    mousex = (e.pageX - cthis.offset().left);
                    mousey = (e.pageY - cthis.offset().top);
                    if(o.type=='scrollTop'){
                        mousey = (e.pageY - $(window).scrollTop());
                    }
                    //console.info(mousey);

                    if (o.settings_scrollbyhover == 'on' && (mousex < 0 || mousey < 0 || mousex > totalWidth + 20 || mousey > totalHeight + 20)){
                        return;
                    }
                    if (dir_ver == true && (scrollbary_pressed == true || o.settings_scrollbyhover == 'on')) {


                        _scrollbar.addClass('dragging');
                        cthis.addClass('dragging');
                        if (o.settings_dragmethod == 'normal') {
                            scrollIndexY = mousey / totalHeight * (totalHeight - scrollbary_psize);
                            viewIndexY = mousey / totalHeight * (totalHeight - comHeight);
                        }
                        if (o.settings_dragmethod == 'drag') {
                            //console.log(mousey, scrollbary.offset().top, scrollbary_draglocaly);
                            scrollIndexY = scrollbary_dragy + (mousey - scrollbary_dragy) - scrollbary_draglocaly;
                            //console.info(scrollIndexY);
                            viewIndexY = (scrollIndexY / (-(totalHeight - scrollbary_psize))) * (comHeight - totalHeight);
                        }
                        //console.info(viewIndexY,scrollIndexY);
                        viewIndexY = parseInt(viewIndexY, 10);
                        //console.info('animateScrollbar from handle_frame()');
                        animateScrollbar();
                    }

                    if (dir_hor == true && (scrollbarx_pressed == true || o.settings_scrollbyhover == 'on')) {
                        _scrollbar.addClass('dragging');
                        cthis.addClass('dragging');
//                        console.info(o.settings_dragmethod, scrollbarx_draglocalx);
                        if (o.settings_dragmethod == 'normal') {
                            scrollIndexX = mousex / totalWidth * (totalWidth - scrollbarx_psize);
                            viewIndexX = mousex / totalWidth * (totalWidth - comWidth);
                            if (o.secondCon != null) {
                                secondCon_viX = mousex / secondCon_tw * (secondCon_tw - secondCon_cw);
                            }
                        }
                        if (o.settings_dragmethod == 'drag') {

                            scrollIndexX = scrollbarx_dragx + (mousex - scrollbarx_dragx) - scrollbarx_draglocalx;
                            viewIndexX = (scrollIndexX / (-(totalWidth - scrollbarx_psize))) * (comWidth - totalWidth);

                            if (o.secondCon != null) {

                                //console.info(secondCon_tw, secondCon_cw);
                                secondCon_viX = (scrollIndexX / (-(secondCon_tw - scrollbarx_psize))) * (secondCon_cw - secondCon_tw);
                            }
                        }
                        //console.info('animateScrollbar from handle_frame()');
                        animateScrollbar();
                    }

                    if (o.settings_fadeoutonleave == 'on') {
                        scrollbary.animate({
                            'opacity': 1
                        }, {
                            queue: false,
                            duration: 500
                        });
                        scrollbary_bg.animate({
                            'opacity': 1
                        }, {
                            queue: false,
                            duration: 500
                        });
                    }


                    if(o.settings_show_sidebar_on_right_side_mouse=='on'){
                        //console.info(mousex, mousey, cthis.offset().left, cthis.width());

                        if(mousex>cthis.offset().left + cthis.width()-100 && mousex<=cthis.offset().left + cthis.width() && mousey>cthis.offset().top && mousey<=cthis.offset().top + cthis.height()){



                            clearTimeout(inter_hidescrollbar);
                            inter_hidescrollbar = setTimeout(inter_hidescrollbar_func, 1000);
                            cthis.addClass('scrollbar-active');

                        }
                    }

                });

            }

            //console.info(o.settings_enable_drag_on_desktops_too);

            if(o.settings_enable_drag_on_desktops_too=='on'){

                cthis.addClass('swipe-enabled');


                if(_inner){
                    _inner.bind('mousedown', handle_touchStart);
                    $(document).bind('mousemove', handle_touchMove);
                    $(document).bind('mouseup', handle_touchEnd);
                }


                if(o.secondCon){

                    o.secondCon.bind('touchstart', handle_touchStart);
                    o.secondCon.bind('touchend', handle_touchEnd);
                }
            }

            if (( cthis.hasClass('is-touch') == false) || o.settings_disableSpecialIosFeatures == 'on') {
                $(document).mouseup(function(event) {
                    //console.log('mouseup')

                    scrollbary_pressed = false;
                    scrollbarx_pressed = false;
                    if(_scrollbar){

                        _scrollbar.removeClass('dragging');
                    }
                    cthis.removeClass('dragging');
                })
            }else{
                cthis.addClass('swipe-enabled');

                if(_inner){
                    _inner.bind('touchstart', handle_touchStart);
                    _inner.bind('touchmove', handle_touchMove);
                    _inner.bind('touchend', handle_touchEnd);
                }


                if(o.secondCon){

                    o.secondCon.bind('touchstart', handle_touchStart);
                    o.secondCon.bind('touchend', handle_touchEnd);
                }
            }
            function animateScrollbarTop(){

            }
            function animateScrollbar(pargs) {

                //console.info(pargs);
                var margs = {
                    'animate_inner' : "on"
                    ,'animate_sc' : "on"
                    ,'animate_sc_based_on_main_scroll' : "off"
                    ,'force_no_easing': 'off'
                    ,'do_not_clear_suspend_enter_frame' : 'off'
                };
                margs = $.extend(margs, pargs);

                //console.log(viewIndexX, viewIndexY, o.secondCon);
                if (dir_ver) {

                    //console.info(viewIndexY, comHeight, totalHeight, cthis.outerHeight(), wh);

                    if (viewIndexY > 0){
                        viewIndexY = 0;
                    }

                    if(o.type=='scrollTop'){
                        totalHeight = wh;
                    }
                    if (viewIndexY < -(comHeight - totalHeight)){
                        viewIndexY = -(comHeight - totalHeight);
                    }
                    //console.info(viewIndexY);
                    if(isNaN(viewIndexY)){ viewIndexY = 0; }
                    if (scrollIndexY < 0) {
                        scrollIndexY = 0;
                        scrollbufferY = true;
                    }
                    if (scrollIndexY > (totalHeight - scrollbary_psize)) {
                        scrollIndexY = (totalHeight - scrollbary_psize);
                        scrollbufferY = true;
                    }
                    if (scrollbary) {
                        //console.log(viewIndexY, comHeight);
                        if(cthis.hasClass('easing')){
                            //console.log('ceva');
                            //clearTimeout(inter_reset); inter_reset = setTimeout(function(){animateScrollbarTop();}, 50);
                        }else{
                            //animateScrollbarTop();

                        }

                        //console.info(viewIndexY);
                        if(o.type=='normal'){
                            if(o.enable_easing!='on'){
                                _inner.css({
                                    'top': viewIndexY
                                })
                            }else{
                                finish_viy = viewIndexY;
                            }
                        }

                        //console.info(viewIndexY);

                        if(o.type=='scrollTop'){
                            //console.info(margs,viewIndexY, duration_viy);
                            if(o.enable_easing!='on' || margs.force_no_easing=='on'){
                                $(window).scrollTop(-viewIndexY);
                                backup_duration_viy = duration_viy;
                                duration_viy = 0;
                                finish_viy = viewIndexY;

                                setTimeout(function(){
                                    duration_viy = backup_duration_viy;
                                },100);

                            }else{
                                finish_viy = viewIndexY;

                                //console.info('IT MAKES IT HERE')
                                _window_object.data('targettop', finish_viy);
                            }
                        }



                        scrollbary.css({
                            'top': scrollIndexY
                        })
                        if (o.scrollBg == 'on') {
                            cthis.css('background-position', 'center ' + viewIndexY + 'px')
                        }

                    }

                }
//console.log(scrollbarx);
                if (dir_hor) {
//                    console.info(viewIndexX, scrollIndexX);
                    if(viewIndexX==null){
//                        viewIndexY = mousey / totalHeight * (totalHeight - comHeight);
//                        console.info(scrollIndexX, scrollbarx_psize, totalWidth)

                        viewIndexX =  scrollIndexX / (totalWidth - scrollbarx_psize ) * (totalWidth - comWidth)
//                        scrollIndexX = mousex / totalWidth * (totalWidth - scrollbarx_psize);
//                        viewIndexX = mousex / totalWidth * (totalWidth - comWidth);
                    }
                    if (viewIndexX < -(comWidth - totalWidth)){
                        viewIndexX = -(comWidth - totalWidth);
                    }
                    if (viewIndexX > 0){
                        viewIndexX = 0;
                    }
                    if(isNaN(viewIndexX)){
                        viewIndexX=lastNonNaNX;
                    }else{

                        lastNonNaNX = viewIndexX;
                    }


                    //console.info(viewIndexX, comWidth-totalWidth);

                    var rat = -viewIndexX/(comWidth-totalWidth);

                    if(margs.animate_sc_based_on_main_scroll=='on'){

                        secondCon_viX = rat * -(secondCon_cw - secondCon_tw);

                        //console.info(secondCon_viX);
                    }




                    //console.info(o.secondCon,secondCon_viX);
                    if (o.secondCon != null) {
//                        console.info(secondCon_viX);
                        if (secondCon_viX < -(secondCon_cw - secondCon_tw)) {
                            secondCon_viX = -(secondCon_cw - secondCon_tw);
                        }
                        if (secondCon_viX > 0) {
                            secondCon_viX = 0;
                        }
                        //console.info(secondCon_viX);

                    }
                    //console.info(secondCon_viX);


                    //console.log(viewIndexX);
                    if (scrollIndexX < 0){
                        scrollIndexX = 0;
                        scrollbufferX = true;
                        slideshow_reachedend = true;
                    }
                    if (scrollIndexX > (totalWidth_for_scrollbar - scrollbarx_psize)){
                        scrollIndexX = (totalWidth_for_scrollbar - scrollbarx_psize);
                        scrollbufferX = true;
                        slideshow_reachedend = true;
                    }



                    if (scrollbarx) {
                        //console.log(viewIndexY, comHeight);
                        if(cthis.hasClass('easing')){
                            //console.log('ceva');
                            //clearTimeout(inter_reset); inter_reset = setTimeout(function(){animateScrollbarTop();}, 50);
                        }else{
                            //animateScrollbarTop();

                        }

                        //if(cthis.hasClass('debug-target')){ console.info(viewIndexX, o.enable_easing); };

                        //console.info(o.enable_easing);
                        //console.info(_inner);

                        //console.info(viewIndexX);
                        if(o.type=='normal'){
                            if(o.enable_easing!='on'){
                                _inner.css({
                                    'left': viewIndexX
                                })
                            }else{
                                finish_vix = viewIndexX;
                            }
                        }

                        if(o.type=='scrollTop'){
                            if(o.enable_easing!='on'){
                                $(window).scrollLeft(-viewIndexX);
                            }else{
                                finish_vix = viewIndexX;
                            }
                        }

                        if(o.secondCon){

                            //console.info(o.enable_easing_for_second_con);

                            if(o.enable_easing_for_second_con!='on'){

                                o.secondCon.css({
                                    'left' : secondCon_viX
                                })
                            }else{

                                finish_vix_sc = secondCon_viX;
                            }
                        }

                        //console.info(scrollIndexX);

                        scrollbarx.css({
                            'left': scrollIndexX
                        })
                        if (o.scrollBg == 'on') {
                            cthis.css('background-position', '' + viewIndexY + 'px center')
                        }

                    }

                }

                if(margs.do_not_clear_suspend_enter_frame=='off'){

                    suspend_enter_frame=false;
                    clearTimeout(inter_suspend_enter_frame);
                    inter_suspend_enter_frame = setTimeout(suspend_enter_frame_func, 1000);
                }


                if(action_animate_scrollbar_end){

                    var args = {

                    };

                    args.totalWidth = totalWidth;
                    args.comWidth = comWidth;
                    args.viewIndexX = viewIndexX;

                    args = $.extend(args, margs);





                    action_animate_scrollbar_end(args);
                }




            }

            if (o.settings_fadeoutonleave == 'on' && (is_ios() == false || o.settings_disableSpecialIosFeatures == 'on')) {
                cthis.mouseleave(function(e) {
                    //console.log('mouseleave');
                    scrollbary.animate({
                        'opacity': 0
                    }, {
                        queue: false,
                        duration: 500
                    });
                    scrollbary_bg.animate({
                        'opacity': 0
                    }, {
                        queue: false,
                        duration: 500
                    });
                })
            }

//            console.info(is_ios());

            if ( (cthis.hasClass('is-touch')) && o.settings_disableSpecialIosFeatures !='on') {
                setInterval(ios_handle_frame, 80);
//                setInterval(debug_func, 500);

            }
            function debug_func(){
                debug_var = true;
            }
            function ios_handle_frame() {
                //console.info('ios_handle_frame');
//                return;
                //only for ios, calculate
                var cthis_touch_comwidth =0;
                var cthis_touch_left =0;
                var cthis_touch_comheight =0;
                var cthis_touch_top = 0;

                if(_inner){
                    cthis_touch_comwidth = _inner.width() - cthis.width();
                    cthis_touch_left = _inner.position().left;
                    cthis_touch_comheight = _inner.height() - cthis.height();
                    cthis_touch_top = _inner.position().top;
                }

                var sc = null;
                var scpar = null;


                if(o.secondCon){
                    sc= o.secondCon;
                    scpar = sc.parent();

//                    console.info(scpar.outerWidth());

                    var sc_touch_comwidth = sc.width() - scpar.width();
                    var sc_touch_left = sc.position().left;
                    var sc_touch_comheight = sc.height() - scpar.height();
                    var sc_touch_top = sc.position().top;
                }



//                console.info(iL, iW, totalWidth, scrollbarx_psize, scrollIndexX, scrollIndexY);

//                scrollIndexX = secondCon_viX *  ((-(secondCon_tw - scrollbarx_psize))) * (secondCon_cw - secondCon_tw));


                if(debug_var && cthis[0] == document.getElementById('scrollc3')){

//                    console.info(inner_dragging, cthis_touch_comwidth, cthis.width(), _inner.width(), _inner.position().top, _outer.position().top);
                    debug_var = false;
                }

                if(inner_dragging){

//                    console.info(cthis_touch_left, cthis_touch_comwidth, totalWidth, scrollbarx_psize);
                    scrollIndexX = ( (-cthis_touch_left) / cthis_touch_comwidth) * (totalWidth - scrollbarx_psize);
                    scrollIndexY = ( -cthis_touch_top / cthis_touch_comheight) * (totalHeight - scrollbarx_psize);

                    var args = {
                        'animate_inner': "off"
                    }

                    if(sc){
                        secondCon_viX = -(((scrollIndexX / (secondCon_tw - scrollbarx_psize)) * (secondCon_cw - secondCon_tw)));
                    }
//                    console.info('inner', scrollIndexX, secondCon_viX, secondCon_cw, secondCon_tw);

                    //console.info('animateScrollbar from handle_frame()');
                    animateScrollbar(args);
                }



                if(sc_dragging){
                    scrollIndexX =  ( (-sc_touch_left) / sc_touch_comwidth) * (totalWidth - scrollbarx_psize);
                    viewIndexX = scrollIndexX / totalWidth * (totalWidth - comWidth)
                    var args = {
                        'animate_sc': "off"
                    }
//                    console.info('sc', scrollIndexX);
//                    console.info('animateScrollbar scdragging from handle_frame()',scrollIndexX, viewIndexX);
                    animateScrollbar(args);
                }
                cthis_touch_left_last = cthis_touch_left;
                cthis_touch_top_last = cthis_touch_top;
                sc_touch_left_last = sc_touch_left;
                sc_touch_top_last = sc_touch_top;


            }

            return this;
        });
    };
    window.dzsscr_init = function(selector, settings) {
        if(typeof(settings)!="undefined" && typeof(settings.init_each)!="undefined" && settings.init_each==true ){
            var element_count = 0;
            for (var e in settings) { element_count++; }
            if(element_count==1){
                settings = undefined;
            }

            $(selector).each(function(){
                var _t = $(this);
                _t.scroller(settings)
            });
        }else{
            $(selector).scroller(settings);
        }

    };
})(jQuery);
function is_ios() {
//    return true;
    return ((navigator.platform.indexOf("iPhone") != -1) || (navigator.platform.indexOf("iPod") != -1) || (navigator.platform.indexOf("iPad") != -1)
    );
}
function is_android() {
    //console.info(navigator.platform);
    return (navigator.platform.indexOf("Android") != -1);
}

function is_touch_device() {
    return !!('ontouchstart' in window);
}

function is_ie() {
    if (navigator.appVersion.indexOf("MSIE") != -1) {
        return true;
    }
    ;
    return false;
}
;
function is_firefox() {
    if (navigator.userAgent.indexOf("Firefox") != -1) {
        return true;
    }
    ;
    return false;
}
;
function is_opera() {
    if (navigator.userAgent.indexOf("Opera") != -1) {
        return true;
    }
    ;
    return false;
}
;
function is_chrome() {
    return /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);;
}
;
function is_safari() {
    return  /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);;
}
;
function version_ie() {
    return parseFloat(navigator.appVersion.split("MSIE")[1]);
}
;
function version_firefox() {
    if (/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
        var aversion = new Number(RegExp.$1);
        return(aversion);
    }
    ;
}
;
function version_opera() {
    if (/Opera[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
        var aversion = new Number(RegExp.$1);
        return(aversion);
    }
    ;
}
;
function is_ie8() {
    if (is_ie() && version_ie() < 9) {
        return true;
    }
    return false;
}
function is_ie9() {
    if (is_ie() && version_ie() == 9) {
        return true;
    }
    return false;
}

function getInternetExplorerVersion()
{
    var rv = -1;
    if (navigator.appName == 'Microsoft Internet Explorer')
    {
        var ua = navigator.userAgent;
        var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
        if (re.exec(ua) != null)
            rv = parseFloat( RegExp.$1 );
    }
    else if (navigator.appName == 'Netscape')
    {
        var ua = navigator.userAgent;
        var re  = new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})");
        if (re.exec(ua) != null)
            rv = parseFloat( RegExp.$1 );
    }
    return rv;
}

window.requestAnimFrame = (function(){
    return  window.requestAnimationFrame       ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        function( callback ){
            window.setTimeout(callback, 1000 / 60);
        };
})();




jQuery(document).ready(function($){
    dzsscr_init('.scroller-con.auto-init', {init_each: true});
});
jQuery(window).load(function(){
    dzsscr_init('.scroller-con.auto-init-onload', {init_each: true});
});