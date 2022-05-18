/**
 * Filter
 *
 * @author Htmlstream
 * @version 1.0
 *
 */
var selectedTab = $.cookie('selectedTab') ? $.cookie('selectedTab') : 0,
  filterKey = $.cookie('filterKey') ? $.cookie('filterKey') : 'all';

$(document).on('ready', function () {
  if (selectedTab != 0) {
    $('.js-shortcode-filter li').removeClass('active');
    $('.js-shortcode-filter li').eq(selectedTab).addClass('active');

    $('.js-shortcode-filter-result').children(':not(.' + filterKey + ')').hide();
    $('.js-shortcode-filter-result').children('.' + filterKey).show();
  }

  function sortUnorderedList() {
    var mylist = $('.js-shortcode-filter-result'),
      listitems = mylist.children('li').get();

    listitems.sort(function (a, b) {
      return $(a).text().toUpperCase().localeCompare($(b).text().toUpperCase());
    });

    $.each(listitems, function (idx, itm) {
      mylist.append(itm);
    });
  }

  sortUnorderedList();

  $('.js-shortcode-filter a').on('click', function (e) {
    e.preventDefault();

    var $this = $(this),
      elIndex = $this.parent().index(),
      filterKey = $this.data("shortcode-filter");

    $.cookie('selectedTab', elIndex);
    $.cookie('filterKey', filterKey);

    $('.js-shortcode-filter li').removeClass('active');
    $this.parent().addClass('active');

    if (filterKey == 'all') {
      $('.js-shortcode-filter-result').find('.js-shortcode-filter__item').show();
    }
    else {
      $('.js-shortcode-filter-result').find('li:not(.' + filterKey + ')').hide();
      $('.js-shortcode-filter-result').find('li.' + filterKey).show();
    }

    return false;
  });
});
