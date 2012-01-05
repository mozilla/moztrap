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
                var editTagForm = context.find('.tag-form'),
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

        context.on('click', '.listitem a[title="edit"]', function (e) {
            e.preventDefault();
            var thisTag = $(this).closest('.listitem'),
                tagID = thisTag.data('id'),
                tagH3 = thisTag.find('h3.name').clone(),
                tagName = tagH3.text(),
                editForm = ich.tag_edit({
                    id: tagID,
                    name: tagName
                }),
                edit = thisTag.find('a[title="edit"]').clone(),
                cancel;

            if (tagID && tagName) {
                thisTag.find('h3.name').replaceWith(editForm);
                editTag();
                cancel = thisTag.find('a[title="edit"]').attr('title', 'cancel').text('cancel');

                cancel.click(function (e) {
                    e.preventDefault();
                    $(this).closest('.listitem').find('.tag-form').replaceWith(tagH3);
                    $(this).replaceWith(edit);
                });
            }
        });

        addTag();
    };

    return CC;

}(CC || {}, jQuery));