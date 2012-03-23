/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, ich */

/**
 * jQuery Multiselect Widget 0.2
 *
 * Copyright (c) 2012, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    $.fn.multiselect = function (opts) {
        var options = $.extend({}, $.fn.multiselect.defaults, opts),
            context = $(this),
            filterLists = context.find(options.availableSel + ' ' + options.filterListSel),
            availableList = context.find(options.availableSel + ' ' + options.itemListSel),
            includedList = context.find(options.includedSel + ' ' + options.itemListSel),
            bulkInclude = context.find(options.bulkIncludeSel),
            bulkExclude = context.find(options.bulkExcludeSel),
            form = $(options.formSel),
            headers = context.find(options.headerSel),
            bulkSelects = context.find(options.bulkSel),
            items,

            updateBulkSel = function (select, list) {
                if (list.find(options.itemSel + ' ' + options.inputSel + ':checked').length && list.find(options.itemSel + ' ' + options.inputSel + ':checked').length === list.find(options.itemSel + ' ' + options.inputSel).length) {
                    select.prop('checked', true);
                } else {
                    select.prop('checked', false);
                }
            },

            filterItems = function () {
                items = availableList.find(options.itemSel);
                items.each(function () {
                    var thisItem = $(this),
                        excludeThisItem = false;
                    filterLists.find(options.filterSel + ':checked').each(function () {
                        var type = $(this).data('name'),
                            filter = $(this).closest('.filter-item').find('.onoffswitch').text().toLowerCase();

                        if (type === 'name') {
                            if (thisItem.find('.title').text().toLowerCase().indexOf(filter) === -1) {
                                excludeThisItem = true;
                            }
                        } else if (type === 'status') {
                            if (thisItem.find('.' + type).children('span').text().toLowerCase() !== filter) {
                                excludeThisItem = true;
                            }
                        } else if (type === 'tag') {
                            if (!(thisItem.find('.tags a').filter(function () { return $(this).text().toLowerCase() === filter; }).length)) {
                                excludeThisItem = true;
                            }
                        } else if (type === 'author') {
                            if (thisItem.find('.' + type).children('span').text().toLowerCase() !== filter) {
                                excludeThisItem = true;
                            }
                        } else {
                            if (thisItem.find('.' + type).text().toLowerCase() !== filter) {
                                excludeThisItem = true;
                            }
                        }
                    });

                    if (excludeThisItem) {
                        thisItem.hide();
                    } else {
                        thisItem.show();
                    }
                });
            };

        filterLists.on('change', options.filterSel, function () {
            filterItems();
        });

        availableList.add(includedList).on('click', options.itemSel + ' .tags a', function (e) {
            var tagName = $(this).text();
            filterLists.filter('[data-name="tag"]').find('.onoffswitch').filter(function () {
                return $(this).text().toLowerCase() === tagName;
            }).closest('.filter-item').find(options.filterSel).prop('checked', true).change();
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
                ui.item.closest(options.availableSel).find(options.filterListSel + ' ' + options.filterSel + ':checked').prop('checked', false).change();
                ui.item.find(options.inputSel).prop('checked', false);
                updateBulkSel(availableList.closest('.itemlist').find(options.bulkSel), availableList);
                updateBulkSel(includedList.closest('.itemlist').find(options.bulkSel), includedList);
            }
        });

        context.on('click', options.itemListSel + ' ' + options.labelSel, function (e) {
            var thisLabel = $(this),
                thisInput = thisLabel.closest(options.itemSel).find(options.inputSel),
                labels = thisLabel.closest(options.itemListSel).find(options.labelSel),
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

        bulkInclude.click(function (e) {
            var selectedItems = availableList.find(options.itemSel + ' ' + options.inputSel + ':checked');
            selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(includedList);
            updateBulkSel(availableList.closest('.itemlist').find(options.bulkSel), availableList);
            updateBulkSel(includedList.closest('.itemlist').find(options.bulkSel), includedList);
            e.preventDefault();
        });

        bulkExclude.click(function (e) {
            var selectedItems = includedList.find(options.itemSel + ' ' + options.inputSel + ':checked');
            selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(availableList);
            filterLists.find(options.filterSel + ':checked').prop('checked', false).change();
            updateBulkSel(availableList.closest('.itemlist').find(options.bulkSel), availableList);
            updateBulkSel(includedList.closest('.itemlist').find(options.bulkSel), includedList);
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
                items = thisSelect.closest('.itemlist').find(options.itemSel + ' ' + options.inputSel);

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
            updateBulkSel(thisSelect, thisList);
        });
    };

    /* Setup plugin defaults */
    $.fn.multiselect.defaults = {
        filterListSel: '.visual .filter-group',
        filterSel: 'input[type="checkbox"]',
        availableSel: '.multiunselected',
        includedSel: '.multiselected',
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

}(jQuery));