/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    MT.owa = function () {
        var trigger = $('#owa a'),
            url = trigger.data('url'),
            installCallback = function () {
                // great - display a message, or redirect to a launch page
                var msg = 'Successfully registered!';
                ich.message({message: msg, tags: 'success'}).appendTo($('#messages ul'));
                $('#messages ul').messages();
            },
            errorCallback = function () {
                // whoops - result.code and result.message have details
                var msg = 'Could not install: ' + this.error;
                ich.message({message: msg, tags: 'error'}).appendTo($('#messages ul'));
                $('#messages ul').messages();
            },
            result;

        trigger.click(function (e) {
            e.preventDefault();
            if (url) {
                result = navigator.mozApps.install(url, {});
                result.onsuccess = installCallback;
                result.onerror = errorCallback;
            }
        });
    };

    return MT;

}(MT || {}, jQuery));