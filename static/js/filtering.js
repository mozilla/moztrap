/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
*/
/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    // Shows/hides the advanced filtering
    CC.toggleAdvancedFiltering = function (context) {
        var advanced = $(context).find('.visual'),
            toggleAdvanced = $(context).find('.toggle a');

        toggleAdvanced.click(function (e) {
            e.preventDefault();
            advanced.toggleClass('compact expanded');
        });
    };

    // Remove filter params from URL on page-load (to avoid "stuck" filters)
    CC.removeInitialFilterParams = function (context) {
        if ($(context).length && window.location.search) {
            window.history.replaceState(null, null, '?');
        }
    };

    // Prevent Firefox javascript state caching
    // See https://developer.mozilla.org/En/Using_Firefox_1.5_caching
    CC.preventCaching = function (context) {
        if ($(context).length) {
            $(window).bind('unload.caching', function () {
                return true;
            });
        }
    };

    // Tags, suites, environments act as filter-links on list pages
    CC.directFilterLinks = function () {
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

    // Prepare filter-form for ajax-submit
    CC.filterFormAjax = function (container) {
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
    CC.clientSideFilter = function (opts) {
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

    return CC;

}(CC || {}, jQuery));