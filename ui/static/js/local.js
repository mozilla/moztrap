var TCM = TCM || {};

(function($) {

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
    },

    formOptionsFilter = function(context_sel, data_attr, trigger_sel, target_sel) {
        var context = $(context_sel),
        trigger = context.find(trigger_sel);
        if (context.length && trigger.is("select")) {
            var target = context.find(target_sel),
            allopts = target.find("option").clone();

            var doFilter = function() {
                var key = trigger.find("option:selected").data(data_attr);
                target.empty();
                allopts.each(function() {
                    if ($(this).data(data_attr) === key) {
                        var newopt = $(this).clone();
                        newopt.appendTo(target);
                    }
                });
            };

            doFilter();

            trigger.change(doFilter);
        }
    },

    // Filtering, autocomplete, and fake placeholder text for manage and results pages
    filtering = function() {

        // Hide the form-actions (submit, reset) initially
        var formActions = $('#filter .form-actions').hide(),
        toggle = $('#filter .toggle a'),
        // Set data-originallyChecked on each input to store original state
        input = $('#filter .visual .filter-group input[type="checkbox"]').each(function() {
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

        // Removes (faked) placeholder text from textbox
        removeFakePlaceholder = function() {
            if (textbox.val().indexOf(placeholder) !== -1) {
                textbox.val(null);
            }
            textbox.removeClass('placeholder');
        },

        // Checks if any inputs have changed from original-state,
        // showing form-actions if any inputs have changed.
        updateFormActions = function() {
            if (input.filter(function() { return $(this).data('state') === 'changed'; }).length) {
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
        updateSuggestions = function() {
            typedText = textbox.val();
            suggestionList.empty();
            if (textbox.val().length) {
                var relevantFilters = notKeywordGroups.find('input[type="checkbox"]:not(:checked)').parent('li').filter(function() {
                    return $(this).children('label').html().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                });
                relevantFilters.each(function() {
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
                keywordGroups.each(function() {
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
                        if ($(this).find('input[type="checkbox"][value^="^"][value$="$"]:checked').length === $(this).find('input[type="checkbox"]:checked').length) {
                            // ...and if the typed-text hasn't already been selected as a filter, and if the typed-text begins with "^" and ends with "$"...
                            if (!($(this).find('input[type="checkbox"][value="' + typedText + '"]:checked').length) && typedText.indexOf('^') === 0 && typedText.lastIndexOf('$') === typedText.length - 1) {
                                // ...then append the keyword suggestion to the suggestion-list.
                                suggestionList.append(keywordSuggestion);
                            }
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
        toggle.click(function() {
            $('#filter .visual').toggleClass('compact expanded');
            return false;
        });

        // Reset button sets each input to its original state, hides form-actions
        // and suggestion-list, and returns focus to the textbox.
        formActions.find('.reset').click(function() {
            formActions.fadeOut('fast');
            $('.managelist').removeClass('expired');
            input.each(function() {
                $(this).data('state', null);
                $(this).prop('checked', $(this).data('originallyChecked'));
            });
            textbox.focus();
            suggestionList.hide();
            return false;
        });

        // Selecting/unselecting an input returns focus to textbox, hides
        // suggestion-list, sets data-state "changed" if input has changed from
        // original state, and shows/hides form-actions as appropriate.
        input.live('change', function() {
            if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                $(this).data('state', 'changed');
            } else {
                $(this).data('state', null);
            }
            textbox.focus();
            suggestionList.hide();
            updateFormActions();
        });

        textbox.keyup(function(event) {
            // Updates suggestion-list if typed-text has changed
            if ($(this).val() !== typedText && $(this).val() !== placeholder) {
                updateSuggestions();
            }
        })
        .keydown(function(event) {
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
                // ENTER auto-completes the "active" suggestion if it isn't already completed
                if (event.keyCode === keycodes.ENTER) {
                    event.preventDefault();
                    var thisFilterName = input.filter('#' + suggestionList.find('.selected').data('id')).siblings('label').html();
                    if (thisFilterName && textbox.val().toLowerCase() !== thisFilterName.toLowerCase()) {
                        textbox.val(thisFilterName);
                    } else {
                        // ENTER submits the form if textbox is empty and inputs have changed...
                        if (textbox.val() === '' && $('.managelist').hasClass('expired')) {
                            formActions.find('button[type="submit"]').click();
                        // ...otherwise, ENTER selects the "active" filter suggestion.
                        } else {
                            suggestionList.find('.selected').click();
                            suggestionList.show();
                        }
                    }
                    return false;
                }
                // TAB auto-completes the "active" suggestion if it isn't already completed...
                if (event.keyCode === keycodes.TAB) {
                    var thisFilterName = input.filter('#' + suggestionList.find('.selected').data('id')).siblings('label').html();
                    if (thisFilterName && textbox.val().toLowerCase() !== thisFilterName.toLowerCase()) {
                        event.preventDefault();
                        textbox.val(thisFilterName);
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
                // ESC hides the suggestion list
                if (event.keyCode === keycodes.ESC) {
                    event.preventDefault();
                    suggestionList.hide();
                    return false;
                }
                return true;
            }
        })
        // If textbox still has fake placeholder text, removes it on click
        .click(function() {
            if (textbox.hasClass('placeholder')) {
                removeFakePlaceholder();
            }
        })
        .focus(function() {
            // Resets textbox data-clicked to ``false`` (becomes ``true`` when an autocomplete suggestion is clicked)
            textbox.data('clicked', false);
            // Adds fake placeholder on initial load (and moves cursor to start of textbox)
            if (textbox.val().length === 0 && textbox.hasClass('placeholder')) {
                textbox.val(placeholder);
                textbox.get(0).setSelectionRange(0, 0);
            }
        })
        // On blur, removes fake placeholder text, and hides the suggestion
        // list after 150 ms if textbox data-clicked is ``false``
        .blur(function() {
            function hideList() {
                if (textbox.data('clicked') !== true) {
                    suggestionList.hide();
                    textbox.data('clicked', false);
                }
            }
            removeFakePlaceholder();
            window.setTimeout(hideList, 150);
        })
        // Add initial ``placeholder`` class and focus to textbox
        .addClass('placeholder').focus();

        suggestionList.find('a').live({
            // Adds ``.selected`` to suggestion on mouseover, removing ``.selected`` from other suggestions
            mouseover: function() {
                var thisSuggestion = $(this).addClass('selected'),
                otherSuggestions = thisSuggestion.parent('li').siblings('li').find('a').removeClass('selected');
            },
            // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
            mousedown: function() {
                textbox.data('clicked', true);
            },
            click: function() {
                // If keyword suggestion clicked...
                if ($(this).data('class') === 'keyword') {
                    var name = $(this).data('name'),
                    thisGroup = keywordGroups.filter(function() {
                        return $(this).data('name') === name;
                    }),
                    existingKeyword = thisGroup.find('input[type="checkbox"][value="' + typedText + '"][name="' + name + '"]'),
                    index = thisGroup.find('li').length + 1,
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
                        thisGroup.removeClass('empty').children('ul').append(newKeywordFilter);
                        $('#id-' + name + '-' + index).data('state', 'changed').data('originallyChecked', false).prop('checked', true);
                        input = input.add('#id-' + name + '-' + index);
                    }
                // If non-keyword suggestion clicked, select it
                } else {
                    var thisFilter = input.filter('#' + $(this).data('id')).prop('checked', true);
                    if (thisFilter.data('originallyChecked') !== thisFilter.is(':checked')) {
                        thisFilter.data('state', 'changed');
                    }
                }
                // Show/hide the form-actions as necessary, reset the textbox, and reset and hide the suggestion list
                updateFormActions();
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
                return false;
            }
        });
    },

    // Ajax-load manage and results list item contents
    listDetails = function() {
        $('#listcontent .items .item.details').live('click', function(event) {
            if ($(event.target).is("button, a")) {
                return;
            }
            var item = $(this),
            content = item.find('.content'),
            url = item.data('details-url');
            if (url && !content.hasClass('loaded')) {
                content.css('min-height', '4.854em').addClass('loaded');
                content.loadingOverlay();
                $.get(url, function(data) {
                    content.loadingOverlay('remove');
                    content.html(data.html);
                });
            }
        });
    },

    // Ajax for manage list actions (clone and delete)
    manageActionsAjax = function() {
        $('.manage button[name^=action-]').live(
            'click',
            function() {
                var button = $(this),
                form = button.closest('form'),
                token = form.find('input[name=csrfmiddlewaretoken]'),
                url = form.attr('action'),
                method = form.attr('method'),
                replace = button.closest('.action-ajax-replace'),
                success = function(data) {
                    var replacement = $(data.html);
                    replace.replaceWith(replacement);
                    replacement.find('.details').html5accordion('.summary');
                    replace.loadingOverlay('remove');
                },
                data = {};
                data[button.attr('name')] = button.val();
                data['csrfmiddlewaretoken'] = token.val();
                replace.loadingOverlay();
                $.ajax(url, {
                           type: method,
                           data: data,
                           success: success
                       });
                return false;
            }
        );
    },

    manageEnvProfiles = function() {
        var elements = $('#addprofile .item .elements .element-select input'),
        categories = $('#addprofile .item .bulk input[id^="bulk-select-"]'),
        addElement = $('input[id$="-add-element"]'),
        addCategory = $('input#edit_name'),
        updateLabels = function() {
            elements.each(function() {
                var thisID = $(this).attr('id');
                if ($(this).is(':checked')) {
                    $('label[for=' + thisID + ']').addClass('checked');
                } else {
                    $('label[for=' + thisID + ']').removeClass('checked');
                }
            });
        };

        elements.live('change', function() {
            var thisID = $(this).attr('id');
            if ($(this).is(':checked')) {
                $('label[for=' + thisID + ']').addClass('checked');
            } else {
                $('label[for=' + thisID + ']').removeClass('checked');
            }
        });

        categories.live('change', function() {
            if ($(this).is(':checked')) {
                $(this).closest('.item').find('.elements input').prop('checked', true);
            } else {
                $(this).closest('.item').find('.elements input').prop('checked', false);
            }
            updateLabels();
        });

        addElement.live('keydown', function(event) {
            if (event.keyCode === keycodes.ENTER) {
                var name = $(this).val(),
                externalIndex = $(this).closest('.items').children('[id^="category"]').length + 1,
                internalIndex = $(this).closest('.elements').children('li').not('.add-element').length + 1;
                if (externalIndex < 10) {
                    externalIndex = '0' + externalIndex;
                }
                var newElement = ich.env_profile_element({
                    name: name,
                    external_index: externalIndex,
                    internal_index: internalIndex
                }),
                newElementPreview = ich.env_profile_element_preview({
                    name: name,
                    external_index: externalIndex,
                    internal_index: internalIndex
                });
                $(this).closest('.elements').children('li.add-element').before(newElement);
                $(this).closest('.item').find('.preview').append(newElementPreview);
                elements = $('#addprofile .item .elements .element-select input');
                $(this).val(null);
            }
        });

        addCategory.keydown(function(event) {
            if (event.keyCode === keycodes.ENTER) {
                var name = $(this).val(),
                index = $(this).closest('.items').children('[id^="category"]').length + 1;
                if (index < 10) {
                    index = '0' + index;
                }
                var newCategory = ich.env_profile_category({
                    name: name,
                    index: index
                });
                $(this).closest('.items').children('.add-item').before(newCategory);
                $('#category-id-' + index).find('.details').andSelf().html5accordion('.summary');
                $(this).val(null);
            }
        });
    };

    $(function() {
        filtering();
        listDetails();
        manageActionsAjax();
        manageEnvProfiles();
        $('.details:not(html)').html5accordion('.summary');
        $('#messages').messages({
            handleAjax: true,
            closeLink: '.message'
        });
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input:not([type=radio], [type=checkbox]), textarea').blur(function() {
            $(this).addClass('hadfocus');
        });
        formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");
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
            callback: function() {
                $('.selectruns + .environment').slideUp('fast');
            },
            lastChildCallback: function(choice) {
                var environments = $('.selectruns + .environment').css('min-height', '169px').slideDown('fast'),
                ajaxUrl = $(choice).data("sub-url");
                environments.loadingOverlay();
                $.get(ajaxUrl, function(data) {
                    environments.loadingOverlay('remove');
                    environments.html(data.html);
                });
            }
        });
        $('.selectruns + .environment.empty').hide();
        // $('.subnav .findertoggle').click(function() {
        //     $(this).add('.subnav .finder').toggleClass('expanded').toggleClass('compact');
        //     return false;
        // });
        // $('.subnav').html5finder( {
        //     loading: true,
        //     ellipsis: true,
        //     horizontalScroll: true,
        //     scrollContainer: '.finder.expanded',
        //     headerSelector: '.listordering',
        //     sectionSelector: '.col',
        //     sectionContentSelector: '.colcontent',
        //     sectionClasses: [
        //         'products',
        //         'cycles',
        //         'runs',
        //         'cases',
        //         'results'
        //     ],
        //     sectionItemSelectors: [
        //         'input[name="product"]',
        //         'input[name="testcycle"]',
        //         'input[name="testrun"]',
        //         'input[name="testcase"]',
        //         'input[name="testresult"]'
        //     ]
        // });
    });

    $(window).load(function() {
        $('#listcontent .items').find('.title, .product, .cycle, .run').ellipsis(true, 300);
        // Expand list item details on direct hashtag links
        if ($('.manage').length && window.location.hash) {
            var hash = window.location.hash;
            $(hash).children('.summary').click();
        }
    });

})(jQuery);
