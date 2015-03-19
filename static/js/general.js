/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery window */

var MT = (function (MT, $) {

    'use strict';

    MT.readOnlyMode = function () {
        var banner = $('#read-only-banner');
        if (banner.length) {
            console.warn(
                "Database is in READ-ONLY mode. " +
                $('p', banner).text()
            );
        }
        banner.on('click', '.close-button', function(event) {
            event.preventDefault();
            banner.fadeOut(500);
        });
    };

    return MT;

}(MT || {}, jQuery));
