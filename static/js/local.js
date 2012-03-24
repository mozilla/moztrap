/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    // Store keycode variables for easier readability
    CC.keycodes = {
        SPACE: 32,
        ENTER: 13,
        TAB: 9,
        ESC: 27,
        BACKSPACE: 8,
        SHIFT: 16,
        CTRL: 17,
        ALT: 18,
        CAPS: 20,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40
    };

    // add class "hadfocus" to inputs and textareas on blur
    CC.inputHadFocus = function () {
        $(document).on('blur', 'input:not([type=radio], [type=checkbox]), textarea', function () {
            $(this).addClass('hadfocus');
        });
    };

    return CC;

}(CC || {}, jQuery));