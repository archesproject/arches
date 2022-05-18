/**
 * File attachments helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.helpers.HSFileAttachments = {
    /**
     * File attachment.
     *
     * @return undefined
     */
    init: function () {
      var collection = $('.u-file-attach--v1 input[type="file"]:enabled, .u-file-attach--v2 input[type="file"]:enabled, .u-file-attach-v1 input[type="file"]:enabled, .u-file-attach-v2 input[type="file"]:enabled');

      if (!collection.length) return;

      collection.each(function () {
        var $this = $(this),
          $thisParent = $this.closest('.u-file-attach--v1, .u-file-attach--v2, .u-file-attach-v1, .u-file-attach-v2'),
          textInputLength = $thisParent.find('input[type="text"]:enabled');

        $this.on('change', function () {
          var thisVal = $this.val();

          if (!textInputLength.length) {
            $thisParent.find('.js-value').text(thisVal.replace(/.+[\\\/]/, ''));
          } else {
            $thisParent.find('input[type="text"]:enabled').val(thisVal);
          }
        });
      });
    }
  };
})(jQuery);
