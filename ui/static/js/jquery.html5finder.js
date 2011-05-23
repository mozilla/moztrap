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
                var container = $(this).closest(options.sectionSelector);
                // Last-child section only receives focus on-click by default
                if (container.is(':last-child')) {
                    addSelectedClass();
                } else {
                    var response;
                    if (container.index() === 0) {
                        var itemName = $(this).data('id'),
                            response =
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_01" data-product="' + itemName + '" data-cycle="01">' +
                                    '<label for="' + itemName + '_cycle_name_01">' +
                                        '<span class="completion" data-perc="75">75%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 01 runs">open all the ' + itemName + ' cycle name 01 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_02" data-product="' + itemName + '" data-cycle="02">' +
                                    '<label for="' + itemName + '_cycle_name_02">' +
                                        '<span class="completion" data-perc="100">100%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 02 runs">open all the ' + itemName + ' cycle name 02 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_03" data-product="' + itemName + '" data-cycle="03">' +
                                    '<label for="' + itemName + '_cycle_name_03">' +
                                        '<span class="completion" data-perc="25">25%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 03 runs">open all the ' + itemName + ' cycle name 03 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_04" data-product="' + itemName + '" data-cycle="04">' +
                                    '<label for="' + itemName + '_cycle_name_04">' +
                                        '<span class="completion" data-perc="17">17%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 04</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 04 runs">open all the ' + itemName + ' cycle name 04 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_05" data-product="' + itemName + '" data-cycle="05">' +
                                    '<label for="' + itemName + '_cycle_name_05">' +
                                        '<span class="completion" data-perc="50">50%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 05</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 05 runs">open all the ' + itemName + ' cycle name 05 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_06" data-product="' + itemName + '" data-cycle="06">' +
                                    '<label for="' + itemName + '_cycle_name_06">' +
                                        '<span class="completion" data-perc="83">83%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 06</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 06 runs">open all the ' + itemName + ' cycle name 06 runs</a>' +
                                '</li>';
                        if (itemName === 'tcm') {
                            response =
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_01" data-product="' + itemName + '" data-cycle="01">' +
                                    '<label for="' + itemName + '_cycle_name_01">' +
                                        '<span class="completion" data-perc="75">75%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 01 runs">open all the ' + itemName + ' cycle name 01 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_02" data-product="' + itemName + '" data-cycle="02">' +
                                    '<label for="' + itemName + '_cycle_name_02">' +
                                        '<span class="completion" data-perc="100">100%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 02 runs">open all the ' + itemName + ' cycle name 02 runs</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_03" data-product="' + itemName + '" data-cycle="03">' +
                                    '<label for="' + itemName + '_cycle_name_03">' +
                                        '<span class="completion" data-perc="25">25%</span>' +
                                        '<span class="title">' + itemName + ' cycle name 03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' cycle name 03 runs">open all the ' + itemName + ' cycle name 03 runs</a>' +
                                '</li>';
                        }
                    }
                    if (container.index() === 1) {
                        var itemName = $(this).data('product'),
                            cycleNumber = $(this).data('cycle'),
                            response =
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_01" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_01">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-01 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-01 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_02" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_02">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-02 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-02 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_03" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_03">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-03 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-03 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_04" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_04">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-04</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-04 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-04 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_05" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_05">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-05</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-05 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-05 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_06" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_06">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-06</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-06 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-06 cases</a>' +
                                '</li>';
                        if (cycleNumber === 1) {
                            response =
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_01" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_01">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-01 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-01 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_02" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_02">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-02 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-02 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_03" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_03">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-03 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-03 cases</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="run" value="" id="' + itemName + '_run_0' + cycleNumber + '_04" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_run_0' + cycleNumber + '_04">' +
                                        '<span class="title">' + itemName + ' run 0' + cycleNumber + '-04</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' run 0' + cycleNumber + '-04 cases">open all the ' + itemName + ' run 0' + cycleNumber + '-04 cases</a>' +
                                '</li>';
                        }
                    }
                    if (container.index() === 2) {
                        var itemName = $(this).data('product'),
                            response =
                                '<li>' +
                                    '<input type="radio" name="case" value="" id="' + itemName + '_case_01" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_case_01">' +
                                        '<span class="title">' + itemName + ' case 01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' case 01 results">open all the ' + itemName + ' case 01 results</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="case" value="" id="' + itemName + '_case_02" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_case_02">' +
                                        '<span class="title">' + itemName + ' case 02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' case 02 results">open all the ' + itemName + ' case 02 results</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="case" value="" id="' + itemName + '_case_03" data-product="' + itemName + '">' +
                                    '<label for="' + itemName + '_case_03">' +
                                        '<span class="title">' + itemName + ' case 03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open all the ' + itemName + ' case 03 results">open all the ' + itemName + ' case 03 results</a>' +
                                '</li>';
                    }
                    if (container.index() === 3) {
                        var itemName = $(this).data('product'),
                            response =
                                '<li>' +
                                    '<input type="radio" name="result" value="" id="' + itemName + '_result_01">' +
                                    '<label for="' + itemName + '_result_01">' +
                                        '<span class="title">' + itemName + ' result 01</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open this result">open this result</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="result" value="" id="' + itemName + '_result_02">' +
                                    '<label for="' + itemName + '_result_02">' +
                                        '<span class="title">' + itemName + ' result 02</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open this result">open this result</a>' +
                                '</li>' +
                                '<li>' +
                                    '<input type="radio" name="result" value="" id="' + itemName + '_result_03">' +
                                    '<label for="' + itemName + '_result_03">' +
                                        '<span class="title">' + itemName + ' result 03</span>' +
                                        '<time class="start">01/07/2011</time>' +
                                        '<time class="end">11/10/2011</time>' +
                                    '</label>' +
                                    '<a href="#" class="open" title="open this result">open this result</a>' +
                                '</li>';
                    }
                        // This function mimics an ajax call with a delay of 300ms
                        fakeAjaxCall = function(callback) {
                            function callbackfn() { callback(response); }
                            window.setTimeout(callbackfn, 300);
                        };
                    // Add returned data to the next section
                    fakeAjaxCall(
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
                }
            });
        }

        // Clicking an already-selected input only scrolls (if applicable), adds focus, and empties subsequent sections
        context.find('.selected').live('click', function() {
            $(this).closest(options.sectionSelector).addClass('focus').siblings(options.sectionSelector).removeClass('focus');
            $(this).closest(options.sectionSelector).next(options.sectionSelector).find('input:checked').removeClass('selected').removeAttr('checked');
            $(this).closest(options.sectionSelector).next(options.sectionSelector).nextAll(options.sectionSelector).children('ul').empty();
            horzScroll();
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
        ]
    };
})(jQuery);
