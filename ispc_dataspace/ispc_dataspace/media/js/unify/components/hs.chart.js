/**
 * Charts wrapper.
 * 
 * @author Htmlstream 
 * @version 1.0
 * @requires sparkline.js (v2.1.2), peity.js (v3.2.1)
 *
 */
;(function($){
	'use strict';

	$.HSCore.components.HSChart = {

		/**
		 * Sparkline Charts
		 */
		sparkline: {

			/**
			 * Base plugin's configuration.
			 * 
			 * @var Object _baseConfig
			 */
			_baseConfig: {
				fillColor: '#72c02c',
				lineColor: '#72c02c',
				barColor: '#72c02c'
			},

			/**
			 * Collection of all initialized items of the page.
			 * 
			 * @var jQuery _pageCollection
			 */
			_pageCollection: $(),

			/**
			 * Initializes new collection of items.
			 * 
			 * @param jQuery collections
			 *
			 * @return jQuery
			 */
			init: function(collection){

				var self = this;

				if(!collection || !collection.length) return $();

				return collection.each(function(i, el){

					var $this = $(el),
							config = $.extend(true, {}, self._baseConfig, $this.data());

					$this.sparkline( $this.data('data'), config);

					self._pageCollection = self._pageCollection.add( $this );

				});

			},

			/**
			 * Returns entire collection of initialized items or single initialized
			 * item (in case with index parameter).
			 * 
			 * @param Number index
			 *
			 * @return jQuery
			 */
			get: function(index) {

				if(index) {
					return this._pageCollection.eq(index);
				}

				return this._pageCollection;

			}

		},

		/**
		 * Peity Charts
		 */
		peity: {

			/**
			 * Base plugin's configuration.
			 * 
			 * @var Object _baseConfig
			 */
			_baseConfig: {
				fill: ''
			},

			/**
			 * Collection of all initialized items of the page.
			 * 
			 * @var jQuery _pageCollection
			 */
			_pageCollection: $(),

			/**
			 * Initializes new collection of items.
			 * 
			 * @param jQuery collections
			 *
			 * @return jQuery
			 */
			init: function(collection, config){

				var self = this;

				if(!collection || !collection.length) return $();

				config = config && $.isPlainObject(config) ? $.extend(true, {}, this._baseConfig, config) : this._baseConfig;


				return collection.each(function(i, el){

					var $this = $(el),
							currentConfig = $.extend(true, {}, config, $this.data());

					$this.peity( $this.data('peity-type'), currentConfig );

					self._pageCollection = self._pageCollection.add( $this );

				});

			},

			/**
			 * Returns entire collection of initialized items or single initialized
			 * item (in case with index parameter).
			 * 
			 * @param Number index
			 *
			 * @return jQuery
			 */
			get: function(index) {

				if(index) {
					return this._pageCollection.eq(index);
				}

				return this._pageCollection;

			}

		}
		
	};

})(jQuery);