/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery */

/**
 * A jQuery plugin to enable the text ellipsis in firefox.
 *
 * see http://yue.st/notes/code/js/ellipsis.en.html
 *
 * usage:
 *  $('.elementsNeedEllipsis').ellipsis();
 *  the elements should be block level ('display: block' or 'display: inline-block')
 *
 * I think you should take care of resize event by yourself,
 * just call $('.elem').ellipsis() again after element is resized.
 */
(function ($) {

    'use strict';

    $.fn.ellipsis = function () {
        $(this).css({'white-space': 'nowrap', 'overflow': 'hidden'});
        // if browser supports 'text-overflow' property, just use it
        if (document.documentElement.style.textOverflow !== undefined || document.documentElement.style.OTextOverflow !== undefined) {
            $(this).css({
                'text-overflow': 'ellipsis',
                '-o-text-overflow': 'ellipsis'
            });
        } else { // firefox does not support the text-overflow property, so...
            $(this).each(function () {
                var $el = $(this),
                    text,
                    w,
                    a,
                    b,
                    c,
                    $t;
                if (!$el.data('originalText')) { $el.data('originalText', $el.text()); } else { $el.text($el.data('originalText')); }
                text = $el.attr('text') || $el.text();
                w = $el.width();
                a = 0;
                b = text.length;
                c = b;
                $t = $el.clone().css({
                    'position': 'absolute',
                    'width': 'auto',
                    'visibility': 'hidden',
                    'overflow': 'hidden'
                }).insertAfter($el);
                $el.text(text);
                $t.text(text);
                if ($t.width() > w) {
                    while ((c = Math.floor((b + a) / 2)) > a) {
                        $t.text(text.substr(0, c) + '...');
                        if ($t.width() > w) {
                            b = c;
                        } else { a = c; }
                    }
                    $el.text(text.substr(0, c) + '...');
                    if (!$el.attr('title')) { $el.attr('title', text); }
                }
                $t.remove();
            });
        }
        return this;
    };
}(jQuery));
