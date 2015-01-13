/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery document ga */

var MT = (function (MT, $) {

    'use strict';

    MT.googleAnalyticsAjax = function () {
        // When you have Google Analytics enabled you get a global
        // object called `ga`. If that's not defined, exit early.
        if (typeof ga === 'undefined') {
            return;
        }
        jQuery(document)
        .ajaxComplete(function(event, xhr, settings) {
            // e.g 'send', 'event', 'GET', '?id=184', non-interation
            ga('send', 'event', 'ajax', settings.type, settings.url, true);
        })
        .ajaxError(function(event, xhr, settings) {
            ga('send', 'event', 'ajaxerror', settings.type, settings.url, true);
        });
    };

    return MT;

}(MT || {}, jQuery));
