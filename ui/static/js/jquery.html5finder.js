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
            addSelectedClass = function() {
                context.find(options.selected).addClass('selected');
                context.find(options.notSelected).removeClass('selected');
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

        // Enable headers to engage section focus
        headers.find('a').click(function() {
            context.find(options.sectionSelector).removeClass('focus');
            $(this).closest(options.sectionSelector).addClass('focus');
            $(this).blur();
            horzScroll();
        });

        for (var i = 0; i < numberCols; i++) {
            context.find(options.sectionItemSelectors[i] + ':not(.selected)').live('click', function() {
                var container = $(this).closest(options.sectionSelector),
                    ajaxUrl = $(this).data("sub-url");
                // Last-child section only receives focus on-click by default
                if (container.is(':last-child')) {
                    addSelectedClass();
                    if (options.lastChildCallback) {
                        options.lastChildCallback(this);
                    }
                } else {
                    // Add returned data to the next section
                    $.get(
                        ajaxUrl,
                        function(data) {
                            container.next(options.sectionSelector).children(options.sectionContentSelector).html(data);
                            $('.loadingCSS').detach();
                            $('.loading').removeClass("loading");
                        }
                    );
                    container.removeClass('focus').prevAll(options.sectionSelector).removeClass('focus');
                    container.next(options.sectionSelector).addClass('focus').children('ul').empty();
                    container.next(options.sectionSelector).nextAll(options.sectionSelector).removeClass('focus').children('ul').empty();
                    horzScroll();
                    addSelectedClass();
                    if (options.callback) {
                        options.callback(this);
                    }
                }
            });
        }

        // Clicking an already-selected input only scrolls (if applicable), adds focus, and empties subsequent sections
        context.find('.selected').live('click', function() {
            var container = $(this).closest(options.sectionSelector);
            container.addClass('focus').siblings(options.sectionSelector).removeClass('focus');
            container.next(options.sectionSelector).find('input:checked').removeClass('selected').removeAttr('checked');
            container.next(options.sectionSelector).nextAll(options.sectionSelector).children('ul').empty();
            horzScroll();
            if (container.is(':last-child')) {
                if (options.lastChildCallback) {
                    options.lastChildCallback();
                }
            } else {
                if (options.callback) {
                    options.callback();
                }
            }
        });

        // Add a loading screen while waiting for the Ajax call to return data
        if (options.loading === true) {
            var addLoading = function(trigger, target) {
                $(trigger).live('click', function() {
                    var container = $(this).closest(target).next(target),
                        addLoadingCSS = function() {
                            var vertHeight = (parseInt(container.css('height'), 10) - parseInt(container.css('line-height'), 10)) / 2 + 'px',
                                style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                            $('head').append(style);
                        };
                    container.addClass('loading');
                    addLoadingCSS();
                });
            };
            for (var i = 0; i < numberCols; i++) {
                addLoading(options.sectionItemSelectors[i] + ':not(.selected)', options.sectionSelector);
            }
        }
    };

    /* Setup plugin defaults */
    $.fn.html5finder.defaults = {
        loading: false,                     // If true, adds a loading overlay while waiting for Ajax response
        horizontalScroll: false,            // If true, automatically scrolls to center the active section
                                                // [This requires the jquery.scrollTo plugin by default]
        scrollContainer: null,              // The container (window) to be automatically scrolled
        scrollSpeed: 500,                   // Speed of the scroll (in ms)
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
