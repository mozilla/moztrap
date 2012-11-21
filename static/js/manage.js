/*jslint    browser:    true,
 indent:     4,
 confusion:  true,
 regexp:     true */
/*global    ich, jQuery, confirm */

var MT = (function (MT, $) {

    'use strict';

    // Filter form options based on trigger form selection
    MT.disableOnChecked = function (opts) {
        var defaults = {
                container: 'body',
                trigger_field: '.trigger',
                target_field: '.target'
            },
            options = $.extend({}, defaults, opts),
            context = $(options.container),
            trigger = context.find(options.trigger_field),
            target;
        if (context.length) {
            target = context.find(options.target_field);
            target.prop("disabled", trigger.is(":checked"));
            trigger.click(function() {
                target.prop("disabled", $(this).is(":checked"));
            });
        }

    };

    return MT;

}(MT || {}, jQuery));
