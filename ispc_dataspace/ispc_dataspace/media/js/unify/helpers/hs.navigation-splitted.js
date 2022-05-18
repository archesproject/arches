/**
 * Helper for splitted-navigation element.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function($){
	'use strict';

	$.HSCore.helpers.HSNavigationSplitted = {

		/**
		 * Base configuration of the helper.
		 * 
		 * @private 
		 */
		_baseConfig: {
			breakpoint: 992,
			mobileTarget: null,
			logoSelector: '.navbar-brand',
			logoItemSelector: '.nav-logo-item'
		},

		/**
		 * Contains all initialized items on the page.
		 * 
		 * @private
		 */
		_pageCollection: $(),

		/**
		 * Initialization.
		 * 
		 * @param {jQuery} collection
		 * @param {Object} config
		 *
		 * @return {jQuery}
		 */
		init: function(collection, config) {

			var self;

			if(!collection || !collection.length) return $();

			self = this;

			$(window).on('resize.HSSplitteNavigation', function(){

				if( self.resizeTimeOutId ) clearTimeout( self.resizeTimeOutId );

				self.resizeTimeOutId = setTimeout(function(){
					self._pageCollection.each(function(i, el){
						$(el).data('HSSplittedNavigation').check();
					});
				},10);

			});

			collection.each(function(i, el){

				var $item = $(el);

				config = config && $.isPlainObject(config) ?
								$.extend(true, {}, self._baseConfig, config, $item.data()) :
								$.extend(true, {}, self._baseConfig, $item.data());

				if( $item.data('HSSplittedNavigation') ) return;

				$item.data('HSSplittedNavigation', new HSSplittedNavigation( $item, config ));
				self._pageCollection = self._pageCollection.add($item);

			});

			self._pageCollection.each(function(i, el){
				$(el).data('HSSplittedNavigation').run();
			});

			return collection;

		}
		

	};

	/**
	 * Creates a splitted-navigation object.
	 * 
	 * @param {jQuery} element
	 * @param {Object} config
	 *
	 * @constructor 
	 */
	function HSSplittedNavigation(element, config) {
		this.element = element;
		this.config = config;

		this.logo = this.element.find( this.config.logoSelector );
		this.logoItem = this.element.find( this.config.logoItemSelector );
		this.target = this.element.find( this.config.mobileTarget ).length ? this.element.find( this.config.mobileTarget ) : this.element;
	}

	/**
	 * 
	 *
	 * @public 
	 * @return {HSSplittedNavigation}
	 */
	HSSplittedNavigation.prototype.run = function() {

		this[$(window).width() < this.config.breakpoint ? 'toMobileState' : 'toDefaultState']();

		return this;

	}

	/**
	 * 
	 *
	 * @public 
	 * @return {HSSplittedNavigation}
	 */
	HSSplittedNavigation.prototype.check = function() {

		var $w = $(window);

		if( $w.width() < this.config.breakpoint && this.defaultState) {
			this.toMobileState();
		}
		else if( $w.width() >= this.config.breakpoint && !this.defaultState ) {
			this.toDefaultState();
		}

		return this;

	}

	/**
	 * 
	 *
	 * @public
	 * @return {HSSplittedNavigation}
	 */
	HSSplittedNavigation.prototype.toDefaultState = function() {
		if( !this.logoItem.length || !this.logo.length ) return this;

		this.logoItem.show().append( this.logo );

		this.defaultState = true;
		return this;
	}

	/**
	 * 
	 * 
	 * @public
	 * @return {HSSplittedNavigation}
	 */
	HSSplittedNavigation.prototype.toMobileState = function() {
		if( !this.logoItem.length || !this.logo.length ) return this;

		this.target.before( this.logo );
		this.logoItem.hide();

		this.defaultState = false;
		return this;
	}

})(jQuery);