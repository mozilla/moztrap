/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    CC.manageTags = function (container) {
        var context = $(container),

            addTag = function () {
                var addTagForm = context.find('#add-tag-form'),
                    replaceList = addTagForm.closest('.action-ajax-replace');

                if (addTagForm.length) {
                    addTagForm.ajaxForm({
                        beforeSubmit: function (arr, form, options) {
                            replaceList.loadingOverlay();
                        },
                        success: function (response) {
                            var newList = $(response.html);
                            replaceList.loadingOverlay('remove');
                            if (response.html) {
                                replaceList.replaceWith(newList);
                                addTag();
                                newList.find('.details').html5accordion();
                            }
                        }
                    });
                }
            },

            editTag = function () {
                var editTagForm = context.find('#edit-tag-form'),
                    replaceList = editTagForm.closest('.action-ajax-replace');

                editTagForm.ajaxForm({
                    beforeSubmit: function (arr, form, options) {
                        replaceList.loadingOverlay();
                    },
                    success: function (response) {
                        var newList = $(response.html);
                        replaceList.loadingOverlay('remove');
                        if (response.html) {
                            replaceList.replaceWith(newList);
                            newList.find('.details').html5accordion();
                        }
                    }
                });
            };

        context.delegate('.item a[title="edit"]', 'click', function (e) {
            e.preventDefault();
            var thisTag = $(this).closest('.item'),
                tagID = thisTag.data('id'),
                tagName = thisTag.find('h3.tag').text(),
                editForm = ich.tag_edit({
                    id: tagID,
                    name: tagName
                }),
                cancel;

            if (tagID && tagName) {
                thisTag.replaceWith(editForm);
                editTag();
                cancel = $(editForm).find('a[title="cancel"]');

                cancel.click(function (e) {
                    e.preventDefault();
                    $(editForm).replaceWith(thisTag);
                });
            }
        });

        addTag();
    };

    return CC;

}(CC || {}, jQuery));