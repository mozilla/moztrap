/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    MT.createEnvProfile = function (container) {
        var context = $(container),
            elements = context.find('.bulkselectitem .elements .element'),
            updateLabels = function () {
                context.find('.bulkselectitem .elements input[name="elements"]').each(function () {
                    var thisID = $(this).attr('id');
                    if ($(this).is(':checked')) {
                        context.find('label[for=' + thisID + ']').addClass('checked');
                    } else {
                        context.find('label[for=' + thisID + ']').removeClass('checked');
                    }
                });
            },
            updateBulkInputs = function () {
                context.find('.bulkselectitem .bulk-value').each(function () {
                    var bulkInput = $(this),
                        thisCategory = bulkInput.closest('.bulkselectitem');
                    if (thisCategory.find('.elements input[name="elements"]:checked').length) {
                        bulkInput.prop('checked', true);
                        if (thisCategory.find('.elements input[name="elements"]').length === thisCategory.find('.elements input[name="elements"]:checked').length) {
                            bulkInput.removeClass('pseudo');
                        } else {
                            bulkInput.addClass('pseudo');
                        }
                    } else {
                        bulkInput.prop('checked', false).removeClass('pseudo');
                    }
                });
            };

        // some elements may load already checked
        updateLabels();
        updateBulkInputs();

        // Removes element preview (label) when element is deleted.
        // Other actions (other than delete) might also cause this to fire, with new HTML
        // (already parsed into jQuery object) in "replacement".
        context.on('before-replace', '.bulkselectitem .element', function (event, replacement) {
            if (!replacement.html()) {
                var thisElement = $(event.target),
                    thisElementID = thisElement.data('element-id'),
                    thisPreview = thisElement.closest('.bulkselectitem').find('.preview label[for="element-' + thisElementID + '"]').parent('li');
                thisElement.find('input[name="elements"]').prop('checked', false);
                thisPreview.remove();
                updateBulkInputs();
            }
        });

        // ENTER in Name textbox shifts focus to submit button
        context.on('keydown', '#id_name', function (event) {
            if (event.keyCode === MT.keycodes.ENTER) {
                event.preventDefault();
                context.find('.form-actions button[type="submit"]').focus();
            }
        });

        // Update category labels and bulk-inputs when element changes
        context.on('change', '.bulkselectitem .element input[name="elements"]', function () {
            updateLabels();
            updateBulkInputs();
        });

        // Select/de-select all elements when category bulk-input is selected/de-selected
        context.on('change', '.bulkselectitem .bulk-value', function () {
            if ($(this).is(':checked')) {
                $(this).closest('.bulkselectitem').find('.element input[name="elements"]').prop('checked', true);
            } else {
                $(this).closest('.bulkselectitem').find('.element input[name="elements"]').prop('checked', false);
            }
            $(this).removeClass('pseudo');
            updateLabels();
        });

        // Ajax-submit new elements
        context.on('keydown', '.bulkselectitem .add-element input[name="new-element-name"]', function (event) {
            if (event.keyCode === MT.keycodes.ENTER) {
                if ($(this).val().length) {
                    var input = $(this),
                        name = input.val(),
                        loading = input.closest('.itembody'),
                        url = '',
                        data = {},
                        success = function (response) {
                            var newElem = $(response.elem),
                                newPreview = $(response.preview);
                            if (!response.no_replace) {
                                input.closest('.elements').find('.add-element').before(newElem);
                                input.closest('.bulkselectitem').find('.preview').append(newPreview);
                                input.val(null);
                                updateBulkInputs();
                            }
                            loading.loadingOverlay('remove');
                        };
                    data['category-id'] = input.data('category-id');
                    data[input.attr('name')] = input.val();

                    loading.loadingOverlay();
                    $.ajax(url, {
                        type: "POST",
                        data: data,
                        success: success
                    });
                } else {
                    $(ich.message({
                        message: "Please enter an element name.",
                        tags: "error"
                    })).appendTo($('#messages ul'));
                    $('#messages ul').messages();
                }
                event.preventDefault();
            }
        });

        // Ajax-submit new categories
        context.on('keydown', '#new-category-name', function (event) {
            if (event.keyCode === MT.keycodes.ENTER) {
                if ($(this).val().length) {
                    var input = $(this),
                        loading = input.closest('.itembody'),
                        url = '',
                        data = {},
                        success = function (response) {
                            var newelem = $(response.html);
                            if (!response.no_replace) {
                                input.closest('.add-item').before(newelem);
                                newelem.find('.details').addClass('open').html5accordion();
                                input.val(null).closest('.add-item').find('.summary').first().click();
                                newelem.find('.elements .add-element input[name="new-element-name"]').focus();
                            }
                            loading.loadingOverlay('remove');
                        };
                    data[input.attr('name')] = input.val();

                    loading.loadingOverlay();
                    $.ajax(url, {
                        type: "POST",
                        data: data,
                        success: success
                    });
                } else {
                    $(ich.message({
                        message: "Please enter a category name.",
                        tags: "error"
                    })).appendTo($('#messages ul'));
                    $('#messages ul').messages();
                }
                event.preventDefault();
            }
        });

        // Replace element edit-link with editing input
        context.on('click', '.bulkselectitem .element .edit-link', function (event) {
            var thisElement = $(this).closest('.element'),
                inputId = thisElement.find('input[name="elements"]').attr('id'),
                elementId = thisElement.data('element-id'),
                name = thisElement.find('label').text(),
                checked = thisElement.find('input[name="elements"]').is(':checked'),
                editThisElement = ich.env_profile_edit_input({
                    inputId: inputId,
                    id: elementId,
                    name: name,
                    checked: checked,
                    type: 'element',
                    element: 'li'
                });
            thisElement.replaceWith(editThisElement);
            $(editThisElement).data('replaced', thisElement);

            event.preventDefault();
        });

        // Replace category name edit-link with editing input
        context.on('click', '.bulkselectitem .item-content .category .edit-link', function (event) {
            var thisName = $(this).closest('.category'),
                categoryId = thisName.data('category-id'),
                inputId = 'edit-category-id-' + categoryId,
                name = thisName.data('category-name'),
                editThisName = ich.env_profile_edit_input({
                    inputId: inputId,
                    id: categoryId,
                    name: name,
                    type: 'category',
                    element: 'div'
                });
            thisName.replaceWith(editThisName);
            $(editThisName).data('replaced', thisName);

            event.preventDefault();
        });

        // Ajax-submit edited element name
        context.on('keydown', '.bulkselectitem .elements .editing input', function (event) {
            if (event.keyCode === MT.keycodes.ENTER) {
                if ($(this).val().length) {
                    if ($(this).val() !== $(this).data('original-value')) {
                        var input = $(this),
                            thisElement = input.closest('.editing'),
                            name = input.val(),
                            inputId = input.attr('id'),
                            elementId = input.data('element-id'),
                            preview = input.closest('.bulkselectitem').find('.preview').find('label[for="' + inputId + '"]').closest('li'),
                            checked = input.data('checked'),
                            url = '',
                            data = {},
                            success = function (response) {
                                var editedElem = $(response.elem),
                                    editedPreview = $(response.preview);

                                if (!response.no_replace) {
                                    thisElement.replaceWith(editedElem);
                                    preview.replaceWith(editedPreview);

                                    if (checked) {
                                        context.find('#' + inputId).prop('checked', checked);
                                        updateLabels();
                                    }
                                    input.val(null);
                                }

                                thisElement.loadingOverlay('remove');
                            };

                        data['element-id'] = elementId;
                        data[input.attr('name')] = input.val();

                        thisElement.loadingOverlay();
                        $.ajax(url, {
                            type: "POST",
                            data: data,
                            success: success
                        });
                    } else {
                        $(this).closest('.editing').replaceWith($(this).closest('.editing').data('replaced'));
                    }
                } else {
                    $(ich.message({
                        message: "Please enter an element name.",
                        tags: "error"
                    })).appendTo($('#messages ul'));
                    $('#messages ul').messages();
                }
                event.preventDefault();
            }
        });

        // Ajax-submit edited category name
        context.on('keydown', '.bulkselectitem .item-content .editing.category input', function (event) {
            if (event.keyCode === MT.keycodes.ENTER) {
                if ($(this).val().length) {
                    if ($(this).val() !== $(this).data('original-value')) {
                        var input = $(this),
                            thisCategory = input.closest('.bulkselectitem'),
                            name = input.val(),
                            nameKey = input.attr('name'),
                            categoryId = input.data('category-id'),
                            url = '',
                            data = {},
                            success = function (response) {
                                var editedCat = $(response.html);

                                if (!response.no_replace) {
                                    thisCategory.replaceWith(editedCat);
                                    editedCat.find('.details').addClass('open').html5accordion();
                                    updateLabels();
                                    updateBulkInputs();
                                }

                                thisCategory.loadingOverlay('remove');
                            };

                        data = thisCategory.find('input[name="elements"]').serializeArray();
                        data.push({'name': 'category-id', 'value': categoryId}, {'name': nameKey, 'value': name});

                        thisCategory.loadingOverlay();
                        $.ajax(url, {
                            type: "POST",
                            data: data,
                            success: success
                        });
                    } else {
                        $(this).closest('.editing').replaceWith($(this).closest('.editing').data('replaced'));
                    }
                } else {
                    $(ich.message({
                        message: "Please enter a category name.",
                        tags: "error"
                    })).appendTo($('#messages ul'));
                    $('#messages ul').messages();
                }
                event.preventDefault();
            }
        });
    };

    MT.addEnvToProfile = function (container, form) {
        var context = $(container),

            // Setup add-env form for ajax-submit
            addEnv = function () {
                var replaceList = context.find('.itemlist.action-ajax-replace');

                if (replaceList.length && context.find(form).length) {
                    context.find(form).ajaxForm({
                        beforeSubmit: function (arr, form, options) {
                            replaceList.loadingOverlay();
                        },
                        success: function (response) {
                            var newList = $(response.html);
                            replaceList.loadingOverlay('remove');
                            if (response.html) {
                                replaceList.replaceWith(newList);
                                $('#filter').find('input.check:checked').prop('checked', false).change();
                                context.find('.add-item').customAutocomplete({
                                    textbox: '#env-elements-input',
                                    inputList: '.env-element-list',
                                    ajax: true,
                                    url: $('#env-elements-input').data('autocomplete-url'),
                                    hideFormActions: true,
                                    inputType: 'element',
                                    caseSensitive: true,
                                    prefix: 'element'
                                });
                                addEnv();
                                newList.find('.details').html5accordion();
                            }
                        }
                    });
                }
            };

        addEnv();

        // Re-attach add-env form handlers after list is ajax-replaced (called in listpages.js)
        context.on('after-replace', '.itemlist.action-ajax-replace', function (event, replacement) {
            // Re-attaches handlers to list after it is reloaded via Ajax (on delete action).
            addEnv();
            context.find('.add-item').customAutocomplete({
                textbox: '#env-elements-input',
                inputList: '.env-element-list',
                ajax: true,
                url: $('#env-elements-input').data('autocomplete-url'),
                hideFormActions: true,
                inputType: 'element',
                caseSensitive: true,
                prefix: 'element'
            });
        });
    };

    MT.editEnvProfileName = function (container) {
        var context = $(container),
            profileNameInput = context.find('#profile-name'),
            profileName = profileNameInput.val(),
            profileNameSubmit = context.find('#save-profile-name').hide();

        // Show/hide profile-name submit button when name is changed
        context.on('keyup', '#profile-name', function (event) {
            if ($(this).val() !== profileName) {
                profileNameSubmit.fadeIn();
            } else {
                profileNameSubmit.fadeOut();
            }
        });

        // Prevent submission of profile-name form if value hasn't changed
        context.on('keydown', '#profile-name', function (event) {
            if (event.keyCode === MT.keycodes.ENTER && !profileNameSubmit.is(':visible')) {
                event.preventDefault();
            }
        });

        // Prepare profile-name form for ajax-submit
        if (context.find('#profile-name-form').length) {
            context.find('#profile-name-form').ajaxForm({
                success: function (response) {
                    profileName = profileNameInput.val();
                    profileNameSubmit.fadeOut();
                    profileNameInput.blur();
                }
            });
        }
    };

    // Bulk-select for visible (filtered) environments
    MT.bulkSelectEnvs = function (container) {
        var context = $(container),
            bulkSelect = context.find('#bulk_select'),
            items = context.find('.itemlist .items .listitem'),
            inputs = items.find('input.bulk-value[name="environments"]'),
            updateBulkSelect = function () {
                if (inputs.filter(':visible:checked').length) {
                    bulkSelect.prop('checked', true);
                    if (inputs.filter(':visible').length === inputs.filter(':visible:checked').length) {
                        bulkSelect.removeClass('pseudo');
                    } else {
                        bulkSelect.addClass('pseudo');
                    }
                } else {
                    bulkSelect.prop('checked', false).removeClass('pseudo');
                }
            };

        // Select-all/none on bulk-select change
        bulkSelect.change(function () {
            if ($(this).is(':checked')) {
                inputs.filter(':visible').prop('checked', true);
            } else {
                inputs.filter(':visible').prop('checked', false);
            }
            bulkSelect.removeClass('pseudo');
        });

        // Update bulk-select on input change
        inputs.change(function () {
            updateBulkSelect();
        });

        // Update bulk-select after filter-change
        context.on('after-filter', '.itemlist .items', updateBulkSelect);

        updateBulkSelect();
    };

    return MT;

}(MT || {}, jQuery));