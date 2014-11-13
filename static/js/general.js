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
            // if we have chosen to ignore the warning, let's close it
            if (window.sessionStorage.getItem('ignore-readonly')) {
                banner.hide();
                console.warn(
                    'To renable the read-only warning enter: ' +
                    "sessionStorage.removeItem('ignore-readonly');\n" +
                    'in the Web Console and refresh the page.'
                );
            }
        }
        banner.on('click', '.close-button', function(event) {
            event.preventDefault();
            window.sessionStorage.setItem('ignore-readonly', true);
            banner.fadeOut(500);
        });
    };

    return MT;

}(MT || {}, jQuery));
