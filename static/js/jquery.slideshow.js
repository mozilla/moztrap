/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery */

/**
 * jQuery slideshow 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    $.fn.slideshow = function (opts) {
        var options = $.extend({}, $.fn.slideshow.defaults, opts),
            hash,
            context = $(this),
            slides = context.find(options.slidesSelector),
            slideLinks = context.find(options.slideLinksSelector),
            showSlide = function (slide) {
                var thisLink = slideLinks.filter('a[href="#' + $(slide).attr('id') + '"]');
                $(slide).addClass('active-slide').removeClass('inactive-slide');
                $(slide).siblings(slidesSelector).removeClass('active-slide').addClass('inactive-slide').fadeOut('fast', function () {
                    $(slide).fadeIn('fast', callback);
                });
                slideLinks.removeClass('active');
                thisLink.addClass('active');
            };

        slideLinks.click(function (e) {
            e.preventDefault();
            showSlide($(this).attr('href'));
            $(this).blur();
        });

        if (window.location.hash) {
            hash = window.location.hash.substring(1);
            if (slides.filter('[id^="' + hash + '"]').length) {
                showSlide(slides.filter('[id^="' + hash + '"]'));
            }
        }
    };

    /* Setup plugin defaults */
    $.fn.slideshow.defaults = {
        slidesSelector: '.slide',           // Selector for slides
        slideLinksSelector: '.slideLink',   // Selector for links to slides
        callback: null,                     // Function to be called after each slide transition
    };
}(jQuery));