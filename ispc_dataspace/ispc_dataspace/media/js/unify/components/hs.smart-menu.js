/**
 * SmartMenu component.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function($){
	'use strict';

	$.HSCore.components.HSSmartMenu = {

		/**
		 * Base configuration of the component.
		 *
		 * @var Object _baseConfig
		 */
		_baseConfig : {
			fixMoment: 300,
			togglerSelector: '.u-smart-nav__toggler',
			navbarSelector: '.navbar',
			menuToggleClass: 'u-smart-nav--opened',
			menuVisibleClass: 'u-smart-nav--shown',
			afterOpen: function(){},
			afterClose: function(){}
		},

		/**
		 * Collection of initialized items.
		 *
		 * @var jQuery _pageCollection
		 */
		_pageCollection : $(),

		/**
		 * Initialization of Counter wrapper.
		 *
		 * @param jQuery collection
		 * @param Object config
		 *
		 * @return jQuery
		 */
		init: function(collection, config){

			if(!collection || !collection.length) return $();

			var self = this;

			config = config && $.isPlainObject(config) ? $.extend(true, {}, this._baseConfig, config) : this._baseConfig;

			if(!this.eventInitalized) {

				// init event

				$(window).on('scroll.HSSmartMenu', function(){

					if($(document).height() > $(window).height()) {

						var $w = $(this);

						self._pageCollection.each(function(i,el){

							var $this = $(el),
									SmartMenu = $this.data('HSSmartMenu');

							if( !SmartMenu ) return;
							
							if( $w.scrollTop() >= SmartMenu.getFixMoment() && SmartMenu.isDefaultState() ) {
								SmartMenu.show();
							}
							else if( $w.scrollTop() < SmartMenu.getFixMoment() && !SmartMenu.isDefaultState() ) {
								SmartMenu.hide();
							}

						});

					}

				});		

				this.eventInitalized = true;
			}

			collection.each(function(i,el){

				var $this = $(el);

				if( $this.data('HSSmartMenu') ) return;

				$this.data('HSSmartMenu', new HSSmartMenu($this, $.extend(config, $this.data())));

				self._pageCollection = self._pageCollection.add($this);

			});

			$(window).trigger('scroll.HSSmartMenu');

			if($(document).height() <= $(window).height()) {
				self._pageCollection.each(function(i,el){

					var $this = $(el),
							SmartMenu = $this.data('HSSmartMenu');

					if( !SmartMenu ) return;

					if(SmartMenu.isDefaultState()) SmartMenu.show();

				});
			}

			$(document).on('keyup.HSSmartMenu', function(e){

				if(e.keyCode != 27) return false;

					self._pageCollection.each(function(i,el){
						var $this = $(el),
								SmartMenu = $this.data('HSSmartMenu');


						if( SmartMenu.toggler.length && SmartMenu.toggler.find('.is-active').length ) {
							SmartMenu.toggler.find('.is-active').removeClass('is-active');
						}
						SmartMenu.hideMenu();
					});
			});

			return collection;

		}

	};

	/**
	 * HSSmartMenu Constructor.
	 * 
	 * @param jQuery element
	 * @param Object config
	 */
	function HSSmartMenu(element, config) {

		if(!element || !element.length || !config || !$.isPlainObject(config)) return;

		var self = this;

		this.element = element;
		this.config = config;
		this.defaultState = true;

		this.toggler = this.element.find(this.config.togglerSelector);

		if(this.toggler.length) {
			this.toggler.on('click.HSSmartMenu', function(e){

				if(!self.element.hasClass(self.config.menuToggleClass)) {
					self.openMenu();
				}
				else {
					self.hideMenu();
				}
				e.preventDefault();

			});
		}
	}

	/**
	 * Shows navigation.
	 * 
	 * @public
	 */
	HSSmartMenu.prototype.openMenu = function( ) {

		var toggler = this.toggler ? this.toggler.find('.is-active') : $();

		this.element.addClass(this.config.menuToggleClass);
		if(this.toggler && toggler.length && !toggler.hasClass('is-active')) toggler.addClass('is-active');

	};

	/**
	 * Hides navigation.
	 * 
	 * @public
	 */
	HSSmartMenu.prototype.hideMenu = function() {
		this.element.removeClass(this.config.menuToggleClass);
	};

	/**
	 * Initialization of HSSmartMenu instance.
	 *
	 * @return Object
	 */
	HSSmartMenu.prototype.show = function() {

		this.element.addClass(this.config.menuVisibleClass);

		this.defaultState = false;
		return this;
	}

	/**
	 * Destroy of HSSmartMenu instance.
	 *
	 * @return Object
	 */
	HSSmartMenu.prototype.hide = function() {

		this.element.removeClass(this.config.menuVisibleClass);

		this.defaultState = true;
		return this;
	}

	/**
	 * Returns true if instance is in default state.
	 * 
	 * @return Boolean
	 */
	HSSmartMenu.prototype.isDefaultState = function() {
		return this.defaultState;
	}

	/**
	 * Returns fixe moment.
	 * 
	 * @return Number
	 */
	HSSmartMenu.prototype.getFixMoment = function() {
		return this.config.fixMoment;
	}

})(jQuery);