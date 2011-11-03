/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery, ich */

/**
 * jQuery Custom Autocomplete 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    // Add cache to avoid repeated duplicate Ajax calls
    var cache = {};

    $.fn.customAutocomplete = function (opts) {
        var options = $.extend({}, $.fn.customAutocomplete.defaults, opts),
            keycodes = $.fn.customAutocomplete.keycodes,
            context = $(this),
            textbox = context.find(options.textbox),
            formActions = context.find(options.formActions),
            suggestionList = context.find(options.suggestionList),
            inputList = context.find(options.inputList),
            newInputList = context.find(options.newInputList),
            inputs = inputList.add(newInputList).find(options.inputs),
            newInputTextbox = newInputList.find(options.newInputTextbox),
            expiredList = context.find(options.expiredList),
            placeholder = textbox.attr('placeholder'),
            url = options.url,
            prefix = options.prefix,
            newInputCounter = 1,
            newSuggestions,
            filteredSuggestions,
            typedText,

            // Removes (faked) placeholder text from textbox
            removeFakePlaceholder = function () {
                if (textbox.val().indexOf(placeholder) !== -1) {
                    textbox.val(null);
                }
                textbox.removeClass('placeholder');
            },

            // Checks if any inputs have changed from original-state,
            // showing form-actions and adding ``.expired`` if any inputs have changed.
            updateFormActions = function () {
                if (inputs.filter(function () { return $(this).data('state') === 'changed'; }).length) {
                    expiredList.addClass('expired');
                    if (options.hideFormActions) {
                        formActions.fadeIn('fast');
                    }
                } else {
                    expiredList.removeClass('expired');
                    if (options.hideFormActions) {
                        formActions.fadeOut('fast');
                    }
                }

                if (options.noInputsNote) {
                    var noInputsNote = ich.autocomplete_no_inputs();
                    inputList.add(newInputList).each(function () {
                        if ($(this).find(options.inputs).length) {
                            $(this).find('.none').remove();
                        } else {
                            if ($(this).children('ul').length) {
                                $(this).children('ul').append(noInputsNote);
                            } else {
                                $(this).append(noInputsNote);
                            }
                        }
                    });
                }
            },

            // Used if there are specific restrictions on new inputs
            passRestrictedNewInputs = function (thisGroup, newInputName) {
                // If the group already has selected inputs...
                if (thisGroup.find(options.inputs + ':checked').length) {
                    // ...and if *all* of the selected inputs begin with "^" and ends with "$"...
                    if (thisGroup.find(options.inputs + '[value^="^"][value$="$"]:checked').length === thisGroup.find(options.inputs + ':checked').length
                            // ...and if the typed-text hasn't already been selected as an input, and if the typed-text begins with "^" and ends with "$"...
                            && !(thisGroup.find(options.inputs + '[value="' + newInputName.toString().toLowerCase() + '"]:checked').length)
                            && newInputName.indexOf('^') === 0
                            && newInputName.lastIndexOf('$') === newInputName.length - 1) {
                        // ...then append the new suggestion to the suggestion-list.
                        return true;
                    } else {
                        return false;
                    }
                } else {
                    return true;
                }
            },

            // Filter autocomplete suggestions, returning those that aren't duplicates.
            filterSuggestions = function () {
                filteredSuggestions = newSuggestions.filter(function () {
                    var thisSuggestionID = $(this).find('a').data('id'),
                        thisSuggestionName = $(this).find('a').data('name'),
                        thisSuggestionType = $(this).find('a').data('type');
                    if (thisSuggestionName && !options.caseSensitive) { thisSuggestionName = thisSuggestionName.toString().toLowerCase(); }
                    if ($(this).find('a').hasClass('new')) {
                        if (inputs.filter('[id^="id-' + prefix + '-' + thisSuggestionType + '-"]:checked').filter(function () { return $(this).siblings('label').text() === thisSuggestionName; }).length
                                || inputs.filter('[id^="id-' + prefix + '-new' + thisSuggestionType + '-"]:checked').filter(function () { return $(this).siblings('label').text() === thisSuggestionName; }).length
                                || newSuggestions.find('a:not(.new)').filter(function () { return $(this).data('name') === thisSuggestionName && $(this).data('type') === thisSuggestionType; }).length) {
                            return false;
                        } else {
                            return true;
                        }
                    } else {
                        if (inputs.filter('[id^="id-' + prefix + '-' + thisSuggestionType + '-"][value="' + thisSuggestionID + '"]:checked').length) {
                            return false;
                        } else {
                            return true;
                        }
                    }
                });
            },

            // Create list of autocomplete suggestions from Ajax response or existing list of inputs
            updateSuggestions = function (data, cached) {
                if (!data && !options.ajax) {
                    var suggestions;
                    if (options.caseSensitive) {
                        suggestions = inputList.find(options.inputs).parent('li').filter(function () {
                            return $(this).children('label').text().indexOf(typedText) !== -1;
                        });
                    } else {
                        suggestions = inputList.find(options.inputs).parent('li').filter(function () {
                            return $(this).children('label').text().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                        });
                    }
                    data = {};
                    data.suggestions = [];
                    suggestions.each(function () {
                        var typedIndex,
                            thisSuggestion = {};
                        if (options.caseSensitive) {
                            typedIndex = $(this).children('label').text().indexOf(typedText);
                        } else {
                            typedIndex = $(this).children('label').text().toLowerCase().indexOf(typedText.toLowerCase());
                        }
                        thisSuggestion.typedText = typedText;
                        thisSuggestion.name = $(this).children('label').text();
                        thisSuggestion.preText = $(this).children('label').text().substring(0, typedIndex);
                        thisSuggestion.postText = $(this).children('label').text().substring(typedIndex + typedText.length);
                        thisSuggestion.id = $(this).children('input').attr('value');
                        if (options.multipleCategories) {
                            thisSuggestion.type = $(this).children('input').data('name');
                            if ($(this).closest(options.inputList).find('.category-title').length) {
                                thisSuggestion.displayType = $(this).closest(options.inputList).find('.category-title').text();
                            }
                        }
                        data.suggestions.push(thisSuggestion);
                    });
                }

                if (options.allowNew && !cached) {
                    newInputList.each(function () {
                        var thisSuggestion = {};
                        thisSuggestion.typedText = typedText;
                        thisSuggestion.name = typedText;
                        thisSuggestion.id = typedText;
                        thisSuggestion.newSuggestion = true;
                        if (options.multipleCategories) {
                            thisSuggestion.type = $(this).data('name');
                            if ($(this).find('.category-title').length) {
                                thisSuggestion.displayType = $(this).find('.category-title').text();
                            }
                        } else {
                            thisSuggestion.type = options.inputType;
                        }

                        if (options.restrictNewInputs) {
                            if (passRestrictedNewInputs($(this), typedText)) {
                                data.suggestions.unshift(thisSuggestion);
                            }
                        } else {
                            data.suggestions.unshift(thisSuggestion);
                        }
                    });
                }

                newSuggestions = ich.autocomplete_suggestion(data);
                filterSuggestions();
                suggestionList.html(filteredSuggestions);

                // Show suggestion list if it contains suggestions; otherwise, hide it.
                if (suggestionList.find('li').length) {
                    suggestionList.show();
                } else {
                    suggestionList.hide();
                }

                // Adds ".selected" to first autocomplete suggestion.
                if (!(suggestionList.find('.selected').length)) {
                    suggestionList.find('li:first-child a').addClass('selected');
                }
            };

        suggestionList.hide();

        if (options.hideFormActions) {
            formActions.hide();
        }

        if (options.fakePlaceholder) {
            textbox.addClass('placeholder');
        }

        if (!options.multipleCategories && options.newInputList === null) {
            newInputList = context.find(options.inputList);
            newInputTextbox = newInputList.find(options.newInputTextbox);
            options.newInputList = options.inputList;
        }

        if (!expiredList.length) {
            expiredList = $(options.expiredList);
        }

        // Set data-originallyChecked on each input to store original state
        inputs.each(function () {
            $(this).data('originallyChecked', $(this).is(':checked'));
        });

        // Reset button sets each input to its original state, hides form-actions
        // and suggestion-list, and returns focus to the textbox.
        formActions.find(options.reset).click(function (e) {
            e.preventDefault();
            if (options.hideFormActions) {
                formActions.fadeOut('fast');
            }
            expiredList.removeClass('expired');
            inputs.each(function () {
                $(this).removeData('state');
                $(this).prop('checked', $(this).data('originallyChecked')).change();
            });
            textbox.focus();
            suggestionList.hide();
        });

        // Selecting/unselecting an input returns focus to textbox, hides
        // suggestion-list, sets data-state "changed" if input has changed from
        // original state, and shows/hides form-actions as appropriate.
        if (options.inputsNeverRemoved) {
            inputList.add(newInputList).delegate(options.inputs, 'change', function () {
                if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                    $(this).data('state', 'changed');
                } else {
                    $(this).removeData('state');
                }
                textbox.focus();
                suggestionList.hide();
                updateFormActions();
            });
        }

        // If there are any new inputs already selected, prevent a new input from being selected
        // unless it and all new inputs begin with ^ and end with $.
        if (options.restrictNewInputs && options.inputsNeverRemoved) {
            newInputList.delegate(options.inputs + ':not(:checked) + label', 'click', function (e) {
                var thisGroup = $(this).closest(options.newInputList),
                    thisInputName = $(this).text();
                if (!passRestrictedNewInputs(thisGroup, thisInputName)) {
                    textbox.focus();
                    e.preventDefault();
                }
            });
        }

        textbox
            .keyup(function (e) {
                // Updates suggestion-list if typed-text has changed
                var updateSuggestionList = function () {
                    if (textbox.val() !== typedText && textbox.val() !== placeholder) {
                        typedText = textbox.val();
                        if (typedText.length) {
                            if (options.ajax) {
                                if (cache[typedText]) {
                                    updateSuggestions(cache[typedText], true);
                                } else {
                                    $.get(options.url, {text: typedText}, function (response) {
                                        cache[typedText] = response;
                                        updateSuggestions(response, false);
                                    });
                                }
                            } else {
                                updateSuggestions();
                            }
                        } else {
                            suggestionList.empty().hide();
                        }
                    }
                };
                if (options.ajax) {
                    $(this).doTimeout(150, function () {
                        updateSuggestionList();
                    });
                } else {
                    updateSuggestionList();
                }
            })
            .keydown(function (e) {
                // Prevent default actions on ENTER
                if (e.keyCode === keycodes.ENTER) {
                    e.preventDefault();
                }
                // If textbox has fake placeholder text, removes it on keydown for non-meta keys other than shift, ctrl, alt, caps, or esc.
                if (textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    if (!e.metaKey && e.keyCode !== keycodes.SHIFT && e.keyCode !== keycodes.CTRL && e.keyCode !== keycodes.ALT && e.keyCode !== keycodes.CAPS && e.keyCode !== keycodes.ESC) {
                        removeFakePlaceholder();
                    }
                }
                // If the suggestion list is not visible...
                if (!suggestionList.is(':visible')) {
                    // ...prevent normal TAB function, and show suggestion list
                    if (e.keyCode === keycodes.TAB && textbox.val() !== '' && suggestionList.find('li').length) {
                        e.preventDefault();
                        suggestionList.show();
                    }
                    // ...perform submit action on ENTER if textbox is empty and inputs have changed
                    if (e.keyCode === keycodes.ENTER && textbox.val() === '' && expiredList.hasClass('expired')) {
                        options.triggerSubmit(context);
                    }
                    // ...show the suggestion list on arrow-keys
                    if (e.keyCode === keycodes.UP || e.keyCode === keycodes.DOWN || e.keyCode === keycodes.LEFT || e.keyCode === keycodes.RIGHT) {
                        if (suggestionList.find('li').length) {
                            suggestionList.show();
                        }
                    }
                // If the suggestion list is already visible...
                } else {
                    var thisInputName = suggestionList.find('.selected').data('name');
                    // UP and DOWN move "active" suggestion
                    if (e.keyCode === keycodes.UP) {
                        e.preventDefault();
                        if (!suggestionList.find('.selected').parent().is(':first-child')) {
                            suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                        }
                    }
                    if (e.keyCode === keycodes.DOWN) {
                        e.preventDefault();
                        if (!suggestionList.find('.selected').parent().is(':last-child')) {
                            suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                        }
                    }
                    // ENTER performs submit action if textbox is empty and inputs have changed...
                    if (e.keyCode === keycodes.ENTER) {
                        e.preventDefault();
                        if (textbox.val() === '' && expiredList.hasClass('expired')) {
                            options.triggerSubmit(context);
                        // ...otherwise, ENTER selects the "active" suggestion.
                        } else {
                            if (suggestionList.find('.selected').length) {
                                suggestionList.find('.selected').click();
                            }
                        }
                    }
                    // TAB auto-completes the "active" suggestion if it isn't already completed...
                    if (e.keyCode === keycodes.TAB) {
                        if (thisInputName && textbox.val().toLowerCase() !== thisInputName.toString().toLowerCase()) {
                            e.preventDefault();
                            textbox.val(thisInputName);
                        // ...otherwise, TAB selects the "active" suggestion (if exists)
                        } else if (suggestionList.find('.selected').length) {
                            e.preventDefault();
                            suggestionList.find('.selected').click();
                        }
                    }
                    // RIGHT auto-completes the "active" suggestion if it isn't already completed
                    // and the cursor is at the end of the textbox
                    if (e.keyCode === keycodes.RIGHT) {
                        if (thisInputName && textbox.val().toLowerCase() !== thisInputName.toString().toLowerCase() && textbox.get(0).selectionStart === textbox.val().length) {
                            e.preventDefault();
                            textbox.val(thisInputName);
                        }
                    }
                    // ESC hides the suggestion list
                    if (e.keyCode === keycodes.ESC) {
                        e.preventDefault();
                        suggestionList.hide();
                    }
                }
            })
            // If textbox still has fake placeholder text, remove it on click
            .click(function () {
                if (textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    removeFakePlaceholder();
                }
            })
            .focus(function () {
                // Resets textbox data-clicked to "false" (becomes "true" when an autocomplete suggestion is clicked)
                textbox.data('clicked', false);
                // Adds fake placeholder on initial page load (and moves cursor to start of textbox)
                if (textbox.val().length === 0 && textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    textbox.val(placeholder);
                    textbox.get(0).setSelectionRange(0, 0);
                }
            })
            // On blur, removes fake placeholder text, and hides the suggestion
            // list after 150 ms if textbox data-clicked is "false"
            .blur(function () {
                function hideList() {
                    if (textbox.data('clicked') !== true) {
                        suggestionList.hide();
                        textbox.data('clicked', false);
                    }
                }
                if (options.fakePlaceholder) {
                    removeFakePlaceholder();
                }
                window.setTimeout(hideList, 150);
            });

        if (options.initialFocus) {
            textbox.focus();
        }

        suggestionList.delegate('a', {
            // Adds ".selected" to suggestion on mouseover, removing ".selected" from other suggestions
            mouseover: function () {
                var thisSuggestion = $(this).addClass('selected'),
                    otherSuggestions = thisSuggestion.parent('li').siblings('li').find('a').removeClass('selected');
            },
            // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
            mousedown: function () {
                textbox.data('clicked', true);
            },
            // Add new input or select existing input when suggestion is clicked
            click: function (e) {
                e.preventDefault();
                var thisGroup, thisTypeName, existingNewInput, index, newInput, thisInput,
                    thisID = $(this).data('id'),
                    inputName = $(this).data('name');
                if (options.multipleCategories) {
                    thisTypeName = $(this).data('type');
                } else {
                    thisTypeName = options.inputType;
                }
                if (!options.caseSensitive) {
                    inputName = inputName.toString().toLowerCase();
                }
                thisInput = inputs.filter('[id^="id-' + prefix + '-' + thisTypeName + '-"][value="' + thisID + '"]');
                // If there's an existing non-new input, select it...
                if (thisInput.length) {
                    thisInput.prop('checked', true).change();
                    if (thisInput.data('originallyChecked') !== thisInput.is(':checked')) {
                        thisInput.data('state', 'changed');
                    }
                } else {
                    if (options.multipleCategories) {
                        thisGroup = newInputList.filter(function () {
                            return $(this).data('name') === thisTypeName;
                        });
                    } else {
                        thisGroup = newInputList;
                    }
                    if (options.inputsNeverRemoved) {
                        index = thisGroup.find(options.inputs).length + 1;
                    } else {
                        index = newInputCounter;
                        newInputCounter = newInputCounter + 1;
                    }
                    // If we're dealing with a new input...
                    if ($(this).hasClass('new') && options.allowNew) {
                        if (!options.multipleCategories) {
                            thisTypeName = 'new' + thisTypeName;
                        }
                        newInput = ich.autocomplete_input({
                            typeName: thisTypeName,
                            inputName: inputName,
                            id: inputName,
                            index: index,
                            newInput: true,
                            prefix: prefix
                        });
                        existingNewInput = thisGroup.find(options.inputs + '[value="' + inputName + '"]');
                        // ...select it if it already exists...
                        if (existingNewInput.length && options.inputsNeverRemoved) {
                            existingNewInput.prop('checked', true).change();
                            if (existingNewInput.data('originallyChecked') !== existingNewInput.is(':checked')) {
                                existingNewInput.data('state', 'changed');
                            }
                        } else {
                            // ...or add it if it doesn't already exist.
                            if (thisGroup.find(options.newInputTextbox).length) {
                                thisGroup.removeClass('empty').find(options.newInputTextbox).parent('li').before(newInput);
                            } else {
                                if (thisGroup.children('ul').length) {
                                    thisGroup.removeClass('empty').children('ul').append(newInput);
                                } else {
                                    thisGroup.removeClass('empty').append(newInput);
                                }
                            }
                            $('#id-' + prefix + '-' + thisTypeName + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true).change();
                            inputs = inputList.add(newInputList).find(options.inputs);
                        }
                    } else {
                        // Otherwise, simply add the input.
                        newInput = ich.autocomplete_input({
                            typeName: thisTypeName,
                            inputName: inputName,
                            id: thisID,
                            index: index,
                            prefix: prefix
                        });
                        if (thisGroup.children('ul').length) {
                            thisGroup.removeClass('empty').children('ul').append(newInput);
                        } else {
                            thisGroup.removeClass('empty').append(newInput);
                        }
                        $('#id-' + prefix + '-' + thisTypeName + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true).change();
                        inputs = inputList.add(newInputList).find(options.inputs);
                    }
                }
                // Update ``.expired`` and form-actions as necessary, empty the textbox, and empty and hide the suggestion list
                updateFormActions();
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        });

        // Remove inputs and update suggestion list when unchecked.
        if (!options.inputsNeverRemoved) {
            inputList.add(newInputList).delegate('label', 'click', function (e) {
                e.preventDefault();
                $(this).parent().remove();
                inputs = inputList.add(newInputList).find(options.inputs);
                if (newSuggestions) {
                    filterSuggestions();
                    suggestionList.hide().html(filteredSuggestions);
                    // Adds ".selected" to first autocomplete suggestion.
                    if (!(suggestionList.find('.selected').length)) {
                        suggestionList.find('li:first-child a').addClass('selected');
                    }
                }
                updateFormActions();
            });
        }

        // Allow adding new inputs via group-specific textbox
        newInputTextbox.each(function () {
            $(this).keydown(function (e) {
                var thisTextbox = $(this),
                    thisText = options.caseSensitive ? thisTextbox.val() : thisTextbox.val().toLowerCase(),
                    thisGroup = thisTextbox.closest(options.newInputList),
                    existingInput = thisGroup.find(options.inputs + '[value="' + thisText + '"]'),
                    typeName = thisGroup.data('name'),
                    index = thisGroup.find(options.inputs).length + 1,
                    newInput = ich.autocomplete_input({
                        typeName: typeName,
                        inputName: thisText,
                        id: thisText,
                        index: index,
                        newInput: true,
                        prefix: prefix
                    }),
                    addInput = function () {
                        newInput.insertBefore(thisTextbox.parent('li'));
                        $('#id-' + prefix + '-' + typeName + '-' + index.toString()).data('state', 'changed').data('originallyChecked', false).prop('checked', true).change();
                        thisGroup.removeClass('empty');
                        inputs = inputs.add('#id-' + prefix + '-' + typeName + '-' + index.toString());
                        updateFormActions();
                        thisTextbox.val(null);
                        thisText = null;
                    },
                    selectInput = function () {
                        existingInput.prop('checked', true).change();
                        if (existingInput.data('originallyChecked') !== existingInput.is(':checked')) {
                            existingInput.data('state', 'changed');
                        }
                        updateFormActions();
                        thisTextbox.val(null);
                        thisText = null;
                    };
                // ENTER performs submit action if textbox is empty and inputs have changed...
                if (e.keyCode === keycodes.ENTER) {
                    e.preventDefault();
                    if (thisText === '' && expiredList.hasClass('expired')) {
                        options.triggerSubmit(context);
                    } else if (thisText.length) {
                        // ...otherwise, if the input already exists, ENTER selects it...
                        if (existingInput.length && !existingInput.is(':checked') && !thisGroup.find(options.inputs + ':checked').length) {
                            selectInput();
                        } else if (options.restrictNewInputs && passRestrictedNewInputs(thisGroup, thisText)) {
                            addInput();
                        }
                    }
                }
            });
        });
    };

    // Store keycode variables for easier readability
    $.fn.customAutocomplete.keycodes = {
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

    /* Setup plugin defaults */
    $.fn.customAutocomplete.defaults = {
        textbox: '#autocomplete-textbox',               // Selector for autocomplete textbox
        inputs: 'input[type="checkbox"]',               // Selector for inputs
        formActions: '.form-actions',                   // Selector for form-actions (only needed if ``hideFormActions: true``)
        suggestionList: '.textual .suggest',            // Selector for list of autocomplete suggestions
        inputList: '.visual',                           // Selector for list of inputs
        ajax: false,                                    // Set ``true`` if using Ajax to retrieve autocomplete suggestions
        url: null,                                      // Ajax url (only needed if ``ajax: true``)
        triggerSubmit: function (context) {             // Function to be executed on ENTER in empty textbox
            context.find('.form-actions button[type="submit"]').click();
        },
        hideFormActions: false,                         // Set ``true`` if form actions should be hidden when inputs are unchanged
        multipleCategories: false,                      // Set ``true`` if inputs are separated into categorized groups
        allowNew: false,                                // Set ``true`` if new inputs (neither existing nor returned via Ajax) are allowed
        newInputList: null,                             // Selector for list of new inputs (only needed if ``allowNew: true``
                                                        //      and ``multipleCategories: true``)
        restrictNewInputs: false,                       // Set ``true`` if new inputs should be restricted to use ^ and $
        newInputTextbox: null,                          // Selector for secondary textbox to enter new group-specific inputs
        fakePlaceholder: false,                         // Set ``true`` to create fake placeholder text when using ``initialFocus: true``
        expiredList: null,                              // Selector for setting ``.expired`` when inputs have changed
        initialFocus: false,                            // Set ``true`` to give textbox focus on initial page load
        reset: '.reset',                                // Selector for button to reset all inputs to original state
        inputType: null,                                // Name for input types when using only one category of inputs
        inputsNeverRemoved: false,                      // Set ``true`` if non-new inputs are never added or removed (only checked or unchecked)
        caseSensitive: false,                           // Set ``true`` if inputs should be treated as case-sensitive
        prefix: '',                                     // Prefix to apply to each input ID (to avoid ID duplication when using multiple times on one page)
        noInputsNote: false                             // Set ``true`` to add "none" when no there are no inputs
    };

}(jQuery));