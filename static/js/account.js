/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    // cancel button on change-password pages triggers browser back event
    MT.changePwdCancel = function () {
        var context = $('#changepasswordform'),
            cancel = context.find('.form-actions .cancel');

        cancel.click(function (e) {
            context.get(0).reset();
            window.history.back();
            e.preventDefault();
        });
    };

    return MT;

}(MT || {}, jQuery));