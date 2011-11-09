/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, ich */

/**
 * jQuery Multiselect Widget 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
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
            items,

            filterItems = function () {
                items = availableList.find(options.itemSel);
                items.each(function () {
                    var thisItem = $(this),
                        excludeThisItem = false;
                    filterLists.find(options.filterSel + ':checked').each(function () {
                        var type = $(this).data('name'),
                            filter = $(this).siblings('label').text().toLowerCase();

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
            var tagName = $(this).text(),
                suggestion = ich.autocomplete_suggestion({
                    suggestions: true,
                    id: tagName,
                    type: 'tag',
                    name: tagName,
                    typedText: tagName
                });
            suggestion.appendTo(context.find(options.availableSel + ' .selectsearch .suggest')).find('a').click();
            return false;
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
                    filteredLabels.closest(options.itemSel).find(options.inputSel).prop('checked', true);
                    labels.data('clicked', false).data('unclicked', false);
                    thisLabel.data('clicked', true);
                    e.preventDefault();
                } else if (labels.filter(function () { return $(this).data('unclicked') === true; }).length) {
                    filteredLabels.closest(options.itemSel).find(options.inputSel).prop('checked', false);
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
            e.preventDefault();
            var selectedItems = availableList.find(options.itemSel + ' ' + options.inputSel + ':checked');
            selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(includedList);
        });

        bulkExclude.click(function (e) {
            e.preventDefault();
            var selectedItems = includedList.find(options.itemSel + ' ' + options.inputSel + ':checked');
            selectedItems.prop('checked', false).closest(options.itemSel).detach().prependTo(availableList);
            filterLists.find(options.filterSel + ':checked').prop('checked', false).change();
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
                sortByClass = $(this).parent().attr('class').substring(2),
                direction;

            if ($(this).hasClass('asc') || $(this).hasClass('desc')) {
                $(this).toggleClass('asc desc');
                $(this).parent().siblings().find('a').removeClass('asc desc');
            } else {
                $(this).addClass('asc');
                $(this).parent().siblings().find('a').removeClass('asc desc');
            }
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
            return false;
        });
    };

    /* Setup plugin defaults */
    $.fn.multiselect.defaults = {
        filterListSel: '.groups .filter-group',
        filterSel: 'input[type="checkbox"]',
        availableSel: '.multiunselected',
        includedSel: '.multiselected',
        itemSel: '.selectitem',
        itemListSel: '.select',
        labelSel: '.bulkselect',
        inputSel: '.item-input',
        bulkIncludeSel: '.multiunselected .listordering .action-include',
        bulkExcludeSel: '.multiselected .listordering .action-exclude',
        headerSel: '.listordering li[class^="by"] a',
        formSel: '#suite-form'
    };

}(jQuery));