/**
 * NL Form wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSNLForm = {
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
     * Initialization of NL Form wrapper.
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

      this.initNLForm();

      return this.pageCollection;

    },

    initNLForm: function () {
      //Variables
      var $self = this,
          collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        var $this = $(el)[0].id;

        //Variables
        var nlform = new NLForm(document.getElementById($this));

        //Actions
        collection = collection.add($this);
      });
    }

  };

})(jQuery);