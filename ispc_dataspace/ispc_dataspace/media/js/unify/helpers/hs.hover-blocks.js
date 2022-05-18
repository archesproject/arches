/**
 * Charts helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires chart.js (v1.0.3)
 *
 */
;(function($){
	'use strict';

	$.HSCore.helpers.HSHoverBlocks = {

		/**
		 * Helper function for correct work the 'pappercut' hover.
		 * 
		 * @return undefined
		 */
		papercut: function(){

			var collection = $('.g-block-hover__additional--pappercut-front, .g-block-hover__additional--pappercut-back');

			if(!collection.length) return;

			collection.each(function(){
        var $this = $(this),
            clipArea = $this.closest('.g-block-hover').outerHeight() / 2 + 60;

          $this.css('background-image', 'url(' + $this.children('img').hide().attr('src') + ')');

          if($this.hasClass('g-block-hover__additional--pappercut-front')){
            $this.css('clip', 'rect(0px, auto, ' +clipArea+ 'px, 0px)');
          }
          else{
            $this.css('clip', 'rect('+clipArea+'px, auto, auto, 0px)');
          }
      });

		}

	};

})(jQuery);