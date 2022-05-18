/**
 * Text Slideshow wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires charming.js, anime.js, textfx.js
 *
 */
;
(function($) {
  'use strict';

  $.HSCore.components.HSTextSlideshow = {

    /**
     * Base configuration.
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      autoplay: false,
      autoplayDelay: 3000,
      slideSelector: '.u-text-slideshow__slide',
      activeSlideClass: 'u-text-slideshow__slide--current',
      slideTargetSelector: '.u-text-slideshow__slide-target'
    },

    /**
     * Collection of all instances of the page.
     *
     * @var jQuery _pageCollection
     */
    _pageCollection: $(),


    /**
     * Initialization of Slideshow.
     *
     * @param jQuery collection (optional)
     * @param Object config (optional)
     *
     * @return jQuery pageCollection - collection of initialized items.
     */
    init: function(collection, config) {

      if(!collection || !collection.length) return this._pageCollection;

      var self = this;

      config = config && $.isPlainObject(config) ? $.extend(true, {}, this._baseConfig, config) : this._baseConfig;


      collection.each(function(i, el){

        var $this = $(this);

        if(!$this.data('HSTextSlideshow')) {

          $this.data('HSTextSlideshow', new HSTextSlideshow($this, $.extend(true, {}, config, {
            effect: $this.data('effect') ? $this.data('effect') : 'fx1'
          })));
          self._pageCollection = self._pageCollection.add($this);

        }


      });

      return this._pageCollection;
    }

  }

  /**
   * Constructor function of Slideshow.
   *
   * @param jQuery element
   * @param Object config
   *
   * @return undefined
   */
  function HSTextSlideshow(element, config) {
    this.config = config && $.isPlainObject(config) ? config : {};

    this.element = element;

    this.config = $.extend(true, {}, this.config, this.element.data() );

    var jCurrentSlide = this.element.find('.' + this.config.activeSlideClass);

    this.currentIndex = this.config.currentIndex = jCurrentSlide.length ? jCurrentSlide.index() : 0;

    this.slides = [];

    if( this.element.attr('id') ) this._initNavigation();

    this._initSlides();

    if( this.config.autoplay ) {
      this._autoplayStart();
    }
  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype._initSlides = function() {

    var self = this,
        jSlides = this.element.find(this.config.slideSelector);

    if(jSlides.length) {
      jSlides.each(function(i, el){

        self.addSlide( $(el), self.config );

      });
    }

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype._updateCarouselBounds = function() {

    var self = this;

    this.element.stop().animate({
      'width': self.slides[self.currentIndex].getElement().outerWidth() + 1
    }, {
      duration: 300,
      easing: 'linear'
    });

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype._autoplayStart = function() {

    var self = this;

    this.autoplayTimeoutId = setTimeout( function autoplay() {

      self.next();

      self.autoplayTimeoutId = setTimeout( autoplay, self.config.autoplayDelay );

    }, this.config.autoplayDelay );

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype._autoplayStop = function() {

    clearTimeout( this.autoplayTimeoutId );

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype._initNavigation = function() {

    var self = this,
        navElements = $( '[data-target="#'+this.element.attr('id')+'"]' );

    navElements.on('click', function(e){

      var $this = $(this);

      if( $this.data('action').toUpperCase() == 'PREV' ) {
        if( self.config.autoplay ) {
          self._autoplayStop();
          self._autoplayStart();
        }
        self.prev();
      }
      else if( $this.data('action').toUpperCase() == 'NEXT' ) {
        if( self.config.autoplay ) {
          self._autoplayStop();
          self._autoplayStart();
        }
        self.next();
      }

      e.preventDefault();
    });

    navElements.each(function(i, el){

      var $this = $(el);

      if( $this.data('action') ) {
        self['_initAction' + $this.data('action').toUpperCase( $this )];
      }

    });

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype.addSlide = function(element, config) {

    if(!element || !element.length) return;
    this.slides.push( new HSTextSlide( element, config ) );

  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype.next = function() {

    if(this.slides.length <= 1) return;

    this.slides[this.currentIndex].hide();

    this.currentIndex++;

    if(this.currentIndex > this.slides.length - 1) this.currentIndex = 0;

    this._updateCarouselBounds();
    this.slides[this.currentIndex].show();
  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlideshow.prototype.prev = function() {

    if(this.slides.length <= 1) return;

    this.slides[this.currentIndex].hide();

    this.currentIndex--;

    if(this.currentIndex < 0) this.currentIndex = this.slides.length - 1;

    this._updateCarouselBounds();
    this.slides[this.currentIndex].show();
  }


  /**
   * Constructor function of Slide.
   *
   * @param jQuery element
   *
   * @return undefined
   */
  function HSTextSlide(element, config) {
    this.element = element;
    this.config = config;

    this.target = element.find( config.slideTargetSelector ).get(0);

    if(!this.target) return;

    this.textfx = new TextFx( this.target );

    if( this.config.currentIndex != this.element.index() ) {
      $(this.target).find('[class*="letter"]').css( this.textfx.effects[config.effect].out );
    }
  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlide.prototype.show = function() {
    if(!this.target) return;

    this.element.addClass(this.config.activeSlideClass);

    this.textfx.show(this.config.effect);
  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlide.prototype.hide = function() {
    if(!this.target) return;

    this.element.removeClass(this.config.activeSlideClass);

    this.textfx.hide(this.config.effect);
  }

  /**
   *
   *
   * @param
   *
   * @return
   */
  HSTextSlide.prototype.getElement = function() {

    return this.element;

  }

})(jQuery);
