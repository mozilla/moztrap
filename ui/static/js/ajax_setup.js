/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery */

(function ($) {

    'use strict';

    $("body").ajaxError(
        function (event, request, settings, error) {
            var data;
            $('body').loadingOverlay('remove');
            if (error === "UNAUTHORIZED" || error === "FORBIDDEN") {
                data = $.parseJSON(request.responseText);
                window.location = data.login_url + "?next=" + window.location.pathname;
            } // @@@ any global default error handling needed?
        }
    );
}(jQuery));
