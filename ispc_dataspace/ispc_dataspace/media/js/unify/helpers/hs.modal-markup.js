/**
 * Modal markup helper-wrapper.
 *
 * @author Htmlstream
 * @version 1.0
 * @requires chart.js (v1.0.3)
 *
 */
;(function ($) {
  'use strict';
  $.HSCore.helpers.HSModalMarkup = {
    /**
     * Modal markup.
     *
     * @return undefined
     */
    init: function (el) {
      var collection = $(el);

      if (!collection.length) return;

      var target,
        HTMLArr = {},
        stylesArr = {},
        scriptsArr = {};

      collection.each(function () {
        var $this = $(this),
          contentTarget = $this.data('content-target');

        HTMLArr[contentTarget] = $(contentTarget + ' .shortcode-html').length ? $(contentTarget + ' .shortcode-html').html().replace(/&quot;/g, "'") : $(contentTarget).html().replace(/&quot;/g, "'").replace(/type=\"text\/plain\"/g, '');
        stylesArr[contentTarget] = $(contentTarget + ' .shortcode-styles').length ? $(contentTarget + ' .shortcode-styles').html().replace(/&quot;/g, "'").replace(/type=\"text\/plain\"/g, '') : '';
        scriptsArr[contentTarget] = $(contentTarget + ' .shortcode-scripts').length ? $(contentTarget + ' .shortcode-scripts').html().replace(/&quot;/g, "'").replace(/type=\"text\/plain\"/g, '') : '';
      });

      $(el).on('click', function () {
        target = $(this).data('content-target');
      });

      $.HSCore.components.HSModalWindow.init(el, {
        onOpen: function () {
          if (stylesArr[target] != '' || scriptsArr[target] != '') {
            $('.custombox-content .modal-demo')
              .append('<div id="modalMarkupContent" style="height: 100%;"><ul class="nav text-center justify-content-center u-nav-v5-2 u-nav-primary g-mb-10" role="tablist"></ul><div id="modalMarkupInner" class="tab-content" style="height: calc(100% - 47px);"></div></div>');

            $('.custombox-content .nav')
              .append('<li class="nav-item"><a class="nav-link active" data-toggle="tab" href="#markupHTML" role="tab">HTML</a></li>');

            $('.custombox-content .tab-content')
              .append('<div id="markupHTML" class="markup-inner tab-pane g-brd-around g-brd-gray-light-v1 fade show active" role="tabpanel" style="max-height: 100%;"><pre><code class="language-markup"><div></div></code></pre></div>')
              .find('#markupHTML code > div')
              .text(HTMLArr[target]);

            if (stylesArr[target] != '') {
              $('.custombox-content .nav')
                .append('<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#markupStyles" role="tab">Styles</a></li>');

              $('.custombox-content .tab-content')
                .append('<div id="markupStyles" class="markup-inner tab-pane g-brd-around g-brd-gray-light-v1 fade" role="tabpanel" style="max-height: 100%;"><pre><code class="language-markup"><div></div></code></pre></div>')
                .find('#markupStyles code > div')
                .text(stylesArr[target]);
            }

            if (scriptsArr[target] != '') {
              $('.custombox-content .nav')
                .append('<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#markupScripts" role="tab">Scripts</a></li>');

              $('.custombox-content .tab-content')
                .append('<div id="markupScripts" class="markup-inner tab-pane g-brd-around g-brd-gray-light-v1 fade" role="tabpanel" style="max-height: 100%;"><pre><code class="language-markup"><div></div></code></pre></div>')
                .find('#markupScripts code > div')
                .text(scriptsArr[target]);
            }

            $.HSCore.components.HSTabs.init('[role="tablist"]');
          } else {
            $('.custombox-content .modal-demo')
              .append('<div id="modalMarkupContent" style="height: 100%;"><div id="modalMarkupInner" class="markup-inner g-brd-around g-brd-gray-light-v1" style="max-height: 100%;"><pre><code class="language-markup"><div></div></code></pre></div></div>')
              .find('#modalMarkupInner code > div')
              .text(HTMLArr[target]);
          }

          $.HSCore.components.HSScrollBar.init($('.custombox-content .markup-inner'));

          Prism.highlightAll();
        },
        onClose: function () {
          $('#modalMarkupContent').remove();
        }
      });
    }
  };
})(jQuery);
