/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (module, $) {

    'use strict';

    // Store keycode variables for easier readability
    var keycodes = {
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

    module.formOptionsFilter = function (context_sel, data_attr, trigger_sel, target_sel) {
        var context = $(context_sel),
            trigger = context.find(trigger_sel),
            target,
            allopts,
            doFilter;
        if (context.length && trigger.is("select")) {
            target = context.find(target_sel);
            allopts = target.find("option").clone();

            doFilter = function () {
                var key = trigger.find("option:selected").data(data_attr);
                target.empty();
                allopts.each(function () {
                    if ($(this).data(data_attr) === key) {
                        var newopt = $(this).clone();
                        newopt.appendTo(target);
                    }
                });
            };

            doFilter();

            trigger.change(doFilter);
        }
    };

    // Filtering, autocomplete, and fake placeholder text for manage and results pages
    module.filtering = function () {

        // Hide the form-actions (submit, reset) initially
        var formActions = $('#filter .form-actions').hide(),
            toggle = $('#filter .toggle a'),
            // Set data-originallyChecked on each input to store original state
            input = $('#filter .visual .filter-group input[type="checkbox"]').each(function () {
                $(this).data('originallyChecked', $(this).is(':checked'));
            }),
            textbox = $('#filter .textual #text-filter'),
            typedText,
            placeholder = textbox.attr('placeholder'),
            // Hide the list of autocomplete suggestions initially
            suggestionList = $('#filter .textual .suggest').hide(),
            keywordGroups = $('#filter .visual .filter-group.keyword'),
            notKeywordGroups = $('#filter .visual .filter-group:not(.keyword)'),
            selected,
            keywordTextboxes = keywordGroups.find('input[type="text"]'),

            // Removes (faked) placeholder text from textbox
            removeFakePlaceholder = function () {
                if (textbox.val().indexOf(placeholder) !== -1) {
                    textbox.val(null);
                }
                textbox.removeClass('placeholder');
            },

            // Checks if any inputs have changed from original-state,
            // showing form-actions if any inputs have changed.
            updateFormActions = function () {
                if (input.filter(function () { return $(this).data('state') === 'changed'; }).length) {
                    formActions.fadeIn('fast');
                    $('.managelist').addClass('expired');
                } else {
                    formActions.fadeOut('fast');
                    $('.managelist').removeClass('expired');
                }
            },

            // Empties suggestion-list, looks for un-selected autocomplete
            // suggestions based on typed-text (if there is typed-text) and appends
            // them to suggestion-list.
            updateSuggestions = function () {
                typedText = textbox.val();
                suggestionList.empty();
                if (textbox.val().length) {
                    var relevantFilters = notKeywordGroups.find('input[type="checkbox"]:not(:checked)').parent('li').filter(function () {
                        return $(this).children('label').html().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                    });
                    relevantFilters.each(function () {
                        var typedIndex = $(this).children('label').html().toLowerCase().indexOf(typedText.toLowerCase()),
                            preText = $(this).children('label').html().substring(0, typedIndex),
                            postText = $(this).children('label').html().substring(typedIndex + typedText.length),
                            type = $(this).children('input').attr('name'),
                            id = $(this).children('input').attr('id'),
                            newSuggestion = ich.filter_suggestion({
                                id: id,
                                preText: preText,
                                typedText: typedText,
                                postText: postText,
                                type: type
                            });
                        suggestionList.append(newSuggestion);
                    });
                    keywordGroups.each(function () {
                        var type = $(this).children('h5').html(),
                            name = $(this).data('name'),
                            keywordSuggestion = ich.keyword_filter_suggestion({
                                name: name,
                                typedText: typedText,
                                type: type
                            });
                        // If the keyword group already has selected filters...
                        if ($(this).find('input[type="checkbox"]:checked').length) {
                            // ...and if *all* of the selected filters begin with "^" and ends with "$"...
                            if ($(this).find('input[type="checkbox"][value^="^"][value$="$"]:checked').length === $(this).find('input[type="checkbox"]:checked').length
                                    // ...and if the typed-text hasn't already been selected as a filter, and if the typed-text begins with "^" and ends with "$"...
                                    && !($(this).find('input[type="checkbox"][value="' + typedText + '"]:checked').length)
                                    && typedText.indexOf('^') === 0
                                    && typedText.lastIndexOf('$') === typedText.length - 1) {
                                // ...then append the keyword suggestion to the suggestion-list.
                                suggestionList.append(keywordSuggestion);
                            }
                        // If there are no other filters selected in the current keyword group, append the current suggestion
                        } else {
                            suggestionList.append(keywordSuggestion);
                        }
                    });
                    // Adds ``.selected`` to first autocomplete suggestion.
                    suggestionList.find('li:first-child a').addClass('selected');
                }
            };

        // Shows/hides the advanced filtering
        toggle.click(function (e) {
            e.preventDefault();
            $('#filter .visual').toggleClass('compact expanded');
        });

        // Reset button sets each input to its original state, hides form-actions
        // and suggestion-list, and returns focus to the textbox.
        formActions.find('.reset').click(function (e) {
            e.preventDefault();
            formActions.fadeOut('fast');
            $('.managelist').removeClass('expired');
            input.each(function () {
                $(this).removeData('state');
                $(this).prop('checked', $(this).data('originallyChecked'));
            });
            textbox.focus();
            suggestionList.hide();
        });

        // Selecting/unselecting an input returns focus to textbox, hides
        // suggestion-list, sets data-state "changed" if input has changed from
        // original state, and shows/hides form-actions as appropriate.
        input.live('change', function () {
            if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                $(this).data('state', 'changed');
            } else {
                $(this).removeData('state');
            }
            textbox.focus();
            suggestionList.hide();
            updateFormActions();
        });

        keywordGroups.find('input[type="checkbox"]:not(:checked) + label').live('click', function (event) {
            var thisGroup = $(this).closest('.filter-group.keyword'),
                thisFilterName = $(this).html();
            if (thisGroup.find('input[type="checkbox"]:checked').length) {
                if (thisGroup.find('input[type="checkbox"][value^="^"][value$="$"]:checked').length === thisGroup.find('input[type="checkbox"]:checked').length
                        && thisFilterName.indexOf('^') === 0
                        && thisFilterName.lastIndexOf('$') === thisFilterName.length - 1) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return true;
            }
        });

        textbox.keyup(function (event) {
            // Updates suggestion-list if typed-text has changed
            if ($(this).val() !== typedText && $(this).val() !== placeholder) {
                updateSuggestions();
            }
        }).keydown(function (event) {
            // If textbox still has fake placeholder text, removes it on keydown for non-meta keys other than shift, ctrl, alt, caps, or esc.
            if (textbox.hasClass('placeholder')) {
                if (!event.metaKey && event.keyCode !== keycodes.SHIFT && event.keyCode !== keycodes.CTRL && event.keyCode !== keycodes.ALT && event.keyCode !== keycodes.CAPS && event.keyCode !== keycodes.ESC) {
                    removeFakePlaceholder();
                }
            }
            // If the suggestion list is not visible...
            if (!suggestionList.is(':visible')) {
                // ...and if the keydown was a non-meta key other than shift, ctrl, alt, caps, or esc...
                if (!event.metaKey && event.keyCode !== keycodes.SHIFT && event.keyCode !== keycodes.CTRL && event.keyCode !== keycodes.ALT && event.keyCode !== keycodes.CAPS && event.keyCode !== keycodes.ESC) {
                    // ...prevent normal TAB function
                    if (event.keyCode === keycodes.TAB && textbox.val() !== '') {
                        event.preventDefault();
                    }
                    // ...submit the form on ENTER if textbox is empty and inputs have changed
                    if (event.keyCode === keycodes.ENTER && textbox.val() === '' && $('.managelist').hasClass('expired')) {
                        formActions.find('button[type="submit"]').click();
                        return false;
                    }
                    // ...update and show the suggestion list
                    updateSuggestions();
                    suggestionList.show();
                }
            // If the suggestion list is already visible...
            } else {
                var thisFilterName = input.filter('#' + suggestionList.find('.selected').data('id')).siblings('label').html();
                // UP and DOWN move "active" suggestion
                if (event.keyCode === keycodes.UP) {
                    event.preventDefault();
                    if (!suggestionList.find('.selected').parent().is(':first-child')) {
                        suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                    }
                    return false;
                }
                if (event.keyCode === keycodes.DOWN) {
                    event.preventDefault();
                    if (!suggestionList.find('.selected').parent().is(':last-child')) {
                        suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                    }
                    return false;
                }
                // ENTER submits the form if textbox is empty and inputs have changed...
                if (event.keyCode === keycodes.ENTER) {
                    event.preventDefault();
                    if (textbox.val() === '' && $('.managelist').hasClass('expired')) {
                        formActions.find('button[type="submit"]').click();
                    // ...otherwise, ENTER selects the "active" filter suggestion.
                    } else {
                        if (suggestionList.find('.selected').length) {
                            suggestionList.find('.selected').click();
                            suggestionList.show();
                        }
                    }
                    return false;
                }
                // TAB auto-completes the "active" suggestion if it isn't already completed...
                if (event.keyCode === keycodes.TAB) {
                    if (thisFilterName && textbox.val().toLowerCase() !== thisFilterName.toLowerCase()) {
                        event.preventDefault();
                        textbox.val(thisFilterName);
                        return false;
                    // ...otherwise, TAB selects the "active" filter suggestion (if exists)
                    } else {
                        if (suggestionList.find('.selected').length) {
                            event.preventDefault();
                            suggestionList.find('.selected').click();
                            suggestionList.show();
                            return false;
                        }
                    }
                }
                // RIGHT auto-completes the "active" suggestion if it isn't already completed
                if (event.keyCode === keycodes.RIGHT) {
                    if (thisFilterName && textbox.val().toLowerCase() !== thisFilterName.toLowerCase()) {
                        event.preventDefault();
                        textbox.val(thisFilterName);
                        return false;
                    }
                }
                // ESC hides the suggestion list
                if (event.keyCode === keycodes.ESC) {
                    event.preventDefault();
                    suggestionList.hide();
                    return false;
                }
                return true;
            }
        // If textbox still has fake placeholder text, removes it on click
        }).click(function () {
            if (textbox.hasClass('placeholder')) {
                removeFakePlaceholder();
            }
        }).focus(function () {
            // Resets textbox data-clicked to ``false`` (becomes ``true`` when an autocomplete suggestion is clicked)
            textbox.data('clicked', false);
            // Adds fake placeholder on initial load (and moves cursor to start of textbox)
            if (textbox.val().length === 0 && textbox.hasClass('placeholder')) {
                textbox.val(placeholder);
                textbox.get(0).setSelectionRange(0, 0);
            }
        // On blur, removes fake placeholder text, and hides the suggestion
        // list after 150 ms if textbox data-clicked is ``false``
        }).blur(function () {
            function hideList() {
                if (textbox.data('clicked') !== true) {
                    suggestionList.hide();
                    textbox.data('clicked', false);
                }
            }
            removeFakePlaceholder();
            window.setTimeout(hideList, 150);
        // Add initial ``placeholder`` class and focus to textbox
        }).addClass('placeholder').focus();

        keywordTextboxes.keydown(function (event) {
            var thisText = $(this).val(),
                thisGroup = $(this).closest('.filter-group.keyword'),
                existingKeyword = thisGroup.find('input[type="checkbox"][value="' + thisText + '"]'),
                groupName = thisGroup.data('name'),
                index = thisGroup.find('input[type="checkbox"]').length + 1,
                newKeywordFilter = ich.keyword_filter({
                    name: groupName,
                    typedText: thisText,
                    index: index
                });
            // ENTER submits the form if textbox is empty and inputs have changed...
            if (event.keyCode === keycodes.ENTER) {
                event.preventDefault();
                if (thisText === '' && $('.managelist').hasClass('expired')) {
                    formActions.find('button[type="submit"]').click();
                    return false;
                }
                if (thisText.length) {
                    // ...otherwise, if the filter already exists, ENTER selects it...
                    if (existingKeyword.length && !existingKeyword.is(':checked') && !thisGroup.find('input[type="checkbox"]:checked').length) {
                        existingKeyword.prop('checked', true);
                        if (existingKeyword.data('originallyChecked') !== existingKeyword.is(':checked')) {
                            existingKeyword.data('state', 'changed');
                        }
                        updateFormActions();
                        $(this).val(null);
                        thisText = null;
                        return false;
                    }
                    // ...otherwise, if the keyword group already has selected filters...
                    if (thisGroup.find('input[type="checkbox"]:checked').length) {
                        // ...and if *all* of the selected filters begin with "^" and end with "$"...
                        if (thisGroup.find('input[type="checkbox"][value^="^"][value$="$"]:checked').length === thisGroup.find('input[type="checkbox"]:checked').length
                                // ...and if the typed-text hasn't already been selected as a filter...
                                && !(thisGroup.find('input[type="checkbox"][value="' + thisText + '"]:checked').length)
                                // ...and if the typed-text begins with "^" and ends with "$"...
                                && thisText.indexOf('^') === 0
                                && thisText.lastIndexOf('$') === thisText.length - 1) {
                            if (existingKeyword.length) {
                                if (!existingKeyword.is(':checked')) {
                                    existingKeyword.prop('checked', true);
                                    if (existingKeyword.data('originallyChecked') !== existingKeyword.is(':checked')) {
                                        existingKeyword.data('state', 'changed');
                                    }
                                    updateFormActions();
                                    $(this).val(null);
                                    thisText = null;
                                    return false;
                                } else { return false; }
                            } else {
                                // ...then add the keyword filter (selected) to this group.
                                $(this).before(newKeywordFilter);
                                $('#id-' + groupName + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true);
                                input = input.add('#id-' + groupName + '-' + index.toString());
                                updateFormActions();
                                $(this).val(null);
                                thisText = null;
                                return false;
                            }
                        }
                    // If there are no other selected filters in this group, just add the new filter.
                    } else {
                        $(this).before(newKeywordFilter);
                        $('#id-' + groupName + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true);
                        input = input.add('#id-' + groupName + '-' + index.toString());
                        updateFormActions();
                        $(this).val(null);
                        thisText = null;
                        return false;
                    }
                }
            }
        });

        suggestionList.find('a').live({
            // Adds ``.selected`` to suggestion on mouseover, removing ``.selected`` from other suggestions
            mouseover: function () {
                var thisSuggestion = $(this).addClass('selected'),
                    otherSuggestions = thisSuggestion.parent('li').siblings('li').find('a').removeClass('selected');
            },
            // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
            mousedown: function () {
                textbox.data('clicked', true);
            },
            click: function (e) {
                e.preventDefault();
                var name, thisFilter, thisGroup, existingKeyword, index, newKeywordFilter;
                // If keyword suggestion clicked...
                if ($(this).data('class') === 'keyword') {
                    name = $(this).data('name');
                    thisGroup = keywordGroups.filter(function () {
                        return $(this).data('name') === name;
                    });
                    existingKeyword = thisGroup.find('input[type="checkbox"][value="' + typedText + '"][name="' + name + '"]');
                    index = thisGroup.find('input[type="checkbox"]').length + 1;
                    newKeywordFilter = ich.keyword_filter({
                        name: name,
                        typedText: typedText,
                        index: index
                    });
                    // ...select it if the filter already exists...
                    if (existingKeyword.length) {
                        existingKeyword.prop('checked', true);
                        if (existingKeyword.data('originallyChecked') !== existingKeyword.is(':checked')) {
                            existingKeyword.data('state', 'changed');
                        }
                    // ...otherwise, append it (selected) to the filters list.
                    } else {
                        thisGroup.removeClass('empty').find('input[type="text"]').before(newKeywordFilter);
                        $('#id-' + name + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true);
                        input = input.add('#id-' + name + '-' + index.toString());
                    }
                // If non-keyword suggestion clicked, select it
                } else {
                    thisFilter = input.filter('#' + $(this).data('id')).prop('checked', true);
                    if (thisFilter.data('originallyChecked') !== thisFilter.is(':checked')) {
                        thisFilter.data('state', 'changed');
                    }
                }
                // Show/hide the form-actions as necessary, reset the textbox, and reset and hide the suggestion list
                updateFormActions();
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        });
    };

    // Ajax-load manage and results list item contents
    module.listDetails = function () {
        $('#listcontent .items .item.details').live('click', function (event) {
            if ($(event.target).is("button, a")) {
                return;
            }
            var item = $(this),
                content = item.find('.content'),
                url = item.data('details-url');
            if (url && !content.hasClass('loaded')) {
                content.css('min-height', '4.854em').addClass('loaded');
                content.loadingOverlay();
                $.get(url, function (data) {
                    content.loadingOverlay('remove');
                    content.html(data.html);
                });
            }
        });
    };

    // Ajax for manage list actions (clone and delete)
    module.manageActionsAjax = function () {
        $('.manage button[name^=action-]').live(
            'click',
            function (e) {
                e.preventDefault();
                var button = $(this),
                    form = button.closest('form'),
                    url = form.prop('action'),
                    method = form.attr('method'),
                    replace = button.closest('.action-ajax-replace'),
                    success = function (response) {
                        var replacement = $(response.html);
                        if (!response.no_replace) {
                            replace.trigger('before-replace', [replacement]);
                            replace.replaceWith(replacement);
                            replacement.trigger('after-replace', [replacement]);
                            replacement.find('.details').html5accordion();
                        }
                        replace.loadingOverlay('remove');
                    },
                    data = {};
                data[button.attr('name')] = button.val();
                replace.loadingOverlay();
                $.ajax(url, {
                    type: method,
                    data: data,
                    success: success
                });
            }
        );
    };

    module.createEnvProfile = function () {
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
            if (event.keyCode === keycodes.ENTER) {
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
            if (event.keyCode === keycodes.ENTER) {
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
            if (event.keyCode === keycodes.ENTER) {
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
            if (event.keyCode === keycodes.ENTER) {
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

    module.editEnvProfile = function () {
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
                            if (!event.metaKey && event.keyCode !== keycodes.SHIFT && event.keyCode !== keycodes.CTRL && event.keyCode !== keycodes.ALT && event.keyCode !== keycodes.CAPS && event.keyCode !== keycodes.ESC) {
                                // ...prevent normal TAB function
                                if (event.keyCode === keycodes.TAB || event.keyCode === keycodes.ENTER) {
                                    event.preventDefault();
                                }
                                // ...show the suggestion list
                                suggestionList.show();
                            }
                        // If the textbox is empty...
                        } else {
                            // ...and if the keydown was ENTER...
                            if (event.keyCode === keycodes.ENTER) {
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
                        if (event.keyCode === keycodes.UP) {
                            event.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':first-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                            }
                            return false;
                        }
                        if (event.keyCode === keycodes.DOWN) {
                            event.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':last-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                            }
                            return false;
                        }
                        // ENTER selects the "active" filter suggestion.
                        if (event.keyCode === keycodes.ENTER) {
                            event.preventDefault();
                            if (suggestionList.find('.selected').length) {
                                suggestionList.find('.selected').click();
                            }
                            return false;
                        }
                        // TAB auto-completes the "active" suggestion if it isn't already completed...
                        if (event.keyCode === keycodes.TAB) {
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
                        if (event.keyCode === keycodes.RIGHT) {
                            if (thisSuggestionName && addEnvTextbox.val().toLowerCase() !== thisSuggestionName.toLowerCase()) {
                                event.preventDefault();
                                addEnvTextbox.val(thisSuggestionName);
                                return false;
                            }
                        }
                        // ESC hides the suggestion list
                        if (event.keyCode === keycodes.ESC) {
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
            if (event.keyCode === keycodes.ENTER && !profileNameSubmit.is(':visible')) {
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

    module.slideshow = function (contextSelector, containerSelector, slidesSelector, slideLinksSelector) {
        var hash,
            context = $(contextSelector),
            container = context.find(containerSelector),
            slides = context.find(slidesSelector),
            slideLinks = context.find(slideLinksSelector),
            showSlide = function (slide) {
                var thisLink = slideLinks.filter('a[href="#' + $(slide).attr('id') + '"]');
                $(slide).addClass('active-slide').removeClass('inactive-slide');
                $(slide).siblings().removeClass('active-slide').addClass('inactive-slide').fadeOut('fast', function () {
                    $(slide).fadeIn('fast');
                });
                slideLinks.removeClass('active');
                thisLink.addClass('active');
            };

        slideLinks.click(function (e) {
            e.preventDefault();
            showSlide($(this).attr('href'));
            $(this).blur();
        });

        if (window.location.hash.length) {
            hash = window.location.hash.substring(1);
            if (slides.filter('[id^="' + hash + '"]').length) {
                showSlide(slides.filter('[id^="' + hash + '"]'));
            }
        }
    };

    module.addEllipses = function () {
        $('#listcontent .items').find('.title, .product, .cycle, .run').ellipsis().each(function () {
            $(this).data('oldWidth', $(this).width());
        });
        $(window).resize(function () {
            $.doTimeout('resize', 300, function () {
                $('#listcontent .items').find('.title, .product, .cycle, .run').each(function () {
                    if ($(this).width() !== $(this).data('oldWidth')) {
                        $(this).data('oldWidth', $(this).width()).ellipsis();
                    }
                });
            });
        });
    };

    $(function () {
        module.filtering();
        module.listDetails();
        module.manageActionsAjax();
        module.createEnvProfile();
        module.editEnvProfile();
        module.slideshow('#addcase', '.forms', '.forms form[id$="-case-form"]', 'a[href^="#"][href$="-case-form"]');
        $('.details:not(html)').html5accordion();
        $('#messages').messages({
            handleAjax: true,
            closeLink: '.message'
        });
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input:not([type=radio], [type=checkbox]), textarea').live('blur', function () {
            $(this).addClass('hadfocus');
        });
        module.formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        module.formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");
        $('.selectruns').html5finder({
            loading: true,
            ellipsis: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]'
            ],
            callback: function () {
                $('.selectruns + .environment').slideUp('fast');
            },
            lastChildCallback: function (choice) {
                var environments = $('.selectruns + .environment').css('min-height', '169px').slideDown('fast'),
                    ajaxUrl = $(choice).data("sub-url");
                environments.loadingOverlay();
                $.get(ajaxUrl, function (data) {
                    environments.loadingOverlay('remove');
                    environments.html(data.html);
                });
            }
        });
        $('.selectruns + .environment.empty').hide();
        $('.managedrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            ellipsis: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'suites'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]',
                'input[name="testsuite"]'
            ]
        });
        $('.resultsdrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            ellipsis: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'cases'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]',
                'input[name="testrunincludedtestcase"]'
            ]
        });
    });

    $(window).load(function () {
        module.addEllipses();
        // Expand list item details on direct hashtag links
        if ($('.manage').length && window.location.hash) {
            $(window.location.hash).children('.summary').click();
        }
    });

    return module;

}(CC || {}, jQuery));