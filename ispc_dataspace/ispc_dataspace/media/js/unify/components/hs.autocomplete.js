/**
 * Autocomplete wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
;(function ($) {
  'use strict';

  $.widget('custom.catcomplete', $.ui.autocomplete, {
    _create: function () {
      this._super();
      this.widget().menu('option', 'items', '> :not(.ui-autocomplete-category)');
    },
    _renderMenu: function (ul, items) {
      var that = this,
        currentCategory = '';
      $.each(items, function (index, item) {
        var li;

        if (!item.category) {
          li = that._renderItemData(ul, item);
          return;
        }

        if (item.category != currentCategory) {
          ul.append('<li class="ui-autocomplete-category">' + item.category + '</li>');
          currentCategory = item.category;
        }
        li = that._renderItemData(ul, item);
        if (item.category) {
          li.html(item.label);
          li.attr('aria-label', item.category + ' : ' + item.label);
        }
      });
    }
  });

  $.HSCore.components.HSAutocomplete = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      minLength: 2
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Autocomplete wrapper.
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

      this.initAutocomplete();

      return this.pageCollection;

    },

    initAutocomplete: function () {
      //Variables
      var $self = this,
        config = $self.config,
        collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        var $this = $(el),
          dataUrl = $this.data('url');

        $.getJSON(dataUrl, function (data) {
          $this.catcomplete({
            delay: 0,
            source: data,
            dataType: 'json',
            minLength: config['minLength'],
            select: function (event, ui) {
              var currentItem = $(this);

              setTimeout(function () {
                var currentVal = currentItem.val();
                $(currentItem).val($(currentVal).get(0).textContent);
              }, 1);
            },
            focus: function (event, ui) {
              var currentItem = $(this);

              setTimeout(function () {
                var currentVal = currentItem.val();
                $(currentItem).val($(currentVal).get(0).textContent);
              });
            }
          });
        });

        //Actions
        collection = collection.add($this);
      });
    }

  };

})(jQuery);