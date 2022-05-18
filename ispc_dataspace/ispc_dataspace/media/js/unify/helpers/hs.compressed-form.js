/**
 * Compressed form helper.
 *
 * @author Htmlstream
 * @version 1.0
 */
;(function($){
	'use strict';

	$.HSCore.helpers.HSCompressedForm = {


		init: function(collection){

			if(!collection || !collection.length) return;
			this.collection = collection;
			this.collection.addClass('u-compressed-form--hidden');

			this.bindEvents();

		},

		bindEvents: function(){

			var self = this;

			this.collection.on('click', function(e){

				var $this = $(this);

				if(!$this.hasClass('u-prevented')){


					e.preventDefault();
					$this.removeClass('u-compressed-form--hidden').addClass('u-prevented');

					$this.find('input').focus();

				}

			});

			$(document).on('click.uSearchform', function(e){

				if( $(e.target).closest('.u-compressed-form').length ) return;

				self.collection.addClass('u-compressed-form--hidden').removeClass('u-prevented');

			});

		}

	};

})(jQuery);