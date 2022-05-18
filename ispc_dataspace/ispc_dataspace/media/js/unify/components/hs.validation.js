/**
 * Validation wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSValidation = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {},

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Validation wrapper.
     *
     * @param String selector (optional)
     * @param Object config (optional)
     *
     * @return jQuery pageCollection - collection of initialized items.
     */

    init: function (selector, config) {

      this.collection = selector && $(selector).length ? $(selector) : $();
      if (!$(selector).length) return;

      this.config = config && $.isPlainObject(config) ?
        $.extend({}, this._baseConfig, config) : this._baseConfig;

      this.config.itemSelector = selector;

      this.initValidation(this.config);

      return this.pageCollection;

    },

    initValidation: function (config) {
      //Variables
      var $self = this,
        collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this = $(el);

        if ($this.hasClass('js-step-form')) {
          $.validator.setDefaults({
            ignore: ':hidden:not(.active select)'
          });
        } else {
          $.validator.setDefaults({
            ignore: ':hidden:not(select)'
          });
        }

        $.validator.setDefaults({
          errorPlacement: config ? false : $self.errorPlacement,
          highlight: $self.highlight,
          unhighlight: $self.unHighlight
        });

        $this.validate(config);

        $('select').change(function () {
          $(this).valid();
        });

        //Actions
        collection = collection.add($this);
      });
    },

    errorPlacement: function (error, element) {
      var $this = $(element),
        errorMsgClasses = $this.data('msg-classes');

      error.addClass(errorMsgClasses);
      error.appendTo(element.parents('.form-group'));
    },

    highlight: function (element) {
      var $this = $(element),
        errorClass = $this.data('error-class');

      $this.parents('.form-group').addClass(errorClass);
    },

    unHighlight: function (element) {
      var $this = $(element),
        errorClass = $this.data('error-class'),
        successClass = $this.data('success-class');

      $this.parents('.form-group').removeClass(errorClass).addClass(successClass);
    }
  };
})(jQuery);
