/**
 * HSHeaderSide Component.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires HSScrollBar component (hs.scrollbar.js v1.0.0), jQuery(v2.0.0)
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSHeaderSide = {

    /**
     * Base configuration.
     *
     * @private
     */
    _baseConfig: {
      headerBreakpoint: null,
      breakpointsMap: {
        'md': 768,
        'sm': 576,
        'lg': 992,
        'xl': 1200
      },
      afterOpen: function(){},
      afterClose: function(){}
    },

    /**
     * Contains collection of all initialized items on the page.
     *
     * @private
     */
    _pageCollection: $(),

    /**
     * Initializtion of the component.
     *
     * @param {jQuery} collection
     * @param {Object} config
     *
     * @public
     * @returns {jQuery}
     */
    init: function(collection, config) {

      var _self = this;

      if(!collection || !collection.length) return $();

      this.$w = $(window);

      config = config && $.isPlainObject(config) ? config : {};

      this._bindGlobalEvents();

      return collection.each(function(i, el){

        var $this = $(el),
            itemConfig = $.extend(true, {}, _self._baseConfig, config, $this.data());

        if( $this.data('HSHeaderSide') ) return;

        $this.data('HSHeaderSide', _self._factoryMethod( $this, itemConfig ) );

        _self._pageCollection = _self._pageCollection.add($this);

      });

    },

    /**
     * Binds necessary global events.
     *
     * @private
     */
    _bindGlobalEvents: function() {

      var _self = this;

      this.$w.on('resize.HSHeaderSide', function(e){

        if(_self.resizeTimeoutId) clearTimeout(_self.resizeTimeoutId);

        _self.resizeTimeoutId = setTimeout(function(){

          _self._pageCollection.each(function(i, el){

            var HSHeaderSide = $(el).data('HSHeaderSide');

            if(!HSHeaderSide.config.headerBreakpoint) return;

            if(_self.$w.width() < HSHeaderSide.config.breakpointsMap[HSHeaderSide.config.headerBreakpoint] && HSHeaderSide.isInit()) {
              HSHeaderSide.destroy();
            }
            else if(_self.$w.width() >= HSHeaderSide.config.breakpointsMap[HSHeaderSide.config.headerBreakpoint] && !HSHeaderSide.isInit()) {
              HSHeaderSide.init();
            }

          });

        }, 10);

      });

      // $(document).on('keyup.HSHeaderSide', function(e){

      //   if(e.keyCode && e.keyCode === 27) {

      //     _self._pageCollection.each(function(i,el){

      //       var HSHeaderSide = $(el).data('HSHeaderSide'),
      //           hamburgers = HSHeaderSide.invoker;

      //       if(!HSHeaderSide) return;
      //       if(hamburgers.length && hamburgers.find('.is-active').length) hamburgers.find('.is-active').removeClass('is-active');
      //       HSHeaderSide.hide();

      //     });

      //   }

      // });

    },

    /**
     * Returns an object which would be describe the Header behavior.
     *
     * @private
     * @returns {HSHeaderSide*}
     */
    _factoryMethod: function(element, config) {

      // static
      if( !config.headerBehavior ) {
        return new (config['headerPosition'] == "left" ? HSHeaderSideStaticLeft : HSHeaderSideStaticRight)(element, config);
      }

      // overlay
      if( config.headerBehavior && config.headerBehavior == 'overlay' ) {
        return new (config['headerPosition'] == "left" ? HSHeaderSideOverlayLeft : HSHeaderSideOverlayRight)(element, config);
      }

      // push
      if( config.headerBehavior && config.headerBehavior == 'push' ) {
        return new (config['headerPosition'] == "left" ? HSHeaderSidePushLeft : HSHeaderSidePushRight)(element, config);
      }

    }

  }

  /**
   * Provides an abstract interface for the side header.
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   */
  function _HSHeaderSideAbstract(element, config) {

    /**
     * Contains link to the current element.
     *
     * @public
     */
    this.element = element;

    /**
     * Contains configuration object.
     *
     * @public
     */
    this.config = config;


    /**
     * Contains link to the window object.
     *
     * @public
     */
    this.$w = $(window);

    /**
     * Contains name of methods which should be implemented in derived class.
     * Each of these methods except 'isInit' must return link to the current object.
     *
     * @private
     */
    this._abstractMethods = ['init', 'destroy', 'show', 'hide', 'isInit'];


    /**
     * Runs initialization of the object.
     *
     * @private
     */
    this._build = function() {

      if( !this.config.headerBreakpoint ) return this.init();

      if( this.config.breakpointsMap[ this.config.headerBreakpoint ] <= this.$w.width() ) {
        return this.init();
      }
      else {
        return this.destroy();
      }
    };


    /**
     * Checks whether derived class implements necessary abstract events.
     *
     * @private
     */
    this._isCorrectDerrivedClass = function() {

      var _self = this;

      this._abstractMethods.forEach(function(method){

        if(!(method in _self) || !$.isFunction(_self[method])) {

          throw new Error("HSHeaderSide: Derived class must implement " + method + " method.");

        }

      });

      this._build();

    };

    setTimeout(this._isCorrectDerrivedClass.bind(this), 10);

  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSideStaticLeft( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    this.body = $('body');

  };


  /**
   * Initialization of the HSHeaderSideStaticLeft instance.
   *
   * @public
   * @returns {HSHeaderSideStaticLeft}
   */
  HSHeaderSideStaticLeft.prototype.init = function() {

    this.body.addClass('u-body--header-side-static-left');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    return this;

  };

  /**
   * Destroys the HSHeaderSideStaticLeft instance.
   *
   * @public
   * @returns {HSHeaderSideStaticLeft}
   */
  HSHeaderSideStaticLeft.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-static-left');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSideStaticLeft.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-static-left');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSideStaticLeft}
   */
  HSHeaderSideStaticLeft.prototype.show = function() {
    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSideStaticLeft}
   */
  HSHeaderSideStaticLeft.prototype.hide = function() {
    return this;
  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSideStaticRight( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    this.body = $('body');

  };


  /**
   * Initialization of the HSHeaderSideStaticRight instance.
   *
   * @public
   * @returns {HSHeaderSideStaticRight}
   */
  HSHeaderSideStaticRight.prototype.init = function() {

    this.body.addClass('u-body--header-side-static-right');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    return this;

  };

  /**
   * Destroys the HSHeaderSideStaticRight instance.
   *
   * @public
   * @returns {HSHeaderSideStaticRight}
   */
  HSHeaderSideStaticRight.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-static-right');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSideStaticRight.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-static-right');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSideStaticRight}
   */
  HSHeaderSideStaticRight.prototype.show = function() {
    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSideStaticRight}
   */
  HSHeaderSideStaticRight.prototype.hide = function() {
    return this;
  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSideOverlayLeft( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    Object.defineProperty(this, 'isShown', {
      get: function() {
        return this.body.hasClass('u-body--header-side-opened');
      }
    });

    Object.defineProperty(this, 'overlayClasses', {
      get: function() {
        return this.element.data('header-overlay-classes') ? this.element.data('header-overlay-classes') : '';
      }
    });

    Object.defineProperty(this, 'headerClasses', {
      get: function() {
        return this.element.data('header-classes') ? this.element.data('header-classes') : '';
      }
    });

    this.body = $('body');
    this.invoker = $('[data-target="#'+this.element.attr('id')+'"]');

  };


  /**
   * Initialization of the HSHeaderSideOverlayLeft instance.
   *
   * @public
   * @returns {HSHeaderSideOverlayLeft}
   */
  HSHeaderSideOverlayLeft.prototype.init = function() {

    var _self = this;

    this.body.addClass('u-body--header-side-overlay-left');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    if(this.invoker.length) {
      this.invoker.on('click.HSHeaderSide', function(e){

        if(_self.isShown) {
          _self.hide();
        }
        else {
          _self.show();
        }

        e.preventDefault();
      }).css('display', 'block');
    }

    if(!this.overlay) {

      this.overlay = $('<div></div>', {
        class: 'u-header__overlay ' + _self.overlayClasses
      });

    }

    this.overlay.on('click.HSHeaderSide', function(e){
      var hamburgers = _self.invoker.length ? _self.invoker.find('.is-active') : $();
      if(hamburgers.length) hamburgers.removeClass('is-active');
      _self.hide();
    });

    this.element.addClass(this.headerClasses).append(this.overlay);

    return this;

  };

  /**
   * Destroys the HSHeaderSideOverlayLeft instance.
   *
   * @public
   * @returns {HSHeaderSideOverlayLeft}
   */
  HSHeaderSideOverlayLeft.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-overlay-left');
    this.hide();

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    this.element.removeClass(this.headerClasses);
    if(this.invoker.length) {
      this.invoker.off('click.HSHeaderSide').css('display', 'none');
    }
    if(this.overlay) {
      this.overlay.off('click.HSHeaderSide');
      this.overlay.remove();
      this.overlay = null;
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSideOverlayLeft.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-overlay-left');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSideOverlayLeft}
   */
  HSHeaderSideOverlayLeft.prototype.show = function() {

    this.body.addClass('u-body--header-side-opened');

    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSideOverlayLeft}
   */
  HSHeaderSideOverlayLeft.prototype.hide = function() {

    // var hamburgers = this.invoker.length ? this.invoker.find('.is-active') : $();
    // if(hamburgers.length) hamburgers.removeClass('is-active');

    this.body.removeClass('u-body--header-side-opened');

    return this;
  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSidePushLeft( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    Object.defineProperty(this, 'isShown', {
      get: function() {
        return this.body.hasClass('u-body--header-side-opened');
      }
    });

    Object.defineProperty(this, 'overlayClasses', {
      get: function() {
        return this.element.data('header-overlay-classes') ? this.element.data('header-overlay-classes') : '';
      }
    });

    Object.defineProperty(this, 'headerClasses', {
      get: function() {
        return this.element.data('header-classes') ? this.element.data('header-classes') : '';
      }
    });

    Object.defineProperty(this, 'bodyClasses', {
      get: function() {
        return this.element.data('header-body-classes') ? this.element.data('header-body-classes') : '';
      }
    });

    this.body = $('body');
    this.invoker = $('[data-target="#'+this.element.attr('id')+'"]');

  };


  /**
   * Initialization of the HSHeaderSidePushLeft instance.
   *
   * @public
   * @returns {HSHeaderSidePushLeft}
   */
  HSHeaderSidePushLeft.prototype.init = function() {

    var _self = this;

    this.body.addClass('u-body--header-side-push-left');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    if(this.invoker.length) {
      this.invoker.on('click.HSHeaderSide', function(e){

        if(_self.isShown) {
          _self.hide();
        }
        else {
          _self.show();
        }

        e.preventDefault();
      }).css('display', 'block');
    }

    if(!this.overlay) {

      this.overlay = $('<div></div>', {
        class: 'u-header__overlay ' + _self.overlayClasses
      });

    }

    this.overlay.on('click.HSHeaderSide', function(e){
      var hamburgers = _self.invoker.length ? _self.invoker.find('.is-active') : $();
      if(hamburgers.length) hamburgers.removeClass('is-active');
      _self.hide();
    });

    this.element.addClass(this.headerClasses).append(this.overlay);
    this.body.addClass(this.bodyClasses);

    return this;

  };

  /**
   * Destroys the HSHeaderSidePushLeft instance.
   *
   * @public
   * @returns {HSHeaderSidePushLeft}
   */
  HSHeaderSidePushLeft.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-push-left');
    this.hide();

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    this.element.removeClass(this.headerClasses);
    this.body.removeClass(this.bodyClasses);
    if(this.invoker.length){
      this.invoker.off('click.HSHeaderSide').css('display', 'none');
    }
    if(this.overlay) {
      this.overlay.off('click.HSHeaderSide');
      this.overlay.remove();
      this.overlay = null;
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSidePushLeft.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-push-left');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSidePushLeft}
   */
  HSHeaderSidePushLeft.prototype.show = function() {

    this.body.addClass('u-body--header-side-opened');

    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSidePushLeft}
   */
  HSHeaderSidePushLeft.prototype.hide = function() {

    this.body.removeClass('u-body--header-side-opened');

    return this;
  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSideOverlayRight( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    Object.defineProperty(this, 'isShown', {
      get: function() {
        return this.body.hasClass('u-body--header-side-opened');
      }
    });

    Object.defineProperty(this, 'overlayClasses', {
      get: function() {
        return this.element.data('header-overlay-classes') ? this.element.data('header-overlay-classes') : '';
      }
    });

    Object.defineProperty(this, 'headerClasses', {
      get: function() {
        return this.element.data('header-classes') ? this.element.data('header-classes') : '';
      }
    });

    this.body = $('body');
    this.invoker = $('[data-target="#'+this.element.attr('id')+'"]');

  };


  /**
   * Initialization of the HSHeaderSideOverlayRight instance.
   *
   * @public
   * @returns {HSHeaderSideOverlayRight}
   */
  HSHeaderSideOverlayRight.prototype.init = function() {

    var _self = this;

    this.body.addClass('u-body--header-side-overlay-right');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    if(this.invoker.length) {
      this.invoker.on('click.HSHeaderSide', function(e){

        if(_self.isShown) {
          _self.hide();
        }
        else {
          _self.show();
        }

        e.preventDefault();
      }).css('display', 'block');
    }

    if(!this.overlay) {

      this.overlay = $('<div></div>', {
        class: 'u-header__overlay ' + _self.overlayClasses
      });

    }

    this.overlay.on('click.HSHeaderSide', function(e){
      var hamburgers = _self.invoker.length ? _self.invoker.find('.is-active') : $();
      if(hamburgers.length) hamburgers.removeClass('is-active');
      _self.hide();
    });

    this.element.addClass(this.headerClasses).append(this.overlay);

    return this;

  };

  /**
   * Destroys the HSHeaderSideOverlayRight instance.
   *
   * @public
   * @returns {HSHeaderSideOverlayRight}
   */
  HSHeaderSideOverlayRight.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-overlay-right');
    this.hide();

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    this.element.removeClass(this.headerClasses);
    if(this.invoker.length) {
      this.invoker.off('click.HSHeaderSide').css('display', 'none');
    }
    if(this.overlay) {
      this.overlay.off('click.HSHeaderSide');
      this.overlay.remove();
      this.overlay = null;
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSideOverlayRight.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-overlay-right');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSideOverlayRight}
   */
  HSHeaderSideOverlayRight.prototype.show = function() {

    this.body.addClass('u-body--header-side-opened');

    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSideOverlayRight}
   */
  HSHeaderSideOverlayRight.prototype.hide = function() {

    // var hamburgers = this.invoker.length ? this.invoker.find('.is-active') : $();
    // if(hamburgers.length) hamburgers.removeClass('is-active');

    this.body.removeClass('u-body--header-side-opened');

    return this;
  };

  /**
   * HSHeaderSide constructor function.
   *
   * @extends _HSHeaderSideAbstract
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSHeaderSidePushRight( element, config ) {

    _HSHeaderSideAbstract.call(this, element, config);

    Object.defineProperty(this, 'scrollContainer', {
      get: function() {
        return this.element.find('.u-header__sections-container');
      }
    });

    Object.defineProperty(this, 'isShown', {
      get: function() {
        return this.body.hasClass('u-body--header-side-opened');
      }
    });

    Object.defineProperty(this, 'overlayClasses', {
      get: function() {
        return this.element.data('header-overlay-classes') ? this.element.data('header-overlay-classes') : '';
      }
    });

    Object.defineProperty(this, 'headerClasses', {
      get: function() {
        return this.element.data('header-classes') ? this.element.data('header-classes') : '';
      }
    });

    Object.defineProperty(this, 'bodyClasses', {
      get: function() {
        return this.element.data('header-body-classes') ? this.element.data('header-body-classes') : '';
      }
    });

    this.body = $('body');
    this.invoker = $('[data-target="#'+this.element.attr('id')+'"]');

  };


  /**
   * Initialization of the HSHeaderSidePushRight instance.
   *
   * @public
   * @returns {HSHeaderSidePushRight}
   */
  HSHeaderSidePushRight.prototype.init = function() {

    var _self = this;

    this.body.addClass('u-body--header-side-push-right');

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.init( this.scrollContainer );
    }

    if(this.invoker.length) {
      this.invoker.on('click.HSHeaderSide', function(e){

        if(_self.isShown) {
          _self.hide();
        }
        else {
          _self.show();
        }

        e.preventDefault();
      }).css('display', 'block');
    }

    if(!this.overlay) {

      this.overlay = $('<div></div>', {
        class: 'u-header__overlay ' + _self.overlayClasses
      });

    }

    this.overlay.on('click.HSHeaderSide', function(e){
      var hamburgers = _self.invoker.length ? _self.invoker.find('.is-active') : $();
      if(hamburgers.length) hamburgers.removeClass('is-active');
      _self.hide();
    });

    this.element.addClass(this.headerClasses).append(this.overlay);
    this.body.addClass(this.bodyClasses);

    return this;

  };

  /**
   * Destroys the HSHeaderSidePushRight instance.
   *
   * @public
   * @returns {HSHeaderSidePushRight}
   */
  HSHeaderSidePushRight.prototype.destroy = function() {

    this.body.removeClass('u-body--header-side-push-right');
    this.hide();

    if( $.HSCore.components.HSScrollBar && this.scrollContainer.length ) {
      $.HSCore.components.HSScrollBar.destroy( this.scrollContainer );
    }

    this.element.removeClass(this.headerClasses);
    this.body.removeClass(this.bodyClasses);
    if(this.invoker.length){
      this.invoker.off('click.HSHeaderSide').css('display', 'none');
    }
    if(this.overlay) {
      this.overlay.off('click.HSHeaderSide');
      this.overlay.remove();
      this.overlay = null;
    }

    return this;

  };

  /**
   * Checks whether instance has been initialized.
   *
   * @public
   * @returns {Boolean}
   */
  HSHeaderSidePushRight.prototype.isInit = function() {

    return this.body.hasClass('u-body--header-side-push-right');

  };

  /**
   * Shows the Header.
   *
   * @public
   * @returns {HSHeaderSidePushRight}
   */
  HSHeaderSidePushRight.prototype.show = function() {

    this.body.addClass('u-body--header-side-opened');

    return this;
  };

  /**
   * Hides the Header.
   *
   * @public
   * @returns {HSHeaderSidePushRight}
   */
  HSHeaderSidePushRight.prototype.hide = function() {

    // var hamburgers = this.invoker.length ? this.invoker.find('.is-active') : $();
    // if(hamburgers.length) hamburgers.removeClass('is-active');

    this.body.removeClass('u-body--header-side-opened');

    return this;
  };

})(jQuery);