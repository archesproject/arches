/**
 * Sticky blocks wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires
 *
 */
;(function ($) {
  'use strict';

  $.HSCore.components.HSStickyBlock = {
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
     * Initialization of Sticky blocks wrapper.
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

      this.initStickyBlock();

      return this.pageCollection;
    },

    initStickyBlock: function () {
      //Variables
      var $self = this,
        config = $self.config,
        collection = $self.pageCollection,
        windW = $(window).width();

      this.collection.each(function (i, el) {
        //Variables
        var $stickyBlock = $(el),
          isResponsive = Boolean($stickyBlock.data('responsive')),
          stickyBlockClasses = $stickyBlock.attr('class').replace($self.config.itemSelector.substring(1), ''),
          stickyBlockH = $stickyBlock.outerHeight(),
          stickyBlockW = $stickyBlock.outerWidth(),
          stickyBlockParentW = $stickyBlock.parent().width(),
          stickyBlockOffsetTop = $stickyBlock.offset().top,
          stickyBlockOffsetLeft = $stickyBlock.offset().left,
          startPoint = $.isNumeric($stickyBlock.data('start-point')) ? $stickyBlock.data('start-point') : $($stickyBlock.data('start-point')).offset().top,
          endPoint = $.isNumeric($stickyBlock.data('end-point')) ? $stickyBlock.data('end-point') : $($stickyBlock.data('end-point')).offset().top,
          hasStickyHeader = $stickyBlock.data('has-sticky-header');

        //Break function if there are no target element
        if (!$stickyBlock.length) return;
        if (stickyBlockH > (endPoint - startPoint)) return;

        $self.resolutionCheck($stickyBlock);

        if ($stickyBlock.hasClass('g-sticky-block--sm') && windW <= 576) {
          $stickyBlock.addClass('die-sticky');
          $self.resolutionCheck($stickyBlock);
        } else if ($stickyBlock.hasClass('g-sticky-block--md') && windW <= 768) {
          $stickyBlock.addClass('die-sticky');
          $self.resolutionCheck($stickyBlock);
        } else if ($stickyBlock.hasClass('g-sticky-block--lg') && windW <= 992) {
          $stickyBlock.addClass('die-sticky');
          $self.resolutionCheck($stickyBlock);
        } else if ($stickyBlock.hasClass('g-sticky-block--xl') && windW <= 1200) {
          $stickyBlock.addClass('die-sticky');
          $self.resolutionCheck($stickyBlock);
        } else {
          $stickyBlock.removeClass('die-sticky');
        }

        $(window).on('resize', function () {
          var windW = $(window).width();

          if ($stickyBlock.hasClass('g-sticky-block--sm') && windW <= 576) {
            $stickyBlock.addClass('die-sticky');
            $self.resolutionCheck($stickyBlock);
          } else if ($stickyBlock.hasClass('g-sticky-block--md') && windW <= 768) {
            $stickyBlock.addClass('die-sticky');
            $self.resolutionCheck($stickyBlock);
          } else if ($stickyBlock.hasClass('g-sticky-block--lg') && windW <= 992) {
            $stickyBlock.addClass('die-sticky');
            $self.resolutionCheck($stickyBlock);
          } else if ($stickyBlock.hasClass('g-sticky-block--xl') && windW <= 1200) {
            $stickyBlock.addClass('die-sticky');
            $self.resolutionCheck($stickyBlock);
          } else {
            $stickyBlock
              .removeClass('die-sticky')
              .css({
                'top': '',
                'left': ''
              });
          }

          if (isResponsive == true) {
            setTimeout(function () {
              var offsetTop = $(this).scrollTop(),
                headerH = $('header').outerHeight();
              stickyBlockH = $stickyBlock.outerHeight(),
                stickyBlockParentW = $stickyBlock.parent().width(),
                stickyBlockOffsetTop = $stickyBlock.parent().offset().top,
                stickyBlockOffsetLeft = $stickyBlock.parent().offset().left + parseInt($stickyBlock.parent().css('padding-left')),
                startPoint = $.isNumeric($stickyBlock.data('start-point')) ? $stickyBlock.data('start-point') : $($stickyBlock.data('start-point')).offset().top,
                endPoint = $.isNumeric($stickyBlock.data('end-point')) ? $stickyBlock.data('end-point') : $($stickyBlock.data('end-point')).offset().top;

              if (hasStickyHeader === true) {
                $stickyBlock
                  .not('.die-sticky')
                  .css({
                    'top': offsetTop + headerH >= (endPoint - stickyBlockH) ? endPoint - stickyBlockH - stickyBlockOffsetTop : headerH,
                    'left': stickyBlockOffsetLeft,
                    'width': stickyBlockParentW
                  });

                // if (offsetTop + headerH <= (endPoint - stickyBlockH)) {
                //   $stickyBlock
                //     .not('.die-sticky')
                //     .addClass('g-pos-fix g-m-reset');
                // }
              } else {
                $stickyBlock
                  .not('.die-sticky')
                  .css({
                    'top': offsetTop >= (endPoint - stickyBlockH) ? endPoint - stickyBlockH - stickyBlockOffsetTop : 0,
                    'left': stickyBlockOffsetLeft,
                    'width': stickyBlockParentW
                  });

                // if (offsetTop <= (endPoint - stickyBlockH)) {
                //   $stickyBlock
                //     .not('.die-sticky')
                //     .addClass('g-pos-fix g-m-reset');
                // }
              }
            }, 400);
          }
        });

        if (isResponsive == false) {
          //Add "shadow" element
          var offsetTop = $(this).scrollTop();

          /* Args:
           * [1: target element]
           * [2: window offset top]
           * [3: target element height]
           * [4: target element width]
           * [5: target element index]
           * [6: target element classes (exclude init class)]
           * [7: start point]
           * [8: end point]
           */
          $self.addShadow($stickyBlock, offsetTop, stickyBlockH, stickyBlockW, i, stickyBlockClasses, startPoint, endPoint, hasStickyHeader);

          //Add sticky state
          /* Args:
           * [1: target element]
           * [2: window offset top]
           * [3: target element height]
           * [4: target element width]
           * [5: target offset left]
           * [6: start point]
           * [7: end point]
           */
          $self.addSticky($stickyBlock, offsetTop, stickyBlockH, stickyBlockW, stickyBlockOffsetLeft, startPoint, endPoint, hasStickyHeader);
        } else {
          //Add responsive sticky state
          var offsetTop = $(this).scrollTop();

          /* Args:
           * [1: target element]
           * [2: window offset top]
           * [3: parent element height]
           * [4: parent element width]
           * [5: target offset left]
           * [6: start point]
           * [7: end point]
           */
          $self.addSticky($stickyBlock, offsetTop, 'auto', stickyBlockParentW, stickyBlockOffsetLeft, startPoint, endPoint, hasStickyHeader);
        }

        $(window).on('scroll', function () {
          var offsetTop = $(this).scrollTop();

          if (isResponsive == false) {
            //Add "shadow" element
            /* Args:
             * [1: target element]
             * [2: window offset top]
             * [3: target element height]
             * [4: target element width]
             * [5: target element index]
             * [6: target element classes (exclude init class)]
             * [7: start point]
             * [8: end point]
             */
            $self.addShadow($stickyBlock, offsetTop, stickyBlockH, stickyBlockW, i, stickyBlockClasses, startPoint, endPoint, hasStickyHeader);

            //Add sticky state
            /* Args:
             * [1: target element]
             * [2: window offset top]
             * [3: target element height]
             * [4: target element width]
             * [5: target offset left]
             * [6: start point]
             * [7: end point]
             */
            $self.addSticky($stickyBlock, offsetTop, stickyBlockH, stickyBlockW, stickyBlockOffsetLeft, startPoint, endPoint, hasStickyHeader);
          } else {
            //Add responsive sticky state
            /* Args:
             * [1: target element]
             * [2: window offset top]
             * [3: parent element height]
             * [4: parent element width]
             * [5: target offset left]
             * [6: start point]
             * [7: end point]
             */
            $self.addSticky($stickyBlock, offsetTop, 'auto', stickyBlockParentW, stickyBlockOffsetLeft, startPoint, endPoint, hasStickyHeader);
          }

          //Remove sticky state
          /* Args:
           * [1: target element]
           * [2: window offset top]
           * [3: start point]
           */
          $self.removeSticky($stickyBlock, offsetTop, startPoint, hasStickyHeader);

          if (endPoint) {
            //Add absolute state
            /* Args:
             * [1: target element]
             * [2: target element height]
             * [3: target element index]
             * [4: target offset top]
             * [5: window offset top]
             * [6: end point]
             */

            $self.addAbsolute($stickyBlock, stickyBlockH, i, stickyBlockOffsetTop, offsetTop, endPoint, hasStickyHeader);
          }
        });

        $(window).trigger('scroll');

        //Add object to collection
        collection = collection.add($stickyBlock);
      });
    },

    addSticky: function (target, offsetTop, targetH, targetW, offsetLeft, startPoint, endPoint, hasStickyHeader) {
      if (hasStickyHeader === true) {
        var headerH = $('header').outerHeight();

        if (offsetTop + headerH >= startPoint && offsetTop + headerH < endPoint) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-rel')
            .css({
              'top': '',
              'left': '',
              'width': '',
              'height': ''
            })
            .addClass('g-pos-fix g-m-reset')
            .css({
              'top': headerH,
              'left': offsetLeft,
              'width': targetW,
              'height': targetH
            });
        }
      } else {
        if (offsetTop >= startPoint && offsetTop < endPoint) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-rel')
            .css({
              'top': '',
              'left': '',
              'width': '',
              'height': ''
            })
            .addClass('g-pos-fix g-m-reset')
            .css({
              'top': 0,
              'left': offsetLeft,
              'width': targetW,
              'height': targetH
            });
        }
      }
    },

    removeSticky: function (target, offsetTop, startPoint, hasStickyHeader) {
      if (hasStickyHeader === true) {
        var headerH = $('header').outerHeight();

        if (offsetTop + headerH <= startPoint) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-fix g-m-reset')
            .css({
              'left': ''
            });
        }
      } else {
        if (offsetTop <= startPoint) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-fix g-m-reset')
            .css({
              'left': ''
            });
        }
      }
    },

    addAbsolute: function (target, targetH, targetI, targetOffsetTop, offsetTop, endPoint, hasStickyHeader) {
      if (target.hasClass('g-pos-rel')) return;

      if (hasStickyHeader === true) {
        var headerH = $('header').outerHeight();

        if (offsetTop + headerH >= endPoint - targetH) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-fix g-m-reset')
            .addClass('g-pos-rel')
            .css({
              'top': endPoint - targetH - targetOffsetTop,
              'left': ''
            });
        }
      } else {
        if (offsetTop >= endPoint - targetH) {
          target
            .not('.die-sticky')
            .removeClass('g-pos-fix g-m-reset')
            .addClass('g-pos-rel')
            .css({
              'top': endPoint - targetH - targetOffsetTop,
              'left': ''
            });
        }
      }
    },

    addShadow: function (target, offsetTop, targetH, targetW, targetI, targetClasses, startPoint, endPoint, hasStickyHeader) {
      if (hasStickyHeader === true) {
        var headerH = $('header').outerHeight();

        if (offsetTop + headerH > startPoint && offsetTop + headerH < (endPoint - targetH)) {
          if ($('#shadow' + targetI).length) return;

          //Add shadow block
          target
            .not('.die-sticky')
            .before('<div id="shadow' + targetI + '" class="' + targetClasses + '" style="height: ' + targetH + 'px; width: ' + targetW + 'px"></div>');
        } else {
          if (!$('#shadow' + targetI).length) return;

          //Remove shadow block
          $('#shadow' + targetI).remove();
        }
      } else {
        if (offsetTop > startPoint && offsetTop < (endPoint - targetH)) {
          if ($('#shadow' + targetI).length) return;

          //Add shadow block
          target
            .not('.die-sticky')
            .before('<div id="shadow' + targetI + '" class="' + targetClasses + '" style="height: ' + targetH + 'px; width: ' + targetW + 'px"></div>');
        } else {
          if (!$('#shadow' + targetI).length) return;

          //Remove shadow block
          $('#shadow' + targetI).remove();
        }
      }
    },

    resolutionCheck: function (target) {
      target
        .removeClass('g-pos-fix g-m-reset')
        .css({
          'top': '',
          'left': '',
          'width': '',
          'height': ''
        });
    }
  }
})(jQuery);
