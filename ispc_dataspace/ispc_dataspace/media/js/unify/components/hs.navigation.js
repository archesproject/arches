/**
 * Navigation component.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires HSScrollBar component (hs.scrollbar.js v1.0.0)
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSNavigation = {

    /**
     * Base configuration of the component.
     *
     * @private
     */
    _baseConfig: {
      navigationOverlayClasses: '',
      navigationInitClasses: '',
      navigationInitBodyClasses: '',
      navigationPosition: 'right',
      activeClass: 'u-main-nav--overlay-opened',
      navigationBreakpoint: 768,
      breakpointsMap: {
        'sm': 576,
        'md': 768,
        'lg': 992,
        'xl': 1200
      },
      afterOpen: function(){},
      afterClose: function(){}
    },

    /**
     * Collection of all initialized items on the page.
     *
     * @private
     */
    _pageCollection: $(),

    /**
     * Initializtion of the navigation.
     *
     * @param {jQuery} collection
     * @param {Object} config
     *
     * @public
     * @return {jQuery}
     */
    init: function( collection, config ) {

      var _self = this,
          $w = $(window);

      if(!collection || !collection.length) return $();

      config = config && $.isPlainObject(config) ? config : {};

      $w.on('resize.HSNavigation', function(e){

        if(_self.resizeTimeoutId) clearTimeout(_self.resizeTimeoutId);

        _self.resizeTimeoutId = setTimeout(function(){

          _self._pageCollection.each(function(i, el){

            var $this = $(el),
                HSNavigation = $this.data('HSNavigation');

            if($w.width() > HSNavigation.config.breakpointsMap[HSNavigation.config.navigationBreakpoint] && HSNavigation.isInitialized() ) {

              HSNavigation.destroy();

            }
            else if($w.width() <= HSNavigation.config.breakpointsMap[HSNavigation.config.navigationBreakpoint] && !HSNavigation.isInitialized()) {
              HSNavigation.init();
            }

          });

        }, 50);

      });


      collection.each(function(i, el){

        var $this = $(el),
            itemConfig = $.extend(true, {}, _self._baseConfig, config, $this.data());

        if( $this.data('HSNavigation') ) return;

        $this.data('HSNavigation', _self._factoryMethod( $this, itemConfig ));

        _self._pageCollection = _self._pageCollection.add( $this );

      });


      _self._pageCollection.each(function(i, el){

          var $this = $(el),
              HSNavigation = $this.data('HSNavigation');

          if($w.width() > HSNavigation.config.breakpointsMap[HSNavigation.config.navigationBreakpoint] ) {

            HSNavigation.destroy();

          }
          else if($w.width() <= HSNavigation.config.breakpointsMap[HSNavigation.config.navigationBreakpoint] ) {
            HSNavigation.init();
          }
      });

      return collection;

    },

    /**
     * Returns certain object relative to class name.
     *
     * @param {jQuery} element
     * @param {Object} config
     *
     * @private
     * @return {HSNavigationOverlay|HSNavigationPush}
     */
    _factoryMethod: function(element, config) {

      if( element.filter('[class*="u-main-nav--overlay"]').length ) {
        return new HSNavigationOverlay(element, config);
      }
      else if ( element.filter('[class*="u-main-nav--push"]').length ) {
       return new HSNavigationPush(element, config);
      }

    }

  };

  /**
   * Abstract class for all HSNavigation* objects.
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @return {Boolean}
   */
  function HSNavigationAbstract(element, config) {

    /**
     * Contains current jQuery object.
     *
     * @public
     */
    this.element = element;

    /**
     * Contains body jQuery object.
     *
     * @public
     */
    this.body = $('body');

    /**
     * Contains configuration.
     *
     * @public
     */
    this.config = config;

    /**
     * Reinitialization of the HSNavigation* object.
     *
     * @public
     */
    this.reinit = function() {

      this.destroy().init();

    }
  };

  /**
   * HSNavigationOverlay.
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSNavigationOverlay(element, config) {

    var _self = this;

    // extends some functionality from abstract class
    HSNavigationAbstract.call(this, element, config);

    Object.defineProperties(this, {

      overlayClasses: {
        get: function() {
          return 'u-main-nav__overlay ' + _self.config.navigationOverlayClasses
        }
      },

      bodyClasses: {
        get: function() {
          return 'u-main-nav--overlay-' + _self.config.navigationPosition
        }
      },

      isOpened: {
        get: function() {
          return _self.body.hasClass( _self.config.activeClass );
        }
      }

    });

  };


  /**
   * Initialization of the instance.
   *
   * @public
   */
  HSNavigationOverlay.prototype.init = function() {

    var _self = this;

    /**
     * Contains overlay object.
     *
     * @public
     */
    this.overlay = $('<div></div>', {
      class: _self.overlayClasses
    });

    if( $.HSCore.components.HSScrollBar ) {

      setTimeout(function(){
        $.HSCore.components.HSScrollBar.init( _self.element.find( '.u-main-nav__list-wrapper' ) );
      }, 10);

    }

    this.toggler = $('[data-target="#'+ this.element.attr('id') +'"]');

    if(this.toggler && this.toggler.length) this.toggler.css('display', 'block');

    this.body.addClass( this.bodyClasses );
    this.element
        .addClass('u-main-nav--overlay')
        .append(this.overlay);

    setTimeout(function(){
      _self.element.addClass( _self.config.navigationInitClasses );
      _self.body.addClass( _self.config.navigationInitBodyClasses );

      _self.transitionDuration = parseFloat( getComputedStyle(_self.element.get(0)).transitionDuration, 10 );


      if(_self.transitionDuration > 0) {

        _self.element.on("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function(e){

          // Old code
          // if(_self.isOpened && (e.originalEvent.propertyName == 'right' || e.originalEvent.propertyName == 'left')) {
          //   _self.config.afterOpen.call(_self.element, _self.overlay);
          // }
          // else if(!_self.isOpened && (e.originalEvent.propertyName == 'right' || e.originalEvent.propertyName == 'left')) {
          //   _self.config.afterClose.call(_self.element, _self.overlay);
          // }

          // New code
          if(_self.isOpened) {
            _self.config.afterOpen.call(_self.element, _self.overlay);
          }
          else if(!_self.isOpened) {
            _self.config.afterClose.call(_self.element, _self.overlay);
          }

          e.stopPropagation();
          e.preventDefault();

        });

      }

    },50);

    this._bindEvents();


    this.isInit = true;

  };


  /**
   * Destroys the instance.
   *
   * @public
   */
  HSNavigationOverlay.prototype.destroy = function() {

    var _self = this;

    if(this.overlay) this.overlay.remove();

    if(this.toggler && this.toggler.length) this.toggler.hide();

    if( $.HSCore.components.HSScrollBar ) {

      setTimeout(function(){
        $.HSCore.components.HSScrollBar.destroy( _self.element.find( '.u-main-nav__list-wrapper' ) );
      }, 10);

    }

    setTimeout(function(){
      if(_self.transitionDuration && _self.transitionDuration > 0) {
        _self.element.off("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend");
      }
    },50);

    this.body.removeClass( this.bodyClasses );
    this.element
        .removeClass('u-main-nav--overlay')
        .removeClass(this.config.navigationInitClasses);

    this.body.removeClass( this.bodyClasses ).removeClass(this.config.navigationInitBodyClasses);

    this._unbindEvents();

    this.isInit = false;

  };

  /**
   * Binds necessary events.
   *
   * @private
   */
  HSNavigationOverlay.prototype._bindEvents = function() {

    var _self = this;

    if(this.toggler && this.toggler.length) {
      this.toggler.on('click.HSNavigation', function(e){

        if(_self.isOpened) {
          _self.close();
        }
        else {
          _self.open();
        }

        e.preventDefault();

      });
    }

    this.overlay.on('click.HSNavigation', function(e){
      _self.close();
    });

    $(document).on('keyup.HSNavigation', function(e){
      if(e.keyCode == 27) {
        _self.close();
      }
    });

  };

  /**
   * Unbinds necessary events.
   *
   * @private
   */
  HSNavigationOverlay.prototype._unbindEvents = function() {

    if(this.toggler && this.toggler.length) {
      this.toggler.off('click.HSNavigation');
    }

    if(this.overlay && this.overlay.length) {
      this.overlay.off('click.HSNavigation');
    }

    $(document).off('keyup.HSNavigation');

  };


  /**
   * Shows the navigation.
   *
   * @public
   */
  HSNavigationOverlay.prototype.open = function() {

    this.body.addClass( this.config.activeClass );

    if(this.transitionDuration !== undefined && this.transitionDuration == 0) {
      this.config.afterOpen.call(this.element, this.overlay);
    }

  };

  /**
   * Hides the navigation.
   *
   * @public
   */
  HSNavigationOverlay.prototype.close = function() {

    var $this = this,
      hamburgers = $this.toggler && $this.toggler.length ? $this.toggler.find('.is-active') : $();

    if(hamburgers.length) hamburgers.removeClass('is-active');

    $this.body.removeClass( $this.config.activeClass );

    // Old code
    // if(this.transitionDuration !== undefined && this.transitionDuration == 0) {
    //   this.config.afterClose.call(this.element, this.overlay);
    // }

    // New code
    $this.element.on("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function(e) {
      $this.toggler.attr('aria-expanded', false);
      $this.element.removeClass('collapse show');
    });

  };

  /**
   * Returns true if the navigation has been initialized.
   *
   * @public
   * @return {Boolean}
   */
  HSNavigationOverlay.prototype.isInitialized = function() {

    return this.isInit;

  };

  /**
   * HSNavigationPush.
   *
   * @param {jQuery} element
   * @param {Object} config
   *
   * @constructor
   */
  function HSNavigationPush(element, config) {

    var _self = this;

    // extends some functionality from abstract class
    HSNavigationAbstract.call(this, element, config);

    Object.defineProperties(this, {

      overlayClasses: {
        get: function() {
          return 'u-main-nav__overlay ' + _self.config.navigationOverlayClasses
        }
      },

      bodyClasses: {
        get: function() {
          return 'u-main-nav--push-' + _self.config.navigationPosition
        }
      },

      isOpened: {
        get: function() {
          return _self.body.hasClass( _self.config.activeClass );
        }
      }

    });

    // this.init();

  };


  /**
   * Initialization of the instance.
   *
   * @public
   */
  HSNavigationPush.prototype.init = function() {

    var _self = this;

    /**
     * Contains overlay object.
     *
     * @public
     */
    this.overlay = $('<div></div>', {
      class: _self.overlayClasses
    });

    if( $.HSCore.components.HSScrollBar ) {

      setTimeout(function(){
        $.HSCore.components.HSScrollBar.init( _self.element.find( '.u-main-nav__list-wrapper' ) );
      }, 10);

    }

    this.toggler = $('[data-target="#'+ this.element.attr('id') +'"]');

    if(this.toggler && this.toggler.length) this.toggler.css('display', 'block');

    this.body.addClass( this.bodyClasses );
    this.element
        .addClass('u-main-nav--push')
        .append(this.overlay);

    setTimeout(function(){
      _self.element.addClass( _self.config.navigationInitClasses );
      _self.body.addClass( _self.config.navigationInitBodyClasses );

      _self.transitionDuration = parseFloat( getComputedStyle(_self.element.get(0)).transitionDuration, 10 );


      if(_self.transitionDuration > 0) {

        _self.element.on("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function(e){

          // Old code
          // if(_self.isOpened && (e.originalEvent.propertyName == 'right' || e.originalEvent.propertyName == 'left')) {
          //   _self.config.afterOpen.call(_self.element, _self.overlay);
          // }
          // else if(!_self.isOpened && (e.originalEvent.propertyName == 'right' || e.originalEvent.propertyName == 'left')) {
          //   _self.config.afterClose.call(_self.element, _self.overlay);
          // }

          // New code
          if(_self.isOpened) {
            _self.config.afterOpen.call(_self.element, _self.overlay);
          }
          else if(!_self.isOpened) {
            _self.config.afterClose.call(_self.element, _self.overlay);
          }

          e.stopPropagation();
          e.preventDefault();

        });

      }

    },50);

    this._bindEvents();

    this.isInit = true;

  };


  /**
   * Destroys the instance.
   *
   * @public
   */
  HSNavigationPush.prototype.destroy = function() {

    var _self = this;

    if(this.overlay) this.overlay.remove();

    if(this.toggler && this.toggler.length) this.toggler.hide();

    if( $.HSCore.components.HSScrollBar ) {

      setTimeout(function(){
        $.HSCore.components.HSScrollBar.destroy( _self.element.find( '.u-main-nav__list-wrapper' ) );
      }, 10);

    }

    setTimeout(function(){
      if(_self.transitionDuration && _self.transitionDuration > 0) {
        _self.element.off("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend");
      }
    },50);

    this.body.removeClass( this.bodyClasses ).removeClass(this.config.navigationInitBodyClasses);
    this.element
        .removeClass('u-main-nav--push')
        .removeClass(this.config.navigationInitClasses);

    this._unbindEvents();

    this.isInit = false;

  };

  /**
   * Binds necessary events.
   *
   * @private
   */
  HSNavigationPush.prototype._bindEvents = function() {

    var _self = this;

    if(this.toggler && this.toggler.length) {
      this.toggler.on('click.HSNavigation', function(e){

        if(_self.isOpened) {
          _self.close();
        }
        else {
          _self.open();
        }

        e.preventDefault();

      });
    }

    this.overlay.on('click.HSNavigation', function(e){
      _self.close();
    });

    $(document).on('keyup.HSNavigation', function(e){
      if(e.keyCode == 27) {
        _self.close();
      }
    });

  };

  /**
   * Unbinds necessary events.
   *
   * @private
   */
  HSNavigationPush.prototype._unbindEvents = function() {

    if(this.toggler && this.toggler.length) {
      this.toggler.off('click.HSNavigation');
    }

    if(this.overlay && this.overlay.length) {
      this.overlay.off('click.HSNavigation');
    }

    $(document).off('keyup.HSNavigation');

  };


  /**
   * Shows the navigation.
   *
   * @public
   */
  HSNavigationPush.prototype.open = function() {

    this.body.addClass( this.config.activeClass );

    if(this.transitionDuration !== undefined && this.transitionDuration == 0) {
      this.config.afterOpen.call(this.element, this.overlay);
    }

  };

  /**
   * Hides the navigation.
   *
   * @public
   */
  HSNavigationPush.prototype.close = function() {

    var hamburgers = this.toggler && this.toggler.length ? this.toggler.find('.is-active') : $();

    if(hamburgers.length) hamburgers.removeClass('is-active');

    this.body.removeClass( this.config.activeClass );

    if(this.transitionDuration !== undefined && this.transitionDuration == 0) {
      this.config.afterClose.call(this.element, this.overlay);
    }

  };

  /**
   * Returns true if the navigation has been initialized.
   *
   * @public
   * @return {Boolean}
   */
  HSNavigationPush.prototype.isInitialized = function() {

    return this.isInit;

  };


})(jQuery);