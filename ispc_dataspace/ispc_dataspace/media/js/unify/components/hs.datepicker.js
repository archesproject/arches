/**
 * Datepicker wrapper.
 *
 * @author Htmlstream
 * @version 1.1
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSDatepicker = {
    /**
     *
     *
     * @var Object _baseConfig
     */
    _baseConfig: {
      dateFormat: 'dd.mm.yy',
      dayNamesMin: [
        'Sun',
        'Mon',
        'Tue',
        'Wed',
        'Thu',
        'Fri',
        'Sat'
      ],
      prevText: '<i class="fa fa-angle-left"></i>',
      nextText: '<i class="fa fa-angle-right"></i>'
    },

    /**
     *
     *
     * @var jQuery pageCollection
     */
    pageCollection: $(),

    /**
     * Initialization of Datepicker wrapper.
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

      this.initDatepicker();

      return this.pageCollection;

    },

    initDatepicker: function () {
      //Variables
      var $self = this,
        config = $self.config,
        collection = $self.pageCollection;

      //Actions
      this.collection.each(function (i, el) {
        //Variables
        var $this = $(el),
          to = $this.data('to'),
          type = $this.data('type'),
          minDate,
          maxDate;

        if (type == 'one-field-range') {
          var datePicker = $this.datepicker({
            dateFormat: config['dateFormat'],
            defaultDate: '+1w',
            dayNamesMin: config['dayNamesMin'],
            numberOfMonths: 1,
            showOtherMonths: true,
            prevText: config['prevText'],
            nextText: config['nextText'],
            beforeShow: $self.datepickerCustomClass,
            onSelect: function(dateText, inst) {
              console.log(inst);
            }
          }).on('change', function () {
            var activeDate = datePicker.datepicker("getDate");

            if(minDate == null) {
              minDate = activeDate;
            } else if(activeDate < minDate) {
              minDate = activeDate;
            }

            if(maxDate == null && activeDate > minDate) {
              maxDate = activeDate;
            } else if(activeDate > maxDate) {
              maxDate = activeDate;
            }
          });
        } else if (type == 'range') {
          var dateFrom = $this.datepicker({
            dateFormat: config['dateFormat'],
            defaultDate: '+1w',
            dayNamesMin: config['dayNamesMin'],
            numberOfMonths: 1,
            showOtherMonths: true,
            prevText: config['prevText'],
            nextText: config['nextText'],
            beforeShow: $self.datepickerCustomClass
          }).on('change', function () {
            dateTo.datepicker('option', 'minDate', $self.getDate(this));
          });

          var dateTo = $('#' + to).datepicker({
            dateFormat: config['dateFormat'],
            defaultDate: '+1w',
            dayNamesMin: config['dayNamesMin'],
            numberOfMonths: 1,
            showOtherMonths: true,
            prevText: config['prevText'],
            nextText: config['nextText'],
            beforeShow: $self.datepickerCustomClass
          }).on('change', function () {
            dateFrom.datepicker('option', 'maxDate', $self.getDate(this));
          });
        } else {
          $this.datepicker({
            dateFormat: config['dateFormat'],
            dayNamesMin: config['dayNamesMin'],
            showOtherMonths: true,
            prevText: config['prevText'],
            nextText: config['nextText'],
            beforeShow: $self.datepickerCustomClass
          });
        }

        //Actions
        collection = collection.add($this);
      });
    },

    datepickerCustomClass: function (el, attr) {
      var arrayOfClasses, customClass, i;

      arrayOfClasses = attr.input[0].className.split(' ');

      for (i = 0; arrayOfClasses.length > i; i++) {
        if (arrayOfClasses[i].substring(0, 6) == 'u-date') {
          customClass = arrayOfClasses[i];
        }
      }

      $('#ui-datepicker-div').addClass(customClass);
    },

    getDate: function (element) {
      var $self = this,
        date,
        config = $self.config;

      try {
        date = $.datepicker.parseDate(config['dateFormat'], element.value);
      } catch (error) {
        date = null;
      }

      return date;
    }
  };
})(jQuery);
