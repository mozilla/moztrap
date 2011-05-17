/**
 * jQuery html5finder 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
;(function($) {
    $.fn.html5finder = function(opts) {
        var options = $.extend({}, $.fn.html5finder.defaults, opts),
            context = this,
            section1 = context.find(options.section + '.' + options.section1class),
            section2 = context.find(options.section + '.' + options.section2class),
            section3 = context.find(options.section + '.' + options.section3class),
            section4 = context.find(options.section + '.' + options.section4class),
            section5 = context.find(options.section + '.' + options.section5class),
            section1item = context.find(options.section1item + ':not(".selected")'),
            section2item = context.find(options.section2item + ':not(".selected")'),
            section3item = context.find(options.section3item + ':not(".selected")'),
            section4item = context.find(options.section4item + ':not(".selected")'),
            section5item = context.find(options.section5item + ':not(".selected")'),
            headers = context.find(options.header).each(function() {
                var scrollbarWidth = $(this).closest(options.section).css('width') - $(this).children('li').css('width');
                $(this).css('right', scrollbarWidth);
            }),
            addSelectedClass = function() {
                context.find(options.selected).addClass('selected');
                context.find(options.notSelected).removeClass('selected');
            },
            expand = $(options.expand).hide();
        headers.find('a').click(function() {
            context.find(options.section).removeClass('focus');
            $(this).closest(options.section).addClass('focus');
            $(this).blur();
        });
        section1item.live('click', function() {
            var itemName = $(this).data('id'),
                fakeAjaxCall = function(itemName, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_01" data-product="' + itemName + '" data-cycle="01">' +
                            '<label for="' + itemName + '_cycle_name_01">' +
                                '<span class="completion" data-perc="75">75%</span>' +
                                '<span class="title">' + itemName + ' cycle name 01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_02" data-product="' + itemName + '" data-cycle="02">' +
                            '<label for="' + itemName + '_cycle_name_02">' +
                                '<span class="completion" data-perc="100">100%</span>' +
                                '<span class="title">' + itemName + ' cycle name 02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_03" data-product="' + itemName + '" data-cycle="03">' +
                            '<label for="' + itemName + '_cycle_name_03">' +
                                '<span class="completion" data-perc="25">25%</span>' +
                                '<span class="title">' + itemName + ' cycle name 03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_04" data-product="' + itemName + '" data-cycle="04">' +
                            '<label for="' + itemName + '_cycle_name_04">' +
                                '<span class="completion" data-perc="17">17%</span>' +
                                '<span class="title">' + itemName + ' cycle name 04</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_05" data-product="' + itemName + '" data-cycle="05">' +
                            '<label for="' + itemName + '_cycle_name_05">' +
                                '<span class="completion" data-perc="50">50%</span>' +
                                '<span class="title">' + itemName + ' cycle name 05</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_06" data-product="' + itemName + '" data-cycle="06">' +
                            '<label for="' + itemName + '_cycle_name_06">' +
                                '<span class="completion" data-perc="83">83%</span>' +
                                '<span class="title">' + itemName + ' cycle name 06</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    if (itemName === 'tcm') {
                        var response =
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_01" data-product="' + itemName + '" data-cycle="01">' +
                                '<label for="' + itemName + '_cycle_name_01">' +
                                    '<span class="completion" data-perc="75">75%</span>' +
                                    '<span class="title">' + itemName + ' cycle name 01</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_02" data-product="' + itemName + '" data-cycle="02">' +
                                '<label for="' + itemName + '_cycle_name_02">' +
                                    '<span class="completion" data-perc="100">100%</span>' +
                                    '<span class="title">' + itemName + ' cycle name 02</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + itemName + '_cycle_name_03" data-product="' + itemName + '" data-cycle="03">' +
                                '<label for="' + itemName + '_cycle_name_03">' +
                                    '<span class="completion" data-perc="25">25%</span>' +
                                    '<span class="title">' + itemName + ' cycle name 03</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>';
                    }
                    function callbackfn() { callback(response); }
                    window.setTimeout(callbackfn, 300);
                };
            fakeAjaxCall(
                itemName,
                function(data) {
                    section2.children('ul').html(data);
                    $('.loadingCSS').detach();
                    $('.loading').removeClass("loading");
                }
            );
            section1.removeClass('focus');
            section2.addClass('focus').children('ul').empty();
            section3.removeClass('focus').children('ul').empty();
            section4.removeClass('focus').children('ul').empty();
            section5.removeClass('focus').children('ul').empty();
            expand.slideUp();
            addSelectedClass();
        });
        section2item.live('click', function() {
            var productName = $(this).data('product'),
                cycleNumber = $(this).data('cycle'),
                fakeAjaxCall = function(productName, cycleNumber, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_01">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_01">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_02">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_02">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_03">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_03">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_04">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_04">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-04</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_05">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_05">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-05</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_06">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_06">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-06</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    if (cycleNumber === 1) {
                        var response =
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_01">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_01">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-01</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_02">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_02">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-02</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_03">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_03">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-03</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_04">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_04">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-04</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>';
                    }
                    function callbackfn() { callback(response); }
                    window.setTimeout(callbackfn, 300);
                };
            fakeAjaxCall(
                productName,
                cycleNumber,
                function(data) {
                    section3.children('ul').html(data);
                    $('.loadingCSS').detach();
                    $('.loading').removeClass("loading");
                }
            );
            section1.removeClass('focus');
            section2.removeClass('focus');
            section3.addClass('focus').children('ul').empty();
            section4.removeClass('focus').children('ul').empty();
            section5.removeClass('focus').children('ul').empty();
            expand.slideUp();
            addSelectedClass();
        });
        section3item.live('click', function() {
            addSelectedClass();
        });
        $(options.expandTrigger).live('click', function() {
            expand.slideDown();
        });
        $('input.selected').live('click', function() {
            $(this).closest(options.section).addClass('focus').siblings(options.section).removeClass('focus');
            $(this).closest(options.section).next(options.section).find('input:checked').removeClass('selected').removeAttr('checked');
            $(this).closest(options.section).next(options.section).nextAll(options.section).children('ul').empty();
        });
        $('input.selected:not("' + options.expandTrigger + '")').live('click', function() {
            expand.slideUp();
        });
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
            addLoading(options.section1item + ':not(".selected"), ' + options.section2item + ':not(".selected")', options.section);
        }
    };

    /* Setup plugin defaults */
    $.fn.html5finder.defaults = {
        expand: null,
        expandTrigger: null,
        loading: false,
        horizontalScroll: false,
        selected: 'input:checked',
        notSelected: 'input:not(:checked)',
        header: 'header',
        section: 'section',
        section1class: 'section1',
        section1item: 'input[name="section1"]',
        section2class: 'section2',
        section2item: 'input[name="section2"]',
        section3class: 'section3',
        section3item: 'input[name="section3"]',
        section4class: 'section4',
        section4item: 'input[name="section4"]',
        section5class: 'section5',
        section5item: 'input[name="section5"]'
    };
})(jQuery);