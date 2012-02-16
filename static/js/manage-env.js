/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
*/
/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    CC.createEnvProfile = function (container) {
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
                context.find('.bulkselectitem .elements input[name="elements"]').each(function () {
                    if ($(this).closest('.elements').find('input[name="elements"]:checked').length) {
                        $(this).closest('.bulkselectitem').find('.bulk-value').prop('checked', true);
                    }
                });
            };

        // some elements may load already checked
        updateLabels();
        updateBulkInputs();

        context.on('before-replace', '.bulkselectitem .element', function (event, replacement) {
            // Removes element preview (label) when element is deleted.
            // Other actions (other than delete) might also cause this to fire, with new HTML
            // (already parsed into jQuery object) in "replacement".
            if (!replacement.html()) {
                var thisElement = $(event.target),
                    thisElementID = thisElement.data('element-id'),
                    thisPreview = thisElement.closest('.bulkselectitem').find('.preview label[for="element-' + thisElementID + '"]').parent('li');
                thisPreview.detach();
                if (thisElement.closest('.elements').find('input[name="elements"]:checked').not(thisElement.find('input[name="elements"]')).length) {
                    thisElement.closest('.bulkselectitem').find('.bulk-value').prop('checked', true);
                } else {
                    thisElement.closest('.bulkselectitem').find('.bulk-value').prop('checked', false);
                }
            }
        });

        context.on('keydown', '#id_name', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                event.preventDefault();
                context.find('.form-actions button[type="submit"]').focus();
            }
        });

        context.on('change', '.bulkselectitem .element input[name="elements"]', function () {
            var thisID = $(this).attr('id');
            if ($(this).is(':checked')) {
                context.find('label[for=' + thisID + ']').addClass('checked');
            } else {
                context.find('label[for=' + thisID + ']').removeClass('checked');
            }
            if ($(this).closest('.elements').find('input[name="elements"]:checked').length) {
                $(this).closest('.bulkselectitem').find('.bulk-value').prop('checked', true);
            } else {
                $(this).closest('.bulkselectitem').find('.bulk-value').prop('checked', false);
            }
        });

        context.on('change', '.bulkselectitem .bulk-value', function () {
            if ($(this).is(':checked')) {
                $(this).closest('.bulkselectitem').find('.element input[name="elements"]').prop('checked', true);
            } else {
                $(this).closest('.bulkselectitem').find('.element input[name="elements"]').prop('checked', false);
            }
            updateLabels();
        });

        context.on('keydown', '.bulkselectitem input[name="new-element-name"]', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
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
                    })).appendTo($('#messages'));
                    $('#messages').messages();
                }
                event.preventDefault();
            }
        });

        context.on('keydown', '#new-category-name', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
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
                    })).appendTo($('#messages'));
                    $('#messages').messages();
                }
                event.preventDefault();
            }
        });

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
                    type: 'element'
                });
            thisElement.replaceWith(editThisElement);

            event.preventDefault();
        });

        context.on('click', '.bulkselectitem .item-content .edit-name .edit-link', function (event) {
            var thisName = $(this).closest('.edit-name'),
                categoryId = thisName.data('category-id'),
                inputId = 'edit-category-id-' + categoryId,
                name = thisName.data('category-name'),
                editThisName = ich.env_profile_edit_input({
                    inputId: inputId,
                    id: categoryId,
                    name: name,
                    type: 'category'
                });
            thisName.replaceWith(editThisName);

            event.preventDefault();
        });

        context.on('keydown', '.bulkselectitem .elements .editing input', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                if ($(this).val().length) {
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
                    $(ich.message({
                        message: "Please enter an element name.",
                        tags: "error"
                    })).appendTo($('#messages'));
                    $('#messages').messages();
                }
                event.preventDefault();
            }
        });

        context.on('keydown', '.bulkselectitem .item-content .editing.category input', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                if ($(this).val().length) {
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
                    $(ich.message({
                        message: "Please enter a category name.",
                        tags: "error"
                    })).appendTo($('#messages'));
                    $('#messages').messages();
                }
                event.preventDefault();
            }
        });
    };

    CC.editEnvProfile = function () {
        var profileNameInput = $('#editprofile #profile-name-form .profile-name input'),
            profileName = profileNameInput.val(),
            profileNameSubmit = $('#editprofile #profile-name-form .form-actions button[type="submit"]').hide(),

            addEnv = function () {
                var replaceList = $('#editprofile .managelist.action-ajax-replace');

                if ($('#editprofile #add-environment-form').length) {
                    $('#editprofile #add-environment-form').ajaxForm({
                        beforeSubmit: function (arr, form, options) {
                            replaceList.loadingOverlay();
                        },
                        success: function (response) {
                            var newList = $(response.html);
                            replaceList.loadingOverlay('remove');
                            if (response.html) {
                                replaceList.replaceWith(newList);
                                $('#editprofile .add-item').customAutocomplete({
                                    textbox: '#env-elements-input',
                                    suggestionList: '.suggest',
                                    inputList: '.env-element-list',
                                    ajax: true,
                                    url: $('#env-elements-input').data('autocomplete-url'),
                                    hideFormActions: true,
                                    expiredList: '.env-element-list',
                                    inputType: 'element'
                                });
                                addEnv();
                                newList.find('.details').html5accordion();
                            }
                        }
                    });
                }
            };

        addEnv();

        $('#editprofile').on('after-replace', '.managelist.action-ajax-replace', function (event, replacement) {
            // Re-attaches handlers to list after it is reloaded via Ajax.
            addEnv();
            $('#editprofile .add-item').customAutocomplete({
                textbox: '#env-elements-input',
                suggestionList: '.suggest',
                inputList: '.env-element-list',
                ajax: true,
                url: $('#env-elements-input').data('autocomplete-url'),
                hideFormActions: true,
                expiredList: '.env-element-list',
                inputType: 'element'
            });
        });

        $('#editprofile').on('keyup', '#profile-name-form .profile-name input', function (event) {
            if ($(this).val() !== profileName) {
                profileNameSubmit.fadeIn();
            } else {
                profileNameSubmit.fadeOut();
            }
        });

        $('#editprofile').on('keydown', '#profile-name-form .profile-name input', function (event) {
            if (event.keyCode === CC.keycodes.ENTER && !profileNameSubmit.is(':visible')) {
                event.preventDefault();
            }
        });

        if ($('#editprofile #profile-name-form').length) {
            $('#editprofile #profile-name-form').ajaxForm({
                success: function (response) {
                    profileName = profileNameInput.val();
                    profileNameSubmit.fadeOut();
                    profileNameInput.blur();
                }
            });
        }
    };

    CC.envNarrowing = function (container) {
        var context = $(container),
            bulkSelect = context.find('#bulk_select'),
            inputs = context.find('input[type="checkbox"][name="environments"]');

        bulkSelect.change(function () {
            if ($(this).is(':checked')) {
                inputs.prop('checked', true);
            } else {
                inputs.prop('checked', false);
            }
        });

        inputs.change(function () {
            if (inputs.not(':checked').length) {
                bulkSelect.prop('checked', false);
            }
        });
    };

    return CC;

}(CC || {}, jQuery));