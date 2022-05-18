/*
 * Author: Digital Zoom Studio
 * Website: http://digitalzoomstudio.net/
 * Portfolio: http://codecanyon.net/user/ZoomIt/portfolio
 * Version: 2.01
 */

(function($) {
    $.fn.prependOnce = function(arg, argfind) {
        var _t = $(this) // It's your element


//        console.info(argfind);
        if(typeof(argfind) =='undefined'){
            var regex = new RegExp('class="(.*?)"');
            var auxarr = regex.exec(arg);


            if(typeof auxarr[1] !='undefined'){
                argfind = '.'+auxarr[1];
            }
        }



        // we compromise chaining for returning the success
        if(_t.children(argfind).length<1){
            _t.prepend(arg);
            return true;
        }else{
            return false;
        }
    };
    $.fn.appendOnce = function(arg, argfind) {
        var _t = $(this) // It's your element


        if(typeof(argfind) =='undefined'){
            var regex = new RegExp('class="(.*?)"');
            var auxarr = regex.exec(arg);


            if(typeof auxarr[1] !='undefined'){
                argfind = '.'+auxarr[1];
            }
        }
//        console.info(_t, _t.children(argfind).length, argfind);
        if(_t.children(argfind).length<1){
            _t.append(arg);
            return true;
        }else{
            return false;
        }
    };
    $.fn.scrollergallery = function(o) {

        var defaults = {
            scrollerSettings : {}
            ,settings_fullwidthHack : 'off'
            ,layout : 'masonry' /// == only masonry / collage / simple available
            ,innerWidth : '0'
            ,type : 'scroller' // scroller or arrows or justmasonry
            ,design_bgpadding: '100'
            ,design_bgrotation: '10'
            ,design_parallaxeffect: 'off'
            ,design_itemwidth: ''
            ,design_itemheight: ''
            ,settings_lightboxlibrary: 'zoombox' //zoombox / prettyPhoto

        };
        var o = $.extend(defaults, o);

        o.design_bgpadding = parseInt(o.design_bgpadding, 10);
        o.design_bgrotation = parseInt(o.design_bgrotation, 10);

        if(isNaN(parseInt(o.design_itemheight,10))==false){
            o.design_itemheight = parseInt(o.design_itemheight,10);
        }
        if(isNaN(parseInt(o.design_itemwidth,10))==false){
            o.design_itemheight = parseInt(o.design_itemheight,10);
        }

        this.each( function() {

            o.innerWidth = parseInt(o.innerWidth, 10);
            //console.log(this);
            var totalWidth=0
                ,totalHeight=0
                ,comWidth=0
                ,comHeight=0
                ,origOffsetX = 0
                ,origWindowW = 0
                ;
            var cthis = $(this)
                ,inner
                ,inners
                ,parorcon
                ,arrows_innerPoints = []
                ,arrows_currPos = 0
                ,arrows_currAPos = 0
                ,_conItems
                ;
            //====variables for determining the availability of slides to perform transition
            var busy=false
                ,busyArray = []
                ,started=false
                ;

            var nrLoaded = 0
                ,nrChildren
                ;

            var arrowPadding = 50
                ;
            var easing = "linear";
            var i=0;

            var hasBg = false;

            var cssFromLeft = {
                'left' : '-100%'
                ,'top' : 0
            };
            var cssFromRight = {
                'left' : '100%'
                ,'top' : 0
            };
            var cssFromTop = {
                'left' : '0'
                ,'top' : '-100%'
            };
            var cssFromBottom = {
                'left' : '0'
                ,'top' : '100%'
            };
            var dir = 'fromLeft';

            var mouseX = 0
                ,mouseY = 0
                ,lastMouseX=0
                ,lastMouseY=0
                ,tiltIndexX
                ,tiltIndexY
                ;

            var int_move_parallax = 0;

            //console.info(o);


            init();
            function init(){
                inner = cthis.find('.inner').eq(0);
                if(o.innerWidth!=0){
                    inner.css('width', o.innerWidth);
                }
                nrChildren = inner.children().length;


                if(cthis.children('.clip-bg').length>0){
                    hasBg = true;
                }

                inner.children().each(function(){
                    var _t = $(this);
                    var toload;
                    if(_t.hasClass('sgitem-tobe')){
                        _t.removeClass('sgitem-tobe');
                        var aux = '';
                        var str_w = '';
                        var str_h = '';
                        var imgtobg = false;
                        if(!isNaN(parseInt(o.design_itemwidth,10))){
                            str_w = ' width: '+o.design_itemwidth+'px;';
                        }
                        if(!isNaN(parseInt(o.design_itemheight,10))){
                            str_h = ' height: '+o.design_itemheight+'px;';
                        }
                        //console.log(isNaN('ceva'));

                        //console.log(cthis, str_w, o.design_itemwidth);

                        var auxlab = 'data-itemwidth';
                        if(_t.attr(auxlab) && _t.attr(auxlab)!=''){
                            if(_t.attr(auxlab).indexOf('%')>-1){
                                str_w = ' width: '+_t.attr(auxlab)+';';
                            }else{
                                str_w = ' width: '+_t.attr(auxlab)+'px;';
                            }
                        }

                        var auxlab = 'data-itemheight';
                        if(_t.attr(auxlab) && _t.attr(auxlab)!=''){
                            if(_t.attr(auxlab).indexOf('%')>-1){
                                str_h = ' height: '+_t.attr(auxlab)+';';
                            }else{
                                str_h = ' height: '+_t.attr(auxlab)+'px;';
                            }
                        }

                        //console.log(str_w);
                        if(str_w!=''){
                            imgtobg = true;
                        }


                        //console.info(o.type, str_w,str_h);
                        if(o.type=="justmasonry"){

                            if(str_w=='' || str_h==''){

                                imgtobg=false;
                                str_h='';
                                str_w='';
                            }

                        }


                        var str_img = '<img src="'+_t.attr('data-src')+'" style="'+str_w+str_h+'"/>';

                        if(imgtobg){
                            str_img = '<div class="imgtobg" style="'+str_w+str_h+' background-image:url('+_t.attr('data-src')+')"></div>'
                        }
                        if(typeof _t.attr('data-type')=='undefined'){
                            _t.attr('data-type','image');
                        }

                        if(_t.attr('data-type')=='image'){

                            aux = '';
                            if(_t.attr('data-link')!='' && _t.attr('data-link')!=undefined){
                                aux += '<a href="' + _t.attr('data-link')+'">';
                            }

                            aux += str_img;


                            if(_t.attr('data-link')!='' && _t.attr('data-link')!=undefined){
                                aux += '</a>';
                            }
                            _t.prepend(aux);
                            if(_t.attr('data-link_wholecontainer')=='on' && _t.attr('data-link')!='' && _t.attr('data-link')!=undefined){
                                _t.wrapInner('<a href="' + _t.attr('data-link')+'"></a>');
                            }


                        }
                        if(_t.attr('data-type')=='imageandlightbox'){
                            //console.log(o.settings_lightboxlibrary)

                            if(_t.find('.desc').length==0){
                                if(o.settings_lightboxlibrary=='prettyPhoto'){
                                    aux = '<a href="' + _t.attr('data-link')+'" rel="prettyPhoto';
                                    if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                        aux+='[' + _t.attr('data-lightboxgallery')  + ']"';
                                    }
                                }
                                if(o.settings_lightboxlibrary=='zoombox'){
                                    aux = '<a href="' + _t.attr('data-link')+'" class="zoombox"';
                                    if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                        aux+=' data-biggallery="' + _t.attr('data-lightboxgallery')  + '"';
                                    }
                                }

                                aux+='>';
                            }


                            aux += str_img;

                            if(_t.find('.desc').length==0){
                                aux += '</a>';
                            }
                            _t.prepend(aux);
                            if(_t.attr('data-link_wholecontainer')=='on' && _t.attr('data-link')!='' && _t.attr('data-link')!=undefined){
                                aux = '';
                                if(o.settings_lightboxlibrary=='prettyPhoto'){
                                    aux = '<a href="' + _t.attr('data-link')+'" rel="prettyPhoto';
                                    if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                        aux+='[' + _t.attr('data-lightboxgallery')  + ']"';
                                    }
                                }
                                if(o.settings_lightboxlibrary=='zoombox'){
                                    aux = '<a href="' + _t.attr('data-link')+'" class="zoombox"';
                                    if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                        aux+=' data-biggallery="' + _t.attr('data-lightboxgallery')  + '"';
                                    }
                                }
                                aux+='></a>';
                                _t.wrapInner(aux);
                            }
                        }
                    }
                    _t.addClass('sgitem');


                    if(_t.get(0).nodeName=="IMG"){
                        toload = _t.get(0);
                    }else{
                        toload = _t.find('img').eq(0).get(0);
                    }
                    if(toload==undefined){
                        imageLoaded();
                    }else{
                        if(toload.complete==true && toload.naturalWidth != 0){
                            imageLoaded();
                        }else{
                            jQuery(toload).bind('load', imageLoaded);
                        }
                    }


                })
                setTimeout(handleReady, 5000); //failsafe in case the image loading
            }
            function imageLoaded(e){
                nrLoaded++;
                if(nrLoaded >= nrChildren){
                    handleReady();
                }
            }
            //function which starts the script
            function handleReady(){
                if(started==true){
                    return;
                }
                started=true;
                if(o.layout=='masonry'){
                    inner.masonry({ columnWidth: 1 });
                }
                if(o.layout=='collage'){
                    inner.collagePlus({ 'targetHeight' : 100 });
                }
                comWidth = inner.width();

                cthis.bind('mousemove', handle_mousemove);

                if(o.type=="scroller"){
                    init_scroller();
                }
                if(o.type=="arrows"){
                    init_arrows();
                }
                if(o.type=="justmasonry"){
                    init_justmasonry();
                }


                if(o.settings_lightboxlibrary=='zoombox'){
                    $('.zoombox').zoomBox();
                }


                if(o.settings_lightboxlibrary=='prettyPhoto' && jQuery.fn.prettyPhoto){
                    cthis.find("a[rel^='prettyPhoto']").prettyPhoto();
                }
            }
            function handle_mousemove(e){
                mouseX = e.pageX - cthis.offset().left;
                mouseY = e.pageY - cthis.offset().top;
                // console.info(mouseX,mouseY);

                if(o.design_parallaxeffect=='on'){
                    tiltIndexX = 0;
                    tiltIndexY = 0;
                    if(hasBg){
                        tiltIndexX = mouseX / totalWidth - 0.5;
                        tiltIndexY = mouseY / totalHeight - 0.5;

                    }


                    clearTimeout(int_move_parallax);
                    int_move_parallax = setTimeout(move_parallax, 10);
                }


                //console.info(((tiltIndexX * 6)-3), tiltIndexY, ((tiltIndexY * 6)-3));
            }
            function move_parallax(){

                cthis.find('.the-bg').eq(0).css({
                    //'transform' : 'rotateX('+(tiltIndexX * o.design_bgrotation)+'deg) rotateY('+(tiltIndexY * o.design_bgrotation)+'deg)',
                    //'left' : ((tiltIndexX * 6)-3) + '%'
                    //,'top' : ((tiltIndexY * 6)-3) + '%'
                    'transform' : 'translate3d('+((tiltIndexX * 6)-3)+'%,'+((tiltIndexY * 6)-3) + '%,0)'
                })


                var auxs = 12;
                _conItems.css({
                    //'transform' : 'rotateX('+(tiltIndexX * o.design_bgrotation)+'deg) rotateY('+(tiltIndexY * o.design_bgrotation)+'deg)',
                    //'left' : ((tiltIndexX * 6)-3) + '%'
                    //,'top' : ((tiltIndexY * 6)-3) + '%'
                    'transform' : 'translate3d('+((tiltIndexX * auxs)-(auxs/2))+'px,'+((tiltIndexY * auxs)-(auxs/2)) + 'px,0)'
                })
            }
            function init_scroller(){
                inner = cthis.find('.inner').eq(0);

                cthis.scroller(o.scrollerSettings);
                _conItems = cthis.find('.scroller').eq(0);
                _conItems.addClass('con-items');
                stylizeGallery();
            }
            function init_justmasonry(){

                cthis.addClass('type-'+ o.type);
                stylizeGallery();
            }
            function init_arrows(){
                cthis.addClass('type-arrows');
                inner = cthis.find('.inner').eq(0);
                inner.wrap('<div class="con-items clip-inners"><div class="inners"></div></div>');
                inners = cthis.find('.inners').eq(0);
                _conItems = cthis.find('.con-items').eq(0);


                var auxa = [];
                var aux = 0;
                inner.children().each(function(){
                    var _t = $(this);
                    //console.log(_t.css('top'));
                    if(parseInt(_t.css('top'), 10)==0){
                        auxa.push(parseInt(_t.css('left'), 10));
                    }
                })
                for(i=auxa.length-1;i>0;i--){
                    aux = -auxa[i];
                    arrows_innerPoints.push(aux);
                }
                arrows_innerPoints.push(0)
                var i2=auxa.length-1;
                for(i=1;i<auxa.length;i++){
                    aux = comWidth - auxa[i2];
                    arrows_innerPoints.push(aux)
                    i2--;
                }
                arrows_currAPos = parseInt(arrows_innerPoints.length/2,10);

                inners.append(inner.clone());
                inners.append(inner.clone());
                inners.children().eq(0).find('div.sgitem[data-type=imageandprettyphoto]').each(function(){
                    var _t = jQuery(this);
                    if(_t.attr('data-prettyPhotoGallery')!=undefined && _t.attr('data-prettyPhotoGallery')!=''){
                        _t.children('a').attr('rel', (_t.children('a').attr('rel') + '1'));
                    }
                });
                inners.children().eq(1).find('div.sgitem[data-type=imageandprettyphoto]').each(function(){
                    var _t = jQuery(this);
                    if(_t.attr('data-prettyPhotoGallery')!=undefined && _t.attr('data-prettyPhotoGallery')!=''){
                        _t.children('a').attr('rel', (_t.children('a').attr('rel') + '2'));
                    }
                });
                inners.children().eq(2).find('div.sgitem[data-type=imageandprettyphoto]').each(function(){
                    var _t = jQuery(this);
                    if(_t.attr('data-prettyPhotoGallery')!=undefined && _t.attr('data-prettyPhotoGallery')!=''){
                        _t.children('a').attr('rel', (_t.children('a').attr('rel') + '3'));
                    }
                });
                if(o.layout=='masonry'){
                    inners.children().addClass('masonry');
                }
                if(o.layout=='collage'){
                    inners.children().addClass('layout-collage');
                }
                inners.children().eq(0).css('left', -comWidth);
                inners.children().eq(1).css('left', 0);
                inners.children().eq(2).css('left', comWidth);

                cthis.append('<div class="arrowleft-con"><div class="arrowleft"></div></div>');
                cthis.append('<div class="arrowright-con"><div class="arrowright"></div></div>');


                //the default padding for the arrows
                arrows_currPos = arrowPadding;
                inners.css('left', arrows_currPos);

                //if its fullwidth we add the listener and trigger an initial load

                if(o.settings_fullwidthHack=='on'){
                    origOffsetX = cthis.offset().left;
                    origWindowW = jQuery(window).width();
                    //cthis.css('left', -cthis.offset().left);
                }

                cthis.find('.arrowright-con').bind('click', handleArrowRightClick);
                cthis.find('.arrowleft-con').bind('click', handleArrowLeftClick);
                stylizeGallery();
            }
            function handleArrowLeftClick(){
                //console.log(arg);
                var tempNr = arrows_currAPos;
                tempNr++;
                if(tempNr>=arrows_innerPoints.length){
                    arrows_reblock();
                }else{
                    arrows_gotoPosition(tempNr);
                }
            }
            function handleArrowRightClick(){
                //console.log(arg);



                var tempNr = arrows_currAPos;
                tempNr--;
                if(tempNr<0){
                    arrows_reblock();
                }else{
                    arrows_gotoPosition(tempNr);
                }
            }
            function arrows_reblock(){
                if(busy==true){
                    return;
                }
                //console.log(inners);
                if(arrows_currAPos==0){
                    arrows_currPos+=comWidth;
                    inners.css('left', arrows_currPos);
                }
                //console.log(arrows_currAPos, arrows_innerPoints.length);
                if(arrows_currAPos>=arrows_innerPoints.length-1){

                    arrows_currPos-= comWidth;
                    inners.css('left', arrows_currPos);


                    //console.log(arrows_currPos)
                }
                arrows_gotoPosition(parseInt(arrows_innerPoints.length/2,10));
            }

            function calculateDims(){

                if(o.design_parallaxeffect=='on'){

                    if(o.type=="arrows"){

                        _conItems.css({
                            'left': o.design_bgpadding,
                            'width': totalWidth - (o.design_bgpadding*2),
                            'height': totalHeight - (o.design_bgpadding*2),
                            'overflow': 'hidden'
                        })

                        if(hasBg){
                            inners.css({
                                'left' : 0
                            })
                            arrowPadding = 0;
                        }
                    }
                }
            }
            function arrows_gotoPosition(arg){
                if(busy==true){
                    return;
                }
                busy=true;
                arrows_currAPos = arg;
                inners.animate({
                    'left' : arrows_innerPoints[arg] + arrowPadding
                }, {queue:false, complete:unbusy})
                arrows_currPos = arrows_innerPoints[arg] + arrowPadding;
                arrows_currAPos = arg;
            }
            function unbusy(){
                busy = false;

            }
            function mouseover_item(e){

                var _t = $(this);
                var ind = (_t.parent().children().index(_t));
                /*if you want direction scrolling uncomment this*/
                //if(e.pageX > $(this).offset().left + $(this).width()/2)
                //dir="right";

                if(ind==0){
                    //console.info(e, _t);
                }
                //console.log(busyArray[ind]);
                if(busyArray[ind]==true){
                    return;
                }

                var localx = e.pageX - _t.offset().left;
                var localy = e.pageY - _t.offset().top;

                var dir = closestEdge(localx, localy, _t.width(), _t.height());
                //console.info(_t, edge);

                //console.log(e.pageX, (_t.offset().left + _t.outerWidth(false)));

                if(dir=="left"){
                    $(this).find('.desc').css(cssFromLeft);
                }
                if(dir=="right"){
                    $(this).find('.desc').css(cssFromRight);

                }
                if(dir=="top"){
                    $(this).find('.desc').css(cssFromTop);

                }
                if(dir=="bottom"){
                    $(this).find('.desc').css(cssFromBottom);

                }


                //console.info($(this));

                $(this).find('.desc').eq(0).stop().animate({
                    'left' : 0,
                    'top' : 0
                }, {duration:300, queue:true, complete:animComplete, easing:easing});
                busyArray[ind]=true;
            }
            function mouseout_item(e){
                var _t = $(this);

                var ind = (_t.parent().children().index(_t));

                //if(e.pageX > $(this).offset().left + $(this).width()/2)
                //dir="right";

                var localx = e.pageX - _t.offset().left;
                var localy = e.pageY - _t.offset().top;

                var dir = closestEdge(localx, localy, _t.width(), _t.height());
                //console.info(_t, edge);

                var cssToAnimate = cssFromLeft;
                if(dir=="left"){
                    cssToAnimate = cssFromLeft;
                }
                if(dir=="right"){
                    cssToAnimate = cssFromRight;

                }
                if(dir=="top"){
                    cssToAnimate = cssFromTop;

                }
                if(dir=="bottom"){
                    cssToAnimate = cssFromBottom;

                }
                $(this).find('.desc').eq(0).animate(cssToAnimate, {duration:300, queue:true, complete:animOutComplete, easing:easing});
                busyArray[ind]=true;
            }
            function animComplete(){
                var ind = 0;
                var _con = null;
                var _conInner = null;

                if($(this).parent().hasClass('sgitem')){
                    _con = $(this).parent();
                }else{
                    _con = $(this).parent().parent();
                }

                if($(this).parent().parent().hasClass('inner')){
                    _conInner = $(this).parent().parent();
                }else{
                    _conInner = $(this).parent().parent().parent();
                }


                ind  = (_conInner.children().index(_con));


                busyArray[ind]=false;
            }
            function animOutComplete(){
                var _t = $(this);
                var ind = 0;
                var _con = null;
                var _conInner = null;

                if($(this).parent().hasClass('sgitem')){
                    _con = $(this).parent();
                }else{
                    _con = $(this).parent().parent();
                }

                if($(this).parent().parent().hasClass('inner')){
                    _conInner = $(this).parent().parent();
                }else{
                    _conInner = $(this).parent().parent().parent();
                }
                ind  = (_conInner.children().index(_con));

                //console.log(_t);
                //console.log('ceva');
                busyArray[ind]=false;
                // _t.stop();
            }
            function distMetric(x,y,x2,y2) {
                var xDiff = x - x2;
                var yDiff = y - y2;
                return (xDiff * xDiff) + (yDiff * yDiff);
            }
            function closestEdge(x,y,w,h) {
                var topEdgeDist = distMetric(x,y,w/2,0);
                var bottomEdgeDist = distMetric(x,y,w/2,h);
                var leftEdgeDist = distMetric(x,y,0,h/2);
                var rightEdgeDist = distMetric(x,y,w,h/2);
                var min = Math.min(topEdgeDist,bottomEdgeDist,leftEdgeDist,rightEdgeDist);
                switch (min) {
                    case leftEdgeDist:
                        return "left";
                    case rightEdgeDist:
                        return "right";
                    case topEdgeDist:
                        return "top";
                    case bottomEdgeDist:
                        return "bottom";
                }
            }
            function stylizeGallery(){

                if(cthis.parent().hasClass('scroller-gallery-con')){
                    parorcon = cthis.parent();
                    parorcon.children('.preloader').fadeOut("slow");
                }


                totalWidth = cthis.width();
                totalHeight = cthis.height();

                if(cthis.css('opacity') == 0){
                    cthis.animate({
                        'opacity' : 1
                    }, 600)
                }

                if(hasBg){
                    _conItems.css({
                        'top': o.design_bgpadding
                    })
                }



                if(cthis.find('.real-inner').length==1){
                    inner = cthis.find('.real-inner');
                }
                //we add classes for the icons to show
                for(i=0;i<nrChildren;i++){
                    busyArray[i]=false;
                }
                cthis.find('.inner').children().each(function(){

                    var auxtype="page";
                    var _t = $(this);
                    if(_t.hasClass('a-image')){
                        auxtype='image';
                    }
                    if(_t.hasClass('a-video')){
                        auxtype='video';
                    }
                    _t.find('.desc').children('div').append('<div class="icon '+auxtype+'"></div>');


                    //console.info(_t);


                    var auxwrap = '';
                    if(_t.attr('data-type')=='image' && _t.attr('data-link')!=undefined && _t.attr('data-link')!=''){
                        auxwrap += '<a href="' + _t.attr('data-link')+'">';
                        auxwrap += '</a>';
                    }
                    if(_t.attr('data-type')=='imageandlightbox'){
                        if(o.settings_lightboxlibrary=='prettyPhoto'){
                            auxwrap = '<a href="' + _t.attr('data-link')+'" rel="prettyPhoto';
                            if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                auxwrap+='[' + _t.attr('data-lightboxgallery')  + ']"';
                            }
                        }
                        if(o.settings_lightboxlibrary=='zoombox'){
                            auxwrap = '<a href="' + _t.attr('data-link')+'" class="zoombox"';
                            if(_t.attr('data-lightboxgallery')!=undefined && _t.attr('data-lightboxgallery')!=''){
                                auxwrap+=' data-biggallery="' + _t.attr('data-lightboxgallery')  + '" data-biggallerythumbnail="' + _t.attr('data-src')  + '"';
                            }
                        }
                        auxwrap+='>';
                        auxwrap += '</a>';
                    }

                    if(auxwrap!=''){
                        _t.find('.fake-link').wrap(auxwrap);
                    }


                })

                cthis.find('.inner').delegate('.sgitem','mouseenter', mouseover_item);
                cthis.find('.inner').delegate('.sgitem','mouseleave', mouseout_item);

                $(window).bind('resize', handleResize);
                handleResize();

                calculateDims();
            }
            function handleResize(){
                totalWidth = cthis.width();
                totalHeight = cthis.height();

                if(o.settings_fullwidthHack=='on'){
                    aux = 0;
                    aux = origOffsetX + ( jQuery(window).width() - origWindowW)/2;
                    if(aux<0){
                        aux = 0
                    }
                    cthis.css('left', -aux);
                }


                calculateDims();

            }
            return this;
        });
    };
    window.dzssg_init = function(selector, settings) {
        $(selector).scrollergallery(settings);
    };

})(jQuery);