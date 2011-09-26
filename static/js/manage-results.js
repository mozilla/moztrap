/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    // Filtering, autocomplete, and fake placeholder text for manage and results pages
    CC.autoCompleteFiltering = function () {

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
                    // Adds ".selected" to first autocomplete suggestion.
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
                if (!event.metaKey && event.keyCode !== CC.keycodes.SHIFT && event.keyCode !== CC.keycodes.CTRL && event.keyCode !== CC.keycodes.ALT && event.keyCode !== CC.keycodes.CAPS && event.keyCode !== CC.keycodes.ESC) {
                    removeFakePlaceholder();
                }
            }
            // If the suggestion list is not visible...
            if (!suggestionList.is(':visible')) {
                // ...and if the keydown was a non-meta key other than shift, ctrl, alt, caps, or esc...
                if (!event.metaKey && event.keyCode !== CC.keycodes.SHIFT && event.keyCode !== CC.keycodes.CTRL && event.keyCode !== CC.keycodes.ALT && event.keyCode !== CC.keycodes.CAPS && event.keyCode !== CC.keycodes.ESC) {
                    // ...prevent normal TAB function
                    if (event.keyCode === CC.keycodes.TAB && textbox.val() !== '') {
                        event.preventDefault();
                    }
                    // ...submit the form on ENTER if textbox is empty and inputs have changed
                    if (event.keyCode === CC.keycodes.ENTER && textbox.val() === '' && $('.managelist').hasClass('expired')) {
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
                // ENTER submits the form if textbox is empty and inputs have changed...
                if (event.keyCode === CC.keycodes.ENTER) {
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
                if (event.keyCode === CC.keycodes.TAB) {
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
                if (event.keyCode === CC.keycodes.RIGHT) {
                    if (thisFilterName && textbox.val().toLowerCase() !== thisFilterName.toLowerCase()) {
                        event.preventDefault();
                        textbox.val(thisFilterName);
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
        // If textbox still has fake placeholder text, removes it on click
        }).click(function () {
            if (textbox.hasClass('placeholder')) {
                removeFakePlaceholder();
            }
        }).focus(function () {
            // Resets textbox data-clicked to "false" (becomes "true" when an autocomplete suggestion is clicked)
            textbox.data('clicked', false);
            // Adds fake placeholder on initial load (and moves cursor to start of textbox)
            if (textbox.val().length === 0 && textbox.hasClass('placeholder')) {
                textbox.val(placeholder);
                textbox.get(0).setSelectionRange(0, 0);
            }
        // On blur, removes fake placeholder text, and hides the suggestion
        // list after 150 ms if textbox data-clicked is "false"
        }).blur(function () {
            function hideList() {
                if (textbox.data('clicked') !== true) {
                    suggestionList.hide();
                    textbox.data('clicked', false);
                }
            }
            removeFakePlaceholder();
            window.setTimeout(hideList, 150);
        // Add initial "placeholder" class and focus to textbox
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
            if (event.keyCode === CC.keycodes.ENTER) {
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
            // Adds ".selected" to suggestion on mouseover, removing ".selected" from other suggestions
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
    CC.loadListItemDetails = function () {
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

    // Expand list item details on direct hashtag links
    CC.openListItemDetails = function () {
        if ($('.manage').length && window.location.hash && $(window.location.hash).length) {
            $(window.location.hash).children('.summary').click();
        }
    };

    // Ajax for manage list actions (clone and delete)
    CC.manageActionsAjax = function () {
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

    // Filter form options for add-run and add-suite
    CC.formOptionsFilter = function (context_sel, data_attr, trigger_sel, target_sel) {
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

    CC.addEllipses = function () {
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

    // Autocomplete suggestions for test case tags
    CC.autoCompleteCaseTags = function (container) {

        var typedText,
            newSuggestions,
            newTagSuggestion,
            newTagCounter = 1,
            getSuggestions = true,
            context = $(container),
            textbox = context.find('input[name="text-tag"]'),
            tagList = context.find('.visual'),
            tags = tagList.find('input[name="tag"]'),
            url = textbox.data('autocomplete-url'),

            // Hide the list of autocomplete suggestions initially
            suggestionList = context.find('.textual .suggest').hide(),

            updateSuggestions = function (data) {
                if (getSuggestions) {
                    var filteredSuggestions;
                    newSuggestions = ich.case_tag_suggestion(data);
                    filteredSuggestions = newSuggestions.filter(function (index) {
                        var thisSuggestion = $(this).find('a').data('id');
                        return !(tagList.find('input[name="tag"][value="' + thisSuggestion + '"]').length);
                    });
                    suggestionList.find('a.tag-suggestion').each(function () {
                        $(this).parent().remove();
                    });
                    suggestionList.append(filteredSuggestions).show();
                    if (suggestionList.find('a.newtag').length) {
                        suggestionList.find('a.newtag').each(function () {
                            if (suggestionList.find('a.tag-suggestion[data-name="' + $(this).data('name') + '"]').length) {
                                $(this).parent().remove();
                            }
                        });
                    }
                    if (!(suggestionList.find('.selected').length)) {
                        suggestionList.find('li:first-child a').addClass('selected');
                    }
                }
            };

        textbox
            // Updates suggestion-list if typed-text has changed on keyup
            .keyup(function () {
                $(this).doTimeout(300, function () {
                    if ($(this).val() !== typedText) {
                        typedText = $(this).val();
                        if (typedText.length) {
                            newTagSuggestion = ich.new_case_tag_suggestion({ typedText: typedText });
                            if (!(tagList.find('label').filter(function () { return $(this).html() === typedText; }).length)) {
                                suggestionList.html(newTagSuggestion).find('li:first-child a').addClass('selected');
                            } else {
                                suggestionList.empty();
                            }
                            $.get(url, {text: typedText}, updateSuggestions);
                            getSuggestions = true;
                        } else {
                            suggestionList.empty().hide();
                            getSuggestions = false;
                        }
                    }
                });
            })
            .keydown(function (event) {
                // If the suggestion list is not visible...
                if (!suggestionList.is(':visible')) {
                    // ...and if the textbox is not empty...
                    if (textbox.val() !== '') {
                        // ...and if the keydown was a non-meta key other than shift, ctrl, alt, caps, or esc...
                        if (!event.metaKey && event.keyCode !== CC.keycodes.SHIFT && event.keyCode !== CC.keycodes.CTRL && event.keyCode !== CC.keycodes.ALT && event.keyCode !== CC.keycodes.CAPS && event.keyCode !== CC.keycodes.ESC) {
                            // ...prevent normal TAB or ENTER function
                            if (event.keyCode === CC.keycodes.TAB || event.keyCode === CC.keycodes.ENTER) {
                                event.preventDefault();
                            }
                            // ...show the suggestion list
                            suggestionList.show();
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
                        if (suggestionList.find('.selected').length) {
                            event.preventDefault();
                            suggestionList.find('.selected').click();
                            return false;
                        }
                    }
                    // TAB auto-completes the "active" suggestion if it isn't already completed...
                    if (event.keyCode === CC.keycodes.TAB) {
                        if (thisSuggestionName.length && textbox.val().toLowerCase() !== thisSuggestionName.toLowerCase()) {
                            event.preventDefault();
                            textbox.val(thisSuggestionName);
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
                        if (thisSuggestionName.length && textbox.val().toLowerCase() !== thisSuggestionName.toLowerCase()) {
                            event.preventDefault();
                            textbox.val(thisSuggestionName);
                            return false;
                        }
                    }
                    // ESC hides the suggestion list
                    if (event.keyCode === CC.keycodes.ESC) {
                        event.preventDefault();
                        suggestionList.hide();
                        return false;
                    }
                }
            })
            // Resets textbox data-clicked to "false" (becomes "true" when an autocomplete suggestion is clicked)
            .focus(function () {
                textbox.data('clicked', false);
            })
            // On blur, hides the suggestion list after 150 ms if textbox data-clicked is "false"
            .blur(function () {
                function hideList() {
                    if (textbox.data('clicked') !== true) {
                        suggestionList.hide();
                        textbox.data('clicked', false);
                    }
                }
                window.setTimeout(hideList, 150);
            });

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
            click: function (e) {
                e.preventDefault();
                var newTag,
                    id,
                    name = $(this).data('name');

                if ($(this).hasClass('tag-suggestion')) {
                    id = $(this).data('id');
                    if (id && name) {
                        newTag = ich.case_tag({
                            id: id,
                            name: name
                        });
                    }
                } else if (name) {
                    newTag = ich.new_case_tag({
                        name: name,
                        counter: newTagCounter
                    });
                    newTagCounter = newTagCounter + 1;
                }

                if (newTag.length) {
                    tagList.append(newTag);
                }

                // Reset the textbox, and reset and hide the suggestion list
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        });

        tagList.delegate('label', 'click', function (e) {
            e.preventDefault();
            var filteredSuggestions,
                newTagSuggestionName;
            $(this).parent().remove();
            if (newSuggestions) {
                newTagSuggestionName = $(newTagSuggestion).find('a').data('name');
                filteredSuggestions = newSuggestions.filter(function (index) {
                    var thisSuggestion = $(this).find('a').data('id');
                    return !(tagList.find('input[name="tag"][value="' + thisSuggestion + '"]').length);
                });
                if (newSuggestions !== filteredSuggestions) {
                    suggestionList.find('a.tag-suggestion').each(function () {
                        $(this).parent().remove();
                    });
                    suggestionList.append(filteredSuggestions);
                }
                if (!(suggestionList.find('a.newtag').length)
                        && !(tagList.find('label').filter(function () { return $(this).html() === typedText; }).length)
                        && !(suggestionList.find('a.tag-suggestion').filter(function () { return $(this).data('name') === newTagSuggestionName; }).length)) {
                    suggestionList.prepend(newTagSuggestion);
                }
                suggestionList.find('.selected').removeClass('selected');
                suggestionList.find('li:first-child a').addClass('selected');
            }
        });

    };

    return CC;

}(CC || {}, jQuery));