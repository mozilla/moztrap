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

    // @@@ remove this once testcase tagging ajax is live
    $.mockjax({
        url: '/manage/testcase/tags*',
        contentType: 'text/json',
        responseText: {
            suggestions: [
                {
                    id: '5',
                    name: 'this tag',
                    preText: '',
                    typedText: 'thi',
                    postText: 's tag'
                },
                {
                    id: '6',
                    name: 'this other tag',
                    preText: '',
                    typedText: 'thi',
                    postText: 's other tag'
                }
            ],
            messages: []
        }
    });

}(jQuery));
