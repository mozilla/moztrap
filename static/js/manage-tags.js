/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    CC.manageTags = function (container) {
        var context = $(container),
            addTag = context.find('#add-tag-form'),
            replaceList = addTag.closest('.action-ajax-replace'),
            editTag = context.find('.item a[title="edit"]');

        addTag.ajaxForm({
            beforeSubmit: function (arr, form, options) {
                replaceList.loadingOverlay();
            },
            success: function (response) {
                var newList = $(response.html);
                replaceList.loadingOverlay('remove');
                if (response.html) {
                    replaceList.replaceWith(newList);
                    CC.manageTags('#managetags');
                    newList.find('.details').html5accordion();
                }
            }
        });
    };

    return CC;

}(CC || {}, jQuery));