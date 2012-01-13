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

    CC.createEnvProfile = function () {
        var context = $('#addprofile'),
            elements = context.find('.item .elements'),
            elementInputs = elements.find('.element-select input'),
            categoryInputs = context.find('.item .bulk input[id^="bulk-select-"]'),
            profileNameInput = context.find('#profile_name'),
            addElement = $('input[id$="-new-element-name"]'),
            addCategory = $('input#new-category-name'),
            editElementLink = elements.find('a[title="edit"]'),
            editElement = elements.find('.editing input'),
            updateLabels = function () {
                context.find('.item .elements .element-select input').each(function () {
                    var thisID = $(this).attr('id');
                    if ($(this).is(':checked')) {
                        $('label[for=' + thisID + ']').addClass('checked');
                    } else {
                        $('label[for=' + thisID + ']').removeClass('checked');
                    }
                });
            },
            updateBulkInputs = function () {
                context.find('.item .elements .element-select input').each(function () {
                    if ($(this).closest('.elements').find('input[type="checkbox"]:checked').length) {
                        $(this).closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', true);
                    }
                });
            };

        // some elements may load already checked
        updateLabels();
        updateBulkInputs();

        context.on('before-replace', '.item .elements', function (event, replacement) {
            // Removes element preview (label) when element is deleted.
            // Other actions (other than delete) might also cause this to fire, with new HTML
            // (already parsed into jQuery object) in "replacement".
            if (!replacement.html()) {
                var thisElement = $(event.target),
                    thisElementID = thisElement.data('element-id'),
                    thisPreview = thisElement.closest('.item').find('.preview label[for="element-' + thisElementID + '"]').parent('li');
                thisPreview.detach();
                if (thisElement.closest('.elements').find('input[name="element"]:checked').not(thisElement.closest('.action-ajax-replace').find('input[name="element"]')).length) {
                    thisElement.closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', true);
                } else {
                    thisElement.closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', false);
                }
            }
        });

        context.on('keydown', '#profile_name', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                event.preventDefault();
                context.find('.form-actions button').focus();
            }
        });

        context.on('change', '.item .elements .element-select input', function () {
            var thisID = $(this).attr('id');
            if ($(this).is(':checked')) {
                $('label[for=' + thisID + ']').addClass('checked');
            } else {
                $('label[for=' + thisID + ']').removeClass('checked');
            }
            if ($(this).closest('.elements').find('input[type="checkbox"]:checked').length) {
                $(this).closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', true);
            } else {
                $(this).closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', false);
            }
        });

        context.on('change', '.item .bulk input[id^="bulk-select-"]', function () {
            if ($(this).is(':checked')) {
                $(this).closest('.item').find('.elements input').prop('checked', true);
            } else {
                $(this).closest('.item').find('.elements input').prop('checked', false);
            }
            updateLabels();
        });

        context.on('keydown', 'input[id$="-new-element-name"]', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                if ($(this).val().length) {
                    var input = $(this),
                        name = input.val(),
                        loading = input.closest('.content'),
                        url = '',
                        data = {},
                        success = function (response) {
                            var newElem = $(response.elem),
                                newPreview = $(response.preview);
                            if (!response.no_replace) {
                                input.closest('.elements').children('li.add-element').before(newElem);
                                input.closest('.item').find('.preview').append(newPreview);
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

        context.on('keydown', 'input#new-category-name', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                if ($(this).val().length) {
                    var input = $(this),
                        loading = input.closest('.content'),
                        url = '',
                        data = {},
                        success = function (response) {
                            var newelem = $(response.html);
                            if (!response.no_replace) {
                                input.closest('.items').children('.add-item').before(newelem);
                                newelem.addClass('open').find('.details').andSelf().html5accordion();
                                input.val(null).closest('.item').find('.summary').click();
                                newelem.find('.elements .add-element input').focus();
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

        context.on('click', '.item .elements a[title="edit"]', function (event) {
            var thisElement = $(this).closest('li'),
                inputId = thisElement.find('input').attr('id'),
                elementId = thisElement.data('element-id'),
                name = thisElement.find('label').html(),
                checked = thisElement.find('input').is(':checked'),
                editThisElement = ich.env_profile_element_edit({
                    inputId: inputId,
                    elementId: elementId,
                    name: name,
                    checked: checked
                });
            thisElement.replaceWith(editThisElement);

            event.preventDefault();
        });

        context.on('keydown', '.item .elements .editing input', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                if ($(this).val().length) {
                    var input = $(this),
                        thisElement = input.closest('.editing'),
                        name = input.val(),
                        inputId = input.attr('id'),
                        elementId = input.data('element-id'),
                        preview = input.closest('.item').find('.preview').find('label[for="' + inputId + '"]').closest('li'),
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
                                    $('#' + inputId).prop('checked', checked);
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

    return CC;

}(CC || {}, jQuery));