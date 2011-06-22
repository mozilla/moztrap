/**
 * jQuery html5finder 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function($) {
    $.fn.html5finder = function(opts) {
        var options = $.extend({}, $.fn.html5finder.defaults, opts),
            context = $(this),
            numberCols = options.sectionClasses.length,
            sections = context.find(options.sectionSelector),

            // Set the width of each section to account for vertical scroll-bars
            headers = context.find(options.headerSelector).each(function() {
                var scrollbarWidth = $(this).closest(options.sectionSelector).css('width') - $(this).children('li').css('width');
                $(this).css('right', scrollbarWidth);
            }),

            // We want to be able to treat already-selected items differently
            markSelected = function() {
                context.find(options.selected).data('selected', true);
                context.find(options.notSelected).data('selected', false);
            },

            // Define the function for updating ellipses on long text
            updateEllipsis = function() {
                if (options.ellipsis === true) {
                    var target = context.find(options.sectionContentSelector + ' ' + options.ellipsisTarget);
                    target.each(function() {
                        if ($(this).data('originalText')) {
                            $(this).html($(this).data('originalText'));
                        }
                    });
                    $.doTimeout('updateEllipsis', 300, function(){
                        target.ellipsis(true, 250);
                    });
                }
            },

            // Define the function for horizontal scrolling (requires jquery.scrollTo plugin):
            // Scrolls to the previous section (so that the active section is centered)
            horzScroll = function() {
                if (options.horizontalScroll === true) {
                    var scrollTarget;
                    if (context.find(options.sectionSelector + '.focus').is(':first-child')) {
                        scrollTarget = context.find(options.sectionSelector + '.focus');
                    } else {
                        scrollTarget = context.find(options.sectionSelector + '.focus').prev(options.sectionSelector);
                    }
                    context.find(options.scrollContainer).scrollTo(scrollTarget, {duration: options.scrollSpeed, axis: 'x'});
                }
            };

        context.find('.finder').data('cols', numberCols);
        markSelected();
        updateEllipsis();

        // Enable headers to engage section focus, and sort column if section already has focus
        // Sorting requires jQuery Element Sorter plugin ( http://plugins.jquery.com/project/ElementSort )
        headers.find('a').live('click', function() {
            var container = $(this).closest(options.sectionSelector),
                list = container.find(options.sectionContentSelector),
                selectorClass = $(this).parent().attr('class').substring(2),
                type = $(this).parent().data('sort'),
                direction;
            if (container.hasClass('focus')) {
                if ($(this).hasClass('asc') || $(this).hasClass('desc')) {
                    $(this).toggleClass('asc').toggleClass('desc');
                    $(this).parent().siblings().find('a').removeClass('asc').removeClass('desc');
                } else {
                    $(this).addClass('asc');
                    $(this).parent().siblings().find('a').removeClass('asc').removeClass('desc');
                }
                if ($(this).hasClass('asc')) {
                    direction = 'asc';
                }
                if ($(this).hasClass('desc')) {
                    direction = 'desc';
                }
                if (type === 'number') {
                    selectorClass = selectorClass + ' .number';
                }
                if (type === 'date') {
                    list.sort({
                        sortOn: '.' + selectorClass,
                        direction: direction,
                        sortType: 'string'
                    });
                }
                list.sort({
                    sortOn: '.' + selectorClass,
                    direction: direction,
                    sortType: type
                });
            } else {
                context.find(options.sectionSelector).removeClass('focus');
                container.addClass('focus');
                updateEllipsis();
                horzScroll();
            }
            $(this).blur();
            return false;
        });

        for (var i = 0; i < numberCols; i++) {
            context.find(options.sectionItemSelectors[i]).live('click', function() {
                var container = $(this).closest(options.sectionSelector);
                // Clicking an already-selected input only scrolls (if applicable), adds focus, and empties subsequent sections
                if ($(this).data('selected') === true) {
                    container.addClass('focus').siblings(options.sectionSelector).removeClass('focus');
                    container.next(options.sectionSelector).find('input:checked').removeAttr('checked').data('selected', false);
                    container.next(options.sectionSelector).nextAll(options.sectionSelector).children('ul').empty();
                    horzScroll();
                    updateEllipsis();
                    if (!container.is(':last-child') && options.callback) {
                        options.callback();
                    }
                } else {
                    var ajaxUrl = $(this).data("sub-url");
                    // Last-child section only receives focus on-click by default
                    if (container.is(':last-child')) {
                        if (options.lastChildCallback) {
                            options.lastChildCallback(this);
                        }
                    } else {
                        // Add a loading screen while waiting for the Ajax call to return data
                        if (options.loading === true) {
                            var target = container.next(options.sectionSelector);
                            TCM.addLoading(target);
                        }
                        // Add returned data to the next section
                        $.get(
                            ajaxUrl,
                            function(data) {
                                container.next(options.sectionSelector).children(options.sectionContentSelector).html(data);
                                $('.overlay').detach();
                                $('.loading').removeClass('loading');
                                updateEllipsis();
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
        }
    };

    /* Setup plugin defaults */
    $.fn.html5finder.defaults = {
        loading: false,                     // If true, adds a loading overlay while waiting for Ajax response
        horizontalScroll: false,            // If true, automatically scrolls to center the active section
                                                // [This requires the jquery.scrollTo plugin by default]
        scrollContainer: null,              // The container (window) to be automatically scrolled
        scrollSpeed: 500,                   // Speed of the scroll (in ms)
        ellipsis: false,                    // If true, adds ellipsis to long text
                                                // [This requires the jquery.text-overflow.js plugin by default]
        ellipsisTarget: '.title',           // The target text to be shortened
        selected: 'input:checked',          // A selected element
        notSelected: 'input:not(:checked)', // An unselected element
        headerSelector: 'header',           // Section headers
        sectionSelector: 'section',         // Sections
        sectionContentSelector: 'ul',       // Content to be replaced by Ajax function
        sectionClasses: [                   // Classes for each section
            'section1',
            'section2',
            'section3'
        ],
        sectionItemSelectors: [             // Selectors for items in each section
            'input[name="section1"]',
            'input[name="section2"]',
            'input[name="section3"]'
        ],
        callback: null,                     // Callback function, currently runs after input in any section (except lastChild) is selected
        lastChildCallback: null             // Callback function, currently runs after input in last section is selected
    };
})(jQuery);
