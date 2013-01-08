/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery, URI */

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
            var cookieVal = JSON.parse($.cookie(filterKey)) || [];

            if (add) {
                // we just pinned this filter, add the value to the cookie
                cookieVal.push(filterValue);
            }
            else {
                // remove the filter value.
                cookieVal = cookieVal.filter(function (e, i, a) {
                    return e !== filterValue;
                });
            }

            // if no more pinned values for this field, remove the cookie
            if (cookieVal.length === 0) {
                cookieVal = null;
            }
            else {
                // marshall back to json here
                cookieVal = JSON.stringify(cookieVal);
            }

            // certain fields have the same field name, but values don't
            // cross over.
            var path = {path: '/'};
            if (filterKey.toLowerCase() === filterPrefix + "name" ||
                filterKey.toLowerCase() === filterPrefix + "id") {
                path = {};
                if (cookieVal) {
                    $(ich.message({
                        message: "Note: This pinned filter value is constrained to this page only.",
                        tags: "warning"
                    })).appendTo($('#messages ul'));
                    $('#messages ul').messages();
                }
            }
            // filter cookies apply anywhere they're relevant
            $.cookie(filterKey, cookieVal, path);

        }

        $('.filter-group').on('click', '.pinswitch', function (e) {
            var thisPin = $(this),
                filterItem = thisPin.closest(".filter-item"),
                onoff = filterItem.find(".onoff"),
                fiInput = filterItem.find('input'),
                filterValue = fiInput.val(),
                filterKey =  filterPrefix + fiInput.data('name');

            onoff.toggleClass("pinned");

            pinFilterValue(filterKey, filterValue, onoff.hasClass("pinned"));

        });

        $('.filter-group').on('click', '.onoffswitch', function (e) {
            var thisPin = $(this),
                filterItem = thisPin.closest(".filter-item"),
                onoff = filterItem.find(".onoff"),
                fiInput = filterItem.find('input'),
                filterValue = fiInput.val(),
                filterKey =  filterPrefix + fiInput.data('name');

            onoff.removeClass("pinned");

            pinFilterValue(filterKey, filterValue, false);

        });
    };

    MT.getPinnedFilters = function () {
        var cookieChunks = document.cookie.split("; "),
            prefix = "moztrap-filter-",
            uri = new URI(MT.getActionAjaxReplaceUri()),
            filters = {};

        for (var i = 0; i < cookieChunks.length; i++) {
            var chunk = cookieChunks[i];
            if (chunk.indexOf(prefix) === 0) {
                // this is one of our filters
                var parts = chunk.split("="),
                    k = parts[0],
                    v = JSON.parse($.cookie(k));
                filters[k.replace(prefix, "")] = v;
            }
        }

        return filters;
    };

    // A pinned filter should have the "pinned" class on the onoff span.
    // Just used for first display of the screen, if filters are in the
    // session already.
    //
    // 1. Check the filters against the cookies to see which ones should
    //    show as pinned.
    // 2. Update the ajax replace url to reflect the pinned filters
    MT.updatePageForExistingPinnedFilters = function () {


        // get all the pinned filter cookies
        var filters = MT.getPinnedFilters(),
            uri = new URI(MT.getActionAjaxReplaceUri());

        for (var key in filters) {
            var values = filters[key];

            // update the uri to have the pinned value
            uri.addSearch("filter-" + key, values);

            // find the filter-item that this pinned filter applies to and
            // add the "pinned" class to the "onoff" span
            var inputs = "input[value='" + values.join("',[value='") +  "']";
            var terst = $(".filter-group[data-name='" + key + "'] " + inputs);
            terst.parent().find('.onoff').addClass('pinned');
        }
        MT.setActionAjaxReplaceUri(uri.toString());
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