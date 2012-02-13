/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    // Enable adding/editing tags on manage-tag page
    CC.manageTags = function (container) {
        var context = $(container),
            createTag = context.find('.create a'),

            addTag = function () {
                var addTagForm = ich.tag_edit({
                        id: 'newtag',
                        action: 'add'
                    }),
                    replaceList = context.find('.action-ajax-replace'),
                    cancel = addTagForm.find('a[title="cancel"]');

                $(addTagForm).appendTo(replaceList).wrap(ich.tag_add()).find('input').focus();

                addTagForm.ajaxForm({
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

                cancel.click(function (e) {
                    e.preventDefault();
                    $(this).closest('.listitem').remove();
                });
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
                edit = $(this),
                tagID = thisTag.data('id'),
                tagH3 = thisTag.find('h3.name').clone(),
                tagName = tagH3.text(),
                editForm = ich.tag_edit({
                    id: tagID,
                    name: tagName,
                    action: 'edit'
                }),
                cancel = editForm.find('a[title="cancel"]');

            if (tagID && tagName) {
                thisTag.find('h3.name').replaceWith(editForm);
                edit.remove();
                editTag();

                cancel.click(function (e) {
                    e.preventDefault();
                    $(this).closest('.listitem').find('.controls').prepend(edit);
                    $(this).closest('.tag-form').replaceWith(tagH3);
                });
            }
        });

        createTag.click(function (e) {
            e.preventDefault();
            if (context.find('#tag-id-newtag').length) {
                $('#tag-id-newtag').find('input').focus();
            } else {
                addTag();
            }
        });
    };

    return CC;

}(CC || {}, jQuery));