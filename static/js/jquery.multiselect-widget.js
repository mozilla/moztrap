/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, ich, URI */

/**
 * jQuery Multiselect Widget 0.3
 *
 * Copyright (c) 2012, Jonny Gerig Meyer
 * Copyright (c) 2013 Cameron Dawson
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    // cache for the ajax calls for multiselect items.
    var cache = {};

    // any ajax requests currently in progress so we can abort them if
    // we want to start a new one.
    var current_xhrs = {};

    var methods = {
        init: function (opts) {
            var options = $.extend({}, msDefaults, opts),
                context = $(this),
                filterLists = context.find(options.availableSel + ' ' +
                    options.filterListSel),
                availableList = context.find(options.availableSel + ' ' +
                    options.itemListSel),
                includedList = context.find(options.includedSel + ' ' +
                    options.itemListSel),
                bulkInclude = context.find(options.bulkIncludeSel),
                bulkExclude = context.find(options.bulkExcludeSel),
                form = $(options.formSel),
                headers = context.find(options.headerSel),
                bulkSelects = context.find(options.bulkSel);


            context.multiselect("filterItemsAjax",
                options.filter_type_map,
                options.ich_template);

            context.find(".visual").bind('DOMNodeInserted DOMNodeRemoved', function (event) {
                context.multiselect("filterItemsAjax",
                                    options.filter_type_map,
                                    options.ich_template);
            });

            // add change handlers to all the checkboxes in the filter groups
            context.multiselect("addFilterHandlers",
                                options.filter_type_map,
                                options.ich_template);

            // add click handlers to tag chicklets in both lists
            availableList.add(includedList).on(
                'click', options.itemSel + ' .tags a', function clickTagChicklet(e) {
                var tagId = $(this).data("id").toString();
                filterLists.filter('[data-name="tag"]').find('input').filter(
                    function () {
                        return $(this).val() === tagId;
                    }
                ).closest('.filter-item').find(options.filterSel).prop(
                    'checked', true).change();
                e.preventDefault();
            });

            availableList.add(includedList).sortable({
                items: options.itemSel,
                connectWith: '.sortable',
                revert: 200,
                delay: 50,
                opacity: 0.7,
                placeholder: 'sortable-placeholder',
                forcePlaceholderSize: true,
                scroll: false,
                tolerance: 'pointer',
                update: function (event, ui) {
                    ui.item.closest(options.availableSel).find(
                        options.filterListSel + ' ' + options.filterSel + ':checked'
                    ).prop('checked', false).change();
                    ui.item.find(options.inputSel).prop('checked', false);
                    context.multiselect("updateBulkSel", availableList.closest('.itemlist').find(
                        options.bulkSel), availableList);
                    context.multiselect("updateBulkSel", includedList.closest('.itemlist').find(
                        options.bulkSel), includedList);
                    headers.removeClass('asc desc');
                }
            });

            // check items for bulk include / exclude
            context.on('click', options.itemListSel + ' ' + options.labelSel,
                function (e) {
                var thisLabel = $(this),
                    thisInput = thisLabel.closest(options.itemSel).find(
                        options.inputSel),
                    labels = thisLabel.closest(options.itemListSel).find(
                        options.labelSel + ':visible'),
                    thisIndex,
                    recentlyClicked,
                    recentlyClickedIndex,
                    filteredLabels;

                if (e.shiftKey) {
                    if (labels.filter(function () { return $(this).data('clicked') === true; }).length) {
                        recentlyClicked = labels.filter(function () { return $(this).data('clicked') === true; });
                    } else if (labels.filter(function () { return $(this).data('unclicked') === true; }).length) {
                        recentlyClicked = labels.filter(function () { return $(this).data('unclicked') === true; });
                    }
                    thisIndex = thisLabel.closest(options.itemSel).index();
                    recentlyClickedIndex = recentlyClicked.closest(options.itemSel).index();
                    filteredLabels = labels.filter(function () {
                        if (thisIndex > recentlyClickedIndex) {
                            return $(this).closest(options.itemSel).index() >= recentlyClickedIndex && $(this).closest(options.itemSel).index() <= thisIndex;
                        } else if (recentlyClickedIndex > thisIndex) {
                            return $(this).closest(options.itemSel).index() >= thisIndex && $(this).closest(options.itemSel).index() <= recentlyClickedIndex;
                        }
                    });
                    if (labels.filter(function () { return $(this).data('clicked') === true; }).length) {
                        filteredLabels.closest(options.itemSel).find(options.inputSel).prop('checked', true).change();
                        labels.data('clicked', false).data('unclicked', false);
                        thisLabel.data('clicked', true);
                        e.preventDefault();
                    } else if (labels.filter(function () { return $(this).data('unclicked') === true; }).length) {
                        filteredLabels.closest(options.itemSel).find(options.inputSel).prop('checked', false).change();
                        labels.data('clicked', false).data('unclicked', false);
                        thisLabel.data('unclicked', true);
                        e.preventDefault();
                    } else {
                        labels.data('clicked', false).data('unclicked', false);
                        if (thisInput.is(':checked')) {
                            thisLabel.data('unclicked', true);
                        } else {
                            thisLabel.data('clicked', true);
                        }
                    }
                } else {
                    labels.data('clicked', false).data('unclicked', false);
                    if (thisInput.is(':checked')) {
                        thisLabel.data('unclicked', true);
                    } else {
                        thisLabel.data('clicked', true);
                    }
                }
            });

            // include button action
            bulkInclude.click(function (e) {
                var selectedItems = availableList.find(options.itemSel + ' ' + options.inputSel + ':checked:visible');
                selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(includedList);
                context.multiselect("updateBulkSel", availableList.closest('.itemlist').find(options.bulkSel), availableList);
                context.multiselect("updateBulkSel", includedList.closest('.itemlist').find(options.bulkSel), includedList);
                e.preventDefault();
            });

            // exclude button action
            bulkExclude.click(function (e) {
                var selectedItems = includedList.find(options.itemSel + ' ' + options.inputSel + ':checked:visible');
                selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(availableList);
                filterLists.find(options.filterSel + ':checked').prop('checked', false).change();
                context.multiselect("updateBulkSel", availableList.closest('.itemlist').find(options.bulkSel), availableList);
                context.multiselect("updateBulkSel", includedList.closest('.itemlist').find(options.bulkSel), includedList);
                e.preventDefault();
            });

            form.submit(function (e) {
                var name = includedList.data('name');
                includedList.find(options.inputSel).each(function () {
                    var id = $(this).attr('value'),
                        hiddenInput = ich.filtered_multiselect_input({
                            id: id,
                            name: name
                        });
                    includedList.append(hiddenInput);
                });
            });

            // Sorting requires jQuery Element Sorter plugin ( http://plugins.jquery.com/project/ElementSort )
            headers.click(function (e) {
                var thisItemContainer = $(this).closest('section').find(options.itemListSel),
                    sortByClass = $(this).data('sort'),
                    direction;

                if ($(this).hasClass('asc') || $(this).hasClass('desc')) {
                    $(this).toggleClass('asc desc');
                } else {
                    $(this).addClass('asc');
                }
                $(this).closest('.listordering').find('.sortlink').not($(this)).removeClass('asc desc');
                if ($(this).hasClass('asc')) {
                    direction = 'asc';
                }
                if ($(this).hasClass('desc')) {
                    direction = 'desc';
                }
                thisItemContainer.sort({
                    sortOn: '.' + sortByClass,
                    direction: direction
                });
                $(this).blur();
                e.preventDefault();
            });

            // Bulk-select
            bulkSelects.change(function (e) {
                var thisSelect = $(this),
                    items = thisSelect.closest('.itemlist').find(options.itemSel + ' ' + options.inputSel + ':visible');

                if (thisSelect.is(':checked')) {
                    items.prop('checked', true).change();
                } else {
                    items.prop('checked', false).change();
                }
            });

            // Update bulk-select status when items are selected/unselected
            context.on('change', options.itemSel + ' ' + options.inputSel, function (e) {
                var thisList = $(this).closest('.itemlist'),
                    thisSelect = thisList.find(options.bulkSel);
                context.multiselect("updateBulkSel", thisSelect, thisList);
            });

            return this;
        },

        // populates the given list with values returned from the query.
        // always append here as it could be used for pagination.  Empty the list
        // prior to calling this function, when needed.
        populateList: function (
            list,
            ajax_url,
            ich_template,
            useshowmoreCallback) {

            list.loadingOverlay();
            current_xhrs.include = $.ajax({
                url: ajax_url,
                success: function (response) {
                    list.loadingOverlay("remove");
                    cache[ajax_url] = ich_template({items: response.objects});
                    list.append(cache[ajax_url]);
                    if (useshowmoreCallback) {
                        $(".multiselect").multiselect("updateshowmore",
                            response.meta, ich_template);
                    }
                },
                error: function (response) {
                    console.error(response);
                },
                always: function () {
                    list.loadingOverlay("remove");
                    delete current_xhrs.include;
                }
            });
        },

        // start from scratch by emptying both lists and populating them both
        // fresh at the beginning of pagination.  But there may be filters checked,
        // so honor that.
        populateBothLists: function (
                availableUrl,
                includedUrl,
                ich_template,
                filter_type_map) {

            var options = $.extend({}, msDefaults),
                context = $(this),
                ms = $(".multiselect"),
                availableList = context.find(
                    options.availableSel + ' ' + options.itemListSel),
                includedList = context.find(
                    options.includedSel + ' ' + options.itemListSel),
                filtered_avail_url = ms.multiselect("filterUrl",
                    availableUrl, filter_type_map);

            // if there are currently any ajax fetches for items, abort them
            // so we can do this new one.
            if (current_xhrs.include) {
                current_xhrs.include.abort();
            }
            if (current_xhrs.available) {
                current_xhrs.available.abort();
            }
            includedList.html("");
            if (includedUrl) {
                ms.multiselect("populateList",
                    includedList,
                    includedUrl,
                    ich_template,
                    false
                );
            }

            availableList.html("");
            $(options.availableSel).data(
                options.availableAjaxReplace,
                filtered_avail_url.toString());
            ms.multiselect("populateList",
                availableList,
                // the available list may already be filtered.  So honor those
                // filters.
                filtered_avail_url,
                ich_template,
                true);
        },

        updateBulkSel: function (select, list) {
            var options = $.extend({}, msDefaults),
                visibleNum = list.find(options.itemSel + ' ' +
                                           options.inputSel + ':visible').length,
                checkedNum = list.find(options.itemSel + ' ' +
                                           options.inputSel + ':visible:checked').length;
            if (checkedNum && checkedNum === visibleNum) {
                select.prop('checked', true);
            } else {
                select.prop('checked', false);
            }
        },


        addFilterHandlers: function addFilterEvents(filter_type_map, ich_template) {
            var options = $.extend({}, msDefaults),
                context = $(this),
                availableList = context.find(options.availableSel + ' ' +
                                                 options.itemListSel),
                filterLists = context.find(options.availableSel + ' ' +
                                               options.filterListSel);

            // add change handlers to all the checkboxes in the filter groups
            filterLists.find(options.filterSel).change(
                function filterChangeHandler() {
                    context.multiselect("filterItemsAjax",
                        filter_type_map,
                        ich_template);
                    context.multiselect("updateBulkSel",
                        availableList.closest('.itemlist').find(
                            options.bulkSel), availableList);
                });

        },

        filterItemsAjax: function filterItemsAjax(filter_type_map, ich_template) {
            var options = $.extend({}, msDefaults),
                context = $(this),
                availableList = context.find(options.availableSel + ' ' +
                    options.itemListSel),
                url_str = $(options.availableSel).data(
                    options.availableAjaxReplace),
                ajax_url = this.multiselect("filterUrl",
                    new URI(url_str),
                    filter_type_map);

            // remove the offset, if there is one, initial filtering
            // won't use an offset
            ajax_url.removeQuery("offset");

            availableList.html("");
            this.multiselect("populateList",
                availableList,
                ajax_url.toString(),
                ich_template, true
            );

        },

    // if the set of fetched available items is not all that is truly available,
        // then let the user fetch more if they would like.
        updateshowmore: function (meta, ich_template) {
            var options = $.extend({}, msDefaults),
                context = $(this),
                availableList = context.find(options.availableSel + ' ' +
                    options.itemListSel),
                show_count = meta.limit + meta.offset,
                more_count = meta.total_count - show_count,
                status = "Showing " + show_count + " of " +
                    meta.total_count + " available items",
                itemcount = $(".itemcount"),
                showmore = $(".showmore"),
                showmorebutton = $(".showmorebutton");

            if (more_count > 0) {
                showmore.removeClass("hiddenfield");
                itemcount.html(status);
                itemcount.data("next", meta.next);
                showmorebutton.unbind("click");
                showmorebutton.click(function () {
                    $(".multiselect").multiselect("populateList",
                        availableList,
                        meta.next,
                        ich_template,
                        true);
                });
            }
            else {
                showmore.addClass("hiddenfield");
            }
        },

        filterUrl: function (ajax_url, filter_type_map) {
            var options = $.extend({}, msDefaults),
                context = $(this),
                filterLists = context.find(options.availableSel + ' ' +
                    options.filterListSel);

            // remove all the filter keys so they can be reset with current values
            // we can't just clear the querystring because there may be pagination
            // and limits, and other queries we want to keep.
            for (var key in filter_type_map) {
                if (filter_type_map.hasOwnProperty(key)) {
                    ajax_url.removeQuery(filter_type_map[key]);
                }
            }

            // add filters for all checked items
            filterLists.find(options.filterSel + ':checked').each(function () {
                var type = $(this).data('name'),
                    filter = $(this).closest('.filter-item').find(".check").val();

                ajax_url.addQuery(filter_type_map[type], filter);

            });

            return ajax_url;
        }
    };

    /* Setup plugin defaults */
    var msDefaults = {
        filterListSel: '.visual .filter-group',
        filterSel: 'input[type="checkbox"]',
        availableSel: '.multiunselected',
        includedSel: '.multiselected',
        availableAjaxReplace: "ajax-replace",
        itemSel: '.selectitem',
        itemListSel: '.select',
        labelSel: '.bulk-type',
        inputSel: '.bulk-value',
        bulkIncludeSel: '.action-include',
        bulkExcludeSel: '.action-exclude',
        headerSel: '.listordering .sortlink',
        formSel: '.manage-form',
        bulkSel: '.listordering .bybulk-value'
    };

    $.fn.multiselect = function (method) {

        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' +  method + ' does not exist on jQuery.tooltip');
        }

    };

})(jQuery);