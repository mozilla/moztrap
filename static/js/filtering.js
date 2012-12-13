/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    // Shows/hides the advanced filtering
    MT.toggleAdvancedFiltering = function (context) {
        var advanced = $(context).find('.visual'),
            toggleAdvanced = $(context).find('.toggle a');

        toggleAdvanced.click(function (e) {
            e.preventDefault();
            advanced.toggleClass('compact expanded');
        });
    };

    // Remove filter params from URL on page-load (to avoid "stuck" filters)
    MT.removeInitialFilterParams = function (context) {
        if ($(context).length && window.location.search) {
            window.history.replaceState(null, null, '?');
        }
    };

    // Prevent Firefox javascript state caching
    // See https://developer.mozilla.org/En/Using_Firefox_1.5_caching
    MT.preventCaching = function (context) {
        if ($(context).length) {
            $(window).bind('unload.caching', function () {
                return true;
            });
        }
    };

    // Tags, suites, environments act as filter-links on list pages
    MT.directFilterLinks = function () {
        $('.listpage').on('click', '.filter-link', function (e) {
            var thisLink = $(this),
                name = thisLink.text(),
                type = thisLink.data('type');
            $('#filterform').find('.filter-group[data-name="' + type + '"] .filter-item label').filter(function () {
                return $(this).text() === name;
            }).closest('.filter-item').children('input').click();
            e.preventDefault();
        });
    };

    // Pinning a filter makes it global by putting it into the session
    MT.pinFilter = function () {
        var filterPrefix = "moztrap-filter-";

        // either add or remove a pinned filter value
        // remove=true will remove it, if it exists
        function pinFilterValue(filterKey, filterValue, add) {

            // store the filter values as an array, because it's possible
            // to filter in the same field on multiple values
            // Must store it as JSON because cookies are just strings
            var cookieVal = eval($.cookie(filterKey)) || [];

            if (add) {
                // we just pinned this filter, add the value to the cookie
                cookieVal.push(filterValue);
            }
            else {
                // remove the filter value.
                cookieVal = cookieVal.filter(function(e, i, a){
                    return e != filterValue;
                });
            }

            // if no more pinned values for this field, remove the cookie
            if (cookieVal.length == 0) {
                cookieVal = null;
            }
            else {
                // marshall back to json here
                cookieVal = JSON.stringify(cookieVal);
            }

            // certain fields have the same field name, but values don't
            // cross over.
            var path = {path: '/'};
            if (filterKey.toLowerCase() == filterPrefix + "name" ||
                filterKey.toLowerCase() == filterPrefix + "id") {
                path = {};
            }
            // filter cookies apply anywhere they're relevant
            $.cookie(filterKey, cookieVal, path);


        }

        $('.filter-group').on('click', '.pinswitch', function (e) {
            var thisPin = $(this),
                filterItem = thisPin.closest(".filter-item"),
                onoff = filterItem.find(".onoff"),
                filterValue = thisPin.data('session-value'),
                filterKey =  filterPrefix + thisPin.data('session-key');

                onoff.toggleClass("pinned");

                pinFilterValue(filterKey, filterValue, onoff.hasClass("pinned"));

        });

        $('.filter-group').on('click', '.onoffswitch', function (e) {
            var thisPin = $(this),
                filterItem = thisPin.closest(".filter-item"),
                onoff = filterItem.find(".onoff"),
                filterValue = thisPin.data('session-value'),
                filterKey =  filterPrefix + thisPin.data('session-key');

            onoff.removeClass("pinned");

            pinFilterValue(filterKey, filterValue, false);

        });
    };


    // A pinned filter should have the "pinned" class on the onoff span.
    // Check the filters against the cookies to see which ones should
    // show as pinned.
    // This is also called in a timer to update filters that were pinned
    // in another tab or window
    MT.markFiltersWithPinClass = function () {


        // get all the pinned filter cookies
        var cookieChunks = document.cookie.split("; ");
        for (var i = 0; i < cookieChunks.length; i++) {
            var chunk = cookieChunks[i];
            if (chunk.indexOf("moztrap-filter-") === 0) {
                // this is one of our filters
                var parts = chunk.split("="),
                    k = parts[0],
                    v = eval($.cookie(k)),
                    fieldVal = k.replace("moztrap-filter-", "");

                // find the filter-item that this pinned filter applies to and
                // add the "pinned" class to the "onoff" span
                $('.filter-item').filter(function(index) {
                    var input = $(this).find('input');
                    for (var j = 0; j < v.length; j++) {
                        if (input.data("name") == fieldVal && input.val() == String(v[j])) {
                            return true;
                        }
                    }
                    return false;
                }).find('.onoff').addClass('pinned');
            }
        }
    };


    // Prepare filter-form for ajax-submit
    MT.filterFormAjax = function (container) {
        var context = $(container),
            filterForm = context.find('#filterform');

        filterForm.ajaxForm({
            beforeSerialize: function (form, options) {
                var replaceList = context.find('.action-ajax-replace'),
                    pagesize = replaceList.find('.listnav').data('pagesize'),
                    sortfield = replaceList.find('.listordering').data('sortfield'),
                    sortdirection = replaceList.find('.listordering').data('sortdirection');

                replaceList.loadingOverlay();

                form.find('input[name="pagesize"]').val(pagesize);
                form.find('input[name="sortfield"]').val(sortfield);
                form.find('input[name="sortdirection"]').val(sortdirection);
            },
            success: function (response) {
                var newList = $(response.html);

                context.find('.action-ajax-replace').loadingOverlay('remove');

                if (response.html) {
                    context.find('.action-ajax-replace').replaceWith(newList);
                    newList.find('.details').html5accordion();
                    newList.trigger('after-replace', [newList]);
                }
            }
        });
    };

    // Filter list of items by hiding/showing based on selected filter-inputs
    MT.clientSideFilter = function (opts) {
        var defaults = {
                container: 'body',
                filterContainer: '#clientfilter',
                filterLists: '.visual .filter-group',
                filterSel: 'input[type="checkbox"]',
                itemList: '.itemlist .items',
                itemSel: '.listitem',
                itemCountSel: '.itemlist .listnav .itemcount'
            },
            options = $.extend({}, defaults, opts),
            context = $(options.container),
            filtering = context.find(options.filterContainer),
            filterLists = filtering.find(options.filterLists),
            itemList = context.find(options.itemList),
            itemCount = context.find(options.itemCountSel),
            items,
            filters,
            filterItems = function () {
                items = itemList.find(options.itemSel);
                filters = filterLists.find(options.filterSel + ':checked');

                if (filters.length) {
                    items.each(function () {
                        var thisItem = $(this),
                            includeThisItem = false;

                        filters.each(function () {
                            var filterType = $(this).data('name'),
                                filterName = $(this).closest('.filter-item').find('.content').text();

                            if (thisItem.find('[data-type="' + filterType + '"]').filter(function () { return $(this).text() === filterName; }).length) {
                                includeThisItem = true;
                            }
                        });

                        if (includeThisItem) {
                            thisItem.show();
                        } else {
                            thisItem.hide();
                        }
                    });
                } else {
                    items.show();
                }

                // Trigger after-filter event on itemList
                itemList.trigger('after-filter');

                // Update total item count
                itemCount.text(items.filter(':visible').length);
            };

        filterLists.on('change', options.filterSel, filterItems);
    };

    return MT;

}(MT || {}, jQuery));