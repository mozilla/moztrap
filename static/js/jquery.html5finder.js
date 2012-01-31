/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery */

/**
 * jQuery html5finder 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    $.fn.html5finder = function (opts) {
        var options = $.extend({}, $.fn.html5finder.defaults, opts),
            context = $(this),
            sections = context.find(options.sectionSelector),

            // Set the width of each section to account for vertical scroll-bars
            headers = context.find(options.headerSelector).each(function () {
                var scrollbarWidth = $(this).closest(options.sectionSelector).css('width') - $(this).children('li').css('width');
                $(this).css('right', scrollbarWidth);
            }),

            // We want to be able to treat already-selected items differently
            markSelected = function () {
                context.find(options.selected).data('selected', true);
                context.find(options.notSelected).data('selected', false);
            },

            // Define the function for horizontal scrolling:
            // Scrolls to the previous section (so that the active section is centered)
            horzScroll = function () {
                if (options.horizontalScroll === true) {
                    var scrollTarget,
                        currentScroll = context.find(options.scrollContainer).scrollLeft();
                    if (context.find(options.sectionSelector + '.focus').is(':first-child')) {
                        scrollTarget = 0;
                    } else {
                        scrollTarget = currentScroll + context.find(options.sectionSelector + '.focus').prev(options.sectionSelector).position().left;
                    }
                    context.find(options.scrollContainer).animate({scrollLeft: scrollTarget});
                }
            },

            itemClick = function () {
                context.on('click', options.itemSelector, function () {
                    var thisItem = $(this),
                        container = thisItem.closest(options.sectionSelector),
                        ajaxUrl = thisItem.data('sub-url'),
                        target = container.next(options.sectionSelector);
                    // Clicking an already-selected input only scrolls (if applicable), adds focus, and empties subsequent sections
                    if (thisItem.data('selected') === true && !container.hasClass('focus')) {
                        container.addClass('focus').siblings(options.sectionSelector).removeClass('focus');
                        container.next(options.sectionSelector).find('input:checked').removeAttr('checked').data('selected', false);
                        container.next(options.sectionSelector).nextAll(options.sectionSelector).children('ul').empty();
                        horzScroll();
                        if (!container.is(':last-child') && options.callback) {
                            options.callback();
                        }
                    } else {
                        // Last-child section only receives focus on-click by default
                        if (container.is(':last-child')) {
                            if (options.lastChildCallback) {
                                options.lastChildCallback(this);
                            }
                        } else {
                            // Add a loading screen while waiting for the Ajax call to return data
                            if (options.loading === true) {
                                target.loadingOverlay();
                            }
                            // Add returned data to the next section
                            $.get(
                                ajaxUrl,
                                function (response) {
                                    container.next(options.sectionSelector).children(options.sectionContentSelector).html(response.html);
                                    container.next(options.sectionSelector).loadingOverlay('remove');
                                }
                            );
                            container.removeClass('focus').prevAll(options.sectionSelector).removeClass('focus');
                            container.next(options.sectionSelector).addClass('focus').children('ul').empty();
                            container.next(options.sectionSelector).nextAll(options.sectionSelector).removeClass('focus').children('ul').empty();
                            horzScroll();
                            if (options.callback) {
                                options.callback();
                            }
                        }
                        markSelected();
                    }
                });
            };

        context.find('.finder').data('cols', options.numberCols);
        markSelected();

        // Enable headers to engage section focus, and sort column if section already has focus
        // Sorting requires jQuery Element Sorter plugin ( http://plugins.jquery.com/project/ElementSort )
        headers.on('click', options.sortLinkSelector, function (e) {
            var container = $(this).closest(options.sectionSelector),
                list = container.find(options.sectionContentSelector),
                selectorClass = $(this).parent().data('sort-by'),
                type = $(this).parent().data('sort-type'),
                sortOnData = $(this).parent().data('sort-on-data-attr'),
                direction;
            if (container.hasClass('focus')) {
                $(this).parent().siblings().find(options.sortLinkSelector).removeClass('asc desc');
                if ($(this).hasClass('asc') || $(this).hasClass('desc')) {
                    $(this).toggleClass('asc desc');
                } else {
                    $(this).addClass('asc');
                }
                if ($(this).hasClass('asc')) {
                    direction = 'asc';
                } else if ($(this).hasClass('desc')) {
                    direction = 'desc';
                }
                list.sort({
                    sortOn: '.' + selectorClass,
                    direction: direction,
                    sortType: type,
                    sortOnDataAttr: sortOnData
                });
            } else {
                context.find(options.sectionSelector).removeClass('focus');
                container.addClass('focus');
                horzScroll();
            }
            $(this).blur();
            e.preventDefault();
        });

        itemClick();
    };

    /* Setup plugin defaults */
    $.fn.html5finder.defaults = {
        loading: false,                     // If true, adds a loading overlay while waiting for Ajax response
        horizontalScroll: false,            // If true, automatically scrolls to center the active section
        scrollContainer: null,              // The container (window) to be automatically scrolled
        scrollSpeed: 500,                   // Speed of the scroll (in ms)
        numberCols: 3,                      // Number of sections (columns)
        selected: 'input:checked',          // A selected element
        notSelected: 'input:not(:checked)', // An unselected element
        headerSelector: 'header',           // Section headers
        sectionSelector: 'section',         // Sections
        sectionContentSelector: 'ul',       // Content to be replaced by Ajax function
        itemSelector: '.finderinput',       // Selector for items in each section
        callback: null,                     // Callback function, currently runs after input in any section (except lastChild) is selected
        lastChildCallback: null,            // Callback function, currently runs after input in last section is selected
        sortLinkSelector: '.sortlink'       // Selector for link (in header) to sort items in that column

    };
}(jQuery));