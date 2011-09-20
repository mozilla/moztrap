/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    CC.createEnvProfile = function () {
        var elements = $('#addprofile .item .elements'),
            elementInputs = elements.find('.element-select input'),
            categoryInputs = $('#addprofile .item .bulk input[id^="bulk-select-"]'),
            profileNameInput = $('#addprofile #profile_name'),
            addElement = $('input[id$="-new-element-name"]'),
            addCategory = $('input#new-category-name'),
            editElementLink = $('#addprofile .item .elements a[title="edit"]'),
            editElement = $('#addprofile .item .elements .editing input'),
            updateLabels = function () {
                $('#addprofile .item .elements .element-select input').each(function () {
                    var thisID = $(this).attr('id');
                    if ($(this).is(':checked')) {
                        $('label[for=' + thisID + ']').addClass('checked');
                    } else {
                        $('label[for=' + thisID + ']').removeClass('checked');
                    }
                });
            },
            updateBulkInputs = function () {
                $('#addprofile .item .elements .element-select input').each(function () {
                    if ($(this).closest('.elements').find('input[type="checkbox"]:checked').length) {
                        $(this).closest('.item').find('.bulk input[name="bulk-select"]').prop('checked', true);
                    }
                });
            };

        // some elements may load already checked
        updateLabels();
        updateBulkInputs();

        elements.live('before-replace', function (event, replacement) {
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

        profileNameInput.live('keydown', function (event) {
            if (event.keyCode === CC.keycodes.ENTER) {
                event.preventDefault();
                $('#addprofile .form-actions button').focus();
            }
        });

        elementInputs.live('change', function () {
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

        categoryInputs.live('change', function () {
            if ($(this).is(':checked')) {
                $(this).closest('.item').find('.elements input').prop('checked', true);
            } else {
                $(this).closest('.item').find('.elements input').prop('checked', false);
            }
            updateLabels();
        });

        addElement.live('keydown', function (event) {
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

        addCategory.live('keydown', function (event) {
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

        editElementLink.live('click', function (event) {
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

        editElement.live('keydown', function (event) {
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
            typedText,
            newSuggestions,

            addEnv = function () {
                var replaceList = $('#editprofile .managelist.action-ajax-replace'),
                    addEnvTextbox = replaceList.find('.items .item.add-item .env-management #env-elements-input'),
                    url = addEnvTextbox.data('autocomplete-url'),
                    newEnvList = replaceList.find('.items .item.add-item #add-environment-form .env-element-list'),
                    suggestionList = replaceList.find('.items .item.add-item .env-management .suggest').hide(),
                    addEnvSubmit = replaceList.find('.items .item.add-item #add-environment-form .form-actions #add-environment').hide(),

                    updateSuggestions = function (data) {
                        var filteredSuggestions;
                        newSuggestions = ich.env_suggestion(data);
                        filteredSuggestions = newSuggestions.filter(function (index) {
                            var thisSuggestion = $(this).find('a').data('id');
                            return !(newEnvList.find('input[name="element"][value="' + thisSuggestion + '"]').length);
                        });
                        suggestionList.html(filteredSuggestions).show().find('li:first-child a').addClass('selected');
                    },

                    updateAddEnvSubmit = function () {
                        if (newEnvList.find('input[name="element"]').length) {
                            addEnvSubmit.fadeIn();
                        } else {
                            addEnvSubmit.fadeOut();
                        }
                    };

                $('#editprofile #add-environment-form').ajaxForm({
                    beforeSubmit: function (arr, form, options) {
                        replaceList.loadingOverlay();
                    },
                    success: function (response) {
                        var newList = $(response.html);
                        replaceList.loadingOverlay('remove');
                        if (response.html) {
                            replaceList.replaceWith(newList);
                            addEnv();
                            newList.find('.details').html5accordion();
                        }
                    }
                });

                addEnvTextbox.keyup(function () {
                    $(this).doTimeout(300, function () {
                        // Updates suggestion-list if typed-text has changed
                        if ($(this).val() !== typedText) {
                            typedText = $(this).val();
                            if (typedText.length) {
                                $.get(url, {text: typedText}, updateSuggestions);
                            } else {
                                suggestionList.empty().hide();
                            }
                        }
                    });
                }).keydown(function (event) {
                    // If the suggestion list is not visible...
                    if (!suggestionList.is(':visible')) {
                        // ...and if the textbox is not empty...
                        if (addEnvTextbox.val() !== '') {
                            // ...and if the keydown was a non-meta key other than shift, ctrl, alt, caps, or esc...
                            if (!event.metaKey && event.keyCode !== CC.keycodes.SHIFT && event.keyCode !== CC.keycodes.CTRL && event.keyCode !== CC.keycodes.ALT && event.keyCode !== CC.keycodes.CAPS && event.keyCode !== CC.keycodes.ESC) {
                                // ...prevent normal TAB function
                                if (event.keyCode === CC.keycodes.TAB || event.keyCode === CC.keycodes.ENTER) {
                                    event.preventDefault();
                                }
                                // ...show the suggestion list
                                suggestionList.show();
                            }
                        // If the textbox is empty...
                        } else {
                            // ...and if the keydown was ENTER...
                            if (event.keyCode === CC.keycodes.ENTER) {
                                event.preventDefault();
                                // ...submit the form.
                                addEnvSubmit.click();
                                return false;
                            }
                        }
                    // If the suggestion list is already visible...
                    } else {
                        var thisSuggestionName = suggestionList.find('.selected').data('name');
                        // UP and DOWN move "active" suggestion
                        if (event.keyCode === CC.keycodes.UP) {
                            event.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':first-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                            }
                            return false;
                        }
                        if (event.keyCode === CC.keycodes.DOWN) {
                            event.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':last-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                            }
                            return false;
                        }
                        // ENTER selects the "active" filter suggestion.
                        if (event.keyCode === CC.keycodes.ENTER) {
                            event.preventDefault();
                            if (suggestionList.find('.selected').length) {
                                suggestionList.find('.selected').click();
                            }
                            return false;
                        }
                        // TAB auto-completes the "active" suggestion if it isn't already completed...
                        if (event.keyCode === CC.keycodes.TAB) {
                            if (thisSuggestionName && addEnvTextbox.val().toLowerCase() !== thisSuggestionName.toLowerCase()) {
                                event.preventDefault();
                                addEnvTextbox.val(thisSuggestionName);
                                return false;
                            // ...otherwise, TAB selects the "active" filter suggestion (if exists)
                            } else {
                                if (suggestionList.find('.selected').length) {
                                    event.preventDefault();
                                    suggestionList.find('.selected').click();
                                    return false;
                                }
                            }
                        }
                        // RIGHT auto-completes the "active" suggestion if it isn't already completed
                        if (event.keyCode === CC.keycodes.RIGHT) {
                            if (thisSuggestionName && addEnvTextbox.val().toLowerCase() !== thisSuggestionName.toLowerCase()) {
                                event.preventDefault();
                                addEnvTextbox.val(thisSuggestionName);
                                return false;
                            }
                        }
                        // ESC hides the suggestion list
                        if (event.keyCode === CC.keycodes.ESC) {
                            event.preventDefault();
                            suggestionList.hide();
                            return false;
                        }
                        return true;
                    }
                }).focus(function () {
                    // Resets textbox data-clicked to ``false`` (becomes ``true`` when an autocomplete suggestion is clicked)
                    addEnvTextbox.data('clicked', false);
                // On blur, hides the suggestion list after 150 ms if textbox data-clicked is ``false``
                }).blur(function () {
                    function hideList() {
                        if (addEnvTextbox.data('clicked') !== true) {
                            suggestionList.hide();
                            addEnvTextbox.data('clicked', false);
                        }
                    }
                    window.setTimeout(hideList, 150);
                });

                suggestionList.find('a').live({
                    // Adds ``.selected`` to suggestion on mouseover, removing ``.selected`` from other suggestions
                    mouseover: function () {
                        var thisSuggestion = $(this).addClass('selected'),
                            otherSuggestions = thisSuggestion.parent('li').siblings('li').find('a').removeClass('selected');
                    },
                    // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
                    mousedown: function () {
                        addEnvTextbox.data('clicked', true);
                    },
                    click: function (e) {
                        e.preventDefault();
                        var newEnv,
                            id = $(this).data('id'),
                            name = $(this).data('name');
                        if (id && name) {
                            newEnv = ich.env_element_selected({
                                id: id,
                                name: name
                            });
                            if (newEnv.length) {
                                newEnvList.append(newEnv);
                                updateAddEnvSubmit();
                            }
                        }

                        // Reset the textbox, and reset and hide the suggestion list
                        addEnvTextbox.val(null);
                        typedText = null;
                        suggestionList.empty().hide();
                    }
                });

                newEnvList.find('li').live('click', function () {
                    var filteredSuggestions;
                    $(this).remove();
                    updateAddEnvSubmit();
                    filteredSuggestions = newSuggestions.filter(function (index) {
                        var thisSuggestion = $(this).find('a').data('id');
                        return !(newEnvList.find('input[name="element"][value="' + thisSuggestion + '"]').length);
                    });
                    suggestionList.html(filteredSuggestions);
                });
            };

        addEnv();

        $('#editprofile .managelist.action-ajax-replace').live('after-replace', function (event, replacement) {
            // Re-attaches handlers to list after it is reloaded via Ajax.
            addEnv();
        });

        profileNameInput.live('keyup', function (event) {
            if ($(this).val() !== profileName) {
                profileNameSubmit.fadeIn();
            } else {
                profileNameSubmit.fadeOut();
            }
        });

        profileNameInput.live('keydown', function (event) {
            if (event.keyCode === CC.keycodes.ENTER && !profileNameSubmit.is(':visible')) {
                event.preventDefault();
            }
        });

        $('#editprofile #profile-name-form').ajaxForm({
            success: function (response) {
                profileName = profileNameInput.val();
                profileNameSubmit.fadeOut();
                profileNameInput.blur();
            }
        });
    };

    return CC;

}(CC || {}, jQuery));