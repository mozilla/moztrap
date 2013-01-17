/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    jQuery, ich */

/**
 * jQuery Custom Autocomplete 0.2
 *
 * Copyright (c) 2012, Jonny Gerig Meyer
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
            origInputs = inputList.html(),
            origNewInputs = newInputList.html(),
            inputs = inputList.add(newInputList).find(options.inputs),
            newInputTextbox = newInputList.find(options.newInputTextbox),
            placeholder = textbox.attr('placeholder'),
            url = options.url,
            prefix = options.prefix,
            newInputCounter = 1,
            newSuggestions,
            filteredSuggestions,
            typedText,
            ajaxCalls = 0,
            ajaxResponses = 0,

            // Removes (faked) placeholder text from textbox
            removeFakePlaceholder = function () {
                if (textbox.val().indexOf(placeholder) !== -1) {
                    textbox.val(null);
                }
                textbox.removeClass('placeholder');
            },

            // Submits form, adds no-inputs note, or shows/hides form-actions when inputs change
            inputsChanged = function () {
                if (options.autoSubmit) {
                    options.triggerSubmit(context);
                }

                if (options.hideFormActions) {
                    if (inputList.html() !== origInputs && newInputList.html() !== origNewInputs) {
                        formActions.fadeIn();
                    } else {
                        formActions.fadeOut();
                    }
                }

                if (options.noInputsNote) {
                    var noInputsNote = ich.autocomplete_no_inputs({ prefix: prefix });
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

            // Filter autocomplete suggestions, returning those that aren't duplicates.
            filterSuggestions = function () {
                filteredSuggestions = newSuggestions.filter(function () {
                    var thisSuggestionID = $(this).find('a').data('id'),
                        thisSuggestionName = $(this).find('a').data('name'),
                        thisSuggestionType = $(this).find('a').data('type');
                    if (thisSuggestionName && !options.caseSensitive) { thisSuggestionName = thisSuggestionName.toString().toLowerCase(); }
                    if ($(this).find('a').hasClass('new')) {
                        if (inputs.filter('[id^="id-' + prefix + '-' + thisSuggestionType + '-"]:checked').filter(function () { return $(this).closest('li[class$="item"]').find('label').text() === thisSuggestionName; }).length
                                || inputs.filter('[id^="id-' + prefix + '-new' + thisSuggestionType + '-"]:checked').filter(function () { return $(this).closest('li[class$="item"]').find('label').text() === thisSuggestionName; }).length
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
                var extraDataName, suggestions;
                if (!data && !options.ajax) {
                    if (options.caseSensitive) {
                        suggestions = inputList.find(options.inputs).not(':disabled').closest('li[class$="item"]').filter(function () {
                            return $(this).find('label').text().indexOf(typedText) !== -1;
                        });
                    } else {
                        suggestions = inputList.find(options.inputs).not(':disabled').closest('li[class$="item"]').filter(function () {
                            return $(this).find('label').text().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                        });
                    }
                    data = {};
                    data.suggestions = [];
                    suggestions.each(function () {
                        var typedIndex,
                            thisSuggestion = {};
                        if (options.caseSensitive) {
                            typedIndex = $(this).find('label').text().indexOf(typedText);
                        } else {
                            typedIndex = $(this).find('label').text().toLowerCase().indexOf(typedText.toLowerCase());
                        }
                        thisSuggestion.typedText = typedText;
                        thisSuggestion.name = $(this).find('label').text();
                        thisSuggestion.preText = $(this).find('label').text().substring(0, typedIndex);
                        thisSuggestion.postText = $(this).find('label').text().substring(typedIndex + typedText.length);
                        thisSuggestion.id = $(this).find('input').attr('value');
                        if (options.multipleCategories) {
                            thisSuggestion.type = $(this).find('input').data('name');
                            if ($(this).closest(options.inputList).find('.category-title').length) {
                                thisSuggestion.displayType = $(this).closest(options.inputList).find('.category-title').text();
                            }
                        }
                        data.suggestions.push(thisSuggestion);
                    });
                }

                if (options.allowNew && !cached) {
                    if (!(options.restrictAllowNew && textbox.data('allow-new') !== true)) {
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

                            data.suggestions.unshift(thisSuggestion);
                        });
                    }
                }

                if (options.extraDataName) {
                    extraDataName = options.extraDataName;
                    $.each(data.suggestions, function (index, value) {
                        if (this[extraDataName]) {
                            this.responseDataName = extraDataName;
                            this.responseDataVal = this[extraDataName];
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

        // Hide suggestion-list on initial page-load
        suggestionList.hide();

        // Optionally hide form-actions on initial page-load
        if (options.hideFormActions) {
            formActions.hide();
        }

        // Optionally add fake placeholder text on initial page-load
        // (this allows textbox to initially have focus and a placeholder)
        if (options.fakePlaceholder) {
            textbox.addClass('placeholder');
        }

        // Set newInputList to inputList if only one category
        if (!options.multipleCategories && options.newInputList === null) {
            newInputList = context.find(options.inputList);
            newInputTextbox = newInputList.find(options.newInputTextbox);
            options.newInputList = options.inputList;
        }

        // Selecting/unselecting an input returns focus to textbox and hides suggestion-list
        inputList.add(newInputList).on('change', options.inputs, function () {
            textbox.focus();
            suggestionList.hide();
            inputsChanged();
        });

        textbox
            .keyup(function (e) {
                // Updates suggestion-list if typed-text has changed
                var updateSuggestionList = function () {
                    var data,
                        serializedData,
                        extraData = {},
                        extraDataName,
                        extraDataVal;
                    if (textbox.val() !== typedText && textbox.val() !== placeholder) {
                        typedText = textbox.val();
                        if (typedText.length && typedText.trim() !== '') {
                            if (options.ajax) {
                                if (options.extraDataName && options.extraDataFn) {
                                    extraDataName = options.extraDataName;
                                    extraDataVal = options.extraDataFn();
                                    extraData[extraDataName] = extraDataVal;
                                }
                                data = $.extend({}, extraData, {text: typedText});
                                serializedData = $.param(data);
                                if (cache[serializedData]) {
                                    updateSuggestions(cache[serializedData], true);
                                } else {
                                    ajaxCalls = ajaxCalls + 1;
                                    $.get(options.url, data, function (response) {
                                        ajaxResponses = ajaxResponses + 1;
                                        cache[serializedData] = response;
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
                if (options.ajax || options.debounce) {
                    $(this).doTimeout('autocomplete', 200, function () {
                        updateSuggestionList();
                    });
                } else {
                    updateSuggestionList();
                }
            })
            .keydown(function (e) {
                // If textbox has fake placeholder text, removes it on keydown for non-meta keys other than shift, ctrl, alt, caps, or esc.
                if (textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    if (!e.metaKey && e.keyCode !== keycodes.SHIFT && e.keyCode !== keycodes.CTRL && e.keyCode !== keycodes.ALT && e.keyCode !== keycodes.CAPS && e.keyCode !== keycodes.ESC) {
                        removeFakePlaceholder();
                    }
                }
                // Submit form if textbox is empty and form-actions are visible
                if (e.keyCode === keycodes.ENTER && textbox.val() === '' && formActions.is(':visible') && !options.autoSubmit) {
                    e.preventDefault();
                    options.triggerSubmit(context);
                } else {
                    // If the suggestion list is not visible...
                    if (!suggestionList.is(':visible')) {
                        // ...prevent normal TAB function, and show suggestion list
                        if (e.keyCode === keycodes.TAB && textbox.val() !== '' && suggestionList.find('li').length) {
                            e.preventDefault();
                            suggestionList.show();
                        }
                        // ...show suggestion list on ENTER
                        if (e.keyCode === keycodes.ENTER) {
                            e.preventDefault();
                            if (suggestionList.find('li').length) {
                                suggestionList.show();
                            }
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
                        // ENTER selects the "active" suggestion, if exists.
                        if (e.keyCode === keycodes.ENTER) {
                            e.preventDefault();
                            if (suggestionList.find('.selected').length) {
                                $.doTimeout(100, function () {
                                    if (ajaxCalls === ajaxResponses) {
                                        suggestionList.find('.selected').click();
                                        return false;
                                    }
                                    return true;
                                });
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

        // Optionally give textbox initial focus on page-load
        if (options.initialFocus) {
            textbox.focus();
        }

        suggestionList.on({
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
                var thisGroup, thisTypeName, existingNewInput, index, newInput, thisInput, data,
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
                        data = {
                            typeName: thisTypeName,
                            inputName: inputName,
                            id: inputName,
                            index: index,
                            newInput: true,
                            prefix: prefix,
                            pinable: options.pinable
                        };
                        if ($(this).data(options.extraDataName)) {
                            data.responseDataName = options.extraDataName;
                            data.responseDataVal = $(this).data(options.extraDataName);
                        }
                        newInput = ich.autocomplete_input(data);
                        existingNewInput = thisGroup.find(options.inputs + '[value="' + inputName + '"]');
                        // ...select it if it already exists...
                        if (existingNewInput.length && options.inputsNeverRemoved) {
                            existingNewInput.prop('checked', true).change();
                        } else {
                            // ...or add it if it doesn't already exist.
                            if (thisGroup.children('ul').length) {
                                thisGroup.removeClass('empty').children('ul').append(newInput);
                            } else {
                                thisGroup.removeClass('empty').append(newInput);
                            }
                            $('#id-' + prefix + '-' + thisTypeName + '-' + index.toString()).prop('checked', true).change();
                            inputs = inputList.add(newInputList).find(options.inputs);
                        }
                    } else {
                        // Otherwise, simply add the input.
                        data = {
                            typeName: thisTypeName,
                            inputName: inputName,
                            id: thisID,
                            index: index,
                            prefix: prefix,
                            pinable: options.pinable
                        };
                        if ($(this).data(options.extraDataName)) {
                            data.responseDataName = options.extraDataName;
                            data.responseDataVal = $(this).data(options.extraDataName);
                        }
                        newInput = ich.autocomplete_input(data);
                        if (thisGroup.children('ul').length) {
                            thisGroup.removeClass('empty').children('ul').append(newInput);
                        } else {
                            thisGroup.removeClass('empty').append(newInput);
                        }
                        $('#id-' + prefix + '-' + thisTypeName + '-' + index.toString()).prop('checked', true).change();
                        inputs = inputList.add(newInputList).find(options.inputs);
                    }
                }
                // Empty the textbox, and empty and hide the suggestion list
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        }, 'a');

        // Remove inputs and update suggestion list when unchecked.
        if (!options.inputsNeverRemoved) {
            inputList.add(newInputList).on('click', 'label', function (e) {
                e.preventDefault();
                $(this).closest('li[class$="item"]').remove();
                inputs = inputList.add(newInputList).find(options.inputs);
                if (newSuggestions) {
                    filterSuggestions();
                    suggestionList.hide().html(filteredSuggestions);
                    // Adds ".selected" to first autocomplete suggestion.
                    if (!(suggestionList.find('.selected').length)) {
                        suggestionList.find('li:first-child a').addClass('selected');
                    }
                }
                inputsChanged();
            });
        }

        // Allow adding new inputs via group-specific textbox
        newInputTextbox.each(function () {
            $(this).keydown(function (e) {
                if (e.keyCode === keycodes.ENTER) {
                    e.preventDefault();
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
                            prefix: prefix,
                            pinable: options.pinable
                        }),
                        addInput = function () {
                            if (thisGroup.children('ul').length) {
                                thisGroup.removeClass('empty').children('ul').append(newInput);
                            } else {
                                thisGroup.removeClass('empty').append(newInput);
                            }
                            $('#id-' + prefix + '-' + typeName + '-' + index.toString()).prop('checked', true).change();
                            inputs = inputs.add('#id-' + prefix + '-' + typeName + '-' + index.toString());
                            thisTextbox.val(null);
                            thisText = null;
                        },
                        selectInput = function () {
                            existingInput.prop('checked', true).change();
                            thisTextbox.val(null);
                            thisText = null;
                        };
                    // ENTER performs submit action if textbox is empty...
                    if (thisText === '' && formActions.is(':visible') && !options.autoSubmit) {
                        options.triggerSubmit(context);
                    } else if (thisText.length && thisText.trim() !== '') {
                        // ...otherwise, if the input already exists, ENTER selects it...
                        if (existingInput.length) {
                            if (!existingInput.is(':checked')) {
                                selectInput();
                            }
                        } else {
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
        suggestionList: '.suggest',                     // Selector for list of autocomplete suggestions
        inputList: '.visual',                           // Selector for list of inputs
        formActions: '.form-actions',                   // Select for form-actions (only needed if ``hideFormActions: true``)
        ajax: false,                                    // Set ``true`` if using Ajax to retrieve autocomplete suggestions
        url: null,                                      // Ajax url (only needed if ``ajax: true``)
        triggerSubmit: function (context) {             // Function to be executed on ENTER in empty textbox
            context.find('.form-actions button[type="submit"]').click();
        },
        hideFormActions: false,                         // Set ``true`` if form actions should be hidden when inputs are unchanged
        autoSubmit: false,                              // Set ``true`` if form should be submitted on every input change
        multipleCategories: false,                      // Set ``true`` if inputs are separated into categorized groups
        allowNew: false,                                // Set ``true`` if new inputs (neither existing nor returned via Ajax) are allowed
        restrictAllowNew: false,                        // Set ``true`` if new inputs are only allowed if textbox has data-allow-new="true"
        newInputList: null,                             // Selector for list of new inputs (only needed if ``allowNew: true``
                                                        //      and ``multipleCategories: true``)
        newInputTextbox: null,                          // Selector for secondary textbox to enter new group-specific inputs
        fakePlaceholder: false,                         // Set ``true`` to create fake placeholder text when using ``initialFocus: true``
        initialFocus: false,                            // Set ``true`` to give textbox focus on initial page load
        reset: '.reset',                                // Selector for button to reset all inputs to original state
        inputType: null,                                // Name for input types when using only one category of inputs
        inputsNeverRemoved: false,                      // Set ``true`` if non-new inputs are never added or removed (only checked or unchecked)
        caseSensitive: false,                           // Set ``true`` if inputs should be treated as case-sensitive
        prefix: '',                                     // Prefix to apply to each input ID (to avoid ID duplication when using multiple times on one page)
        noInputsNote: false,                            // Set ``true`` to add "none" when no there are no inputs
        extraDataName: null,                            // Additional key to be sent with ajax-request
        extraDataFn: null,                              // Function which returns additional value to be sent with ajax-request
        pinable: true                                   // Whether the result template supports pinning, as in a pinable filter.
    };

}(jQuery));