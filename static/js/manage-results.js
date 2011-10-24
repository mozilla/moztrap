/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011 uTest Inc.

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
            confusion:  true,
            regexp:     true */
/*global    ich, jQuery, confirm */

var CC = (function (CC, $) {

    'use strict';

    CC.toggleAdvancedFiltering = function (context) {
        var advanced = $(context).find('.visual'),
            toggleAdvanced = $(context).find('.toggle a');

        // Shows/hides the advanced filtering
        toggleAdvanced.click(function (e) {
            e.preventDefault();
            advanced.toggleClass('compact expanded');
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

    CC.testcaseAttachments = function (container) {
        var context = $(container),
            counter = 1,
            label = context.find('.upload'),
            uploads = context.find('.uploads'),
            attachment,
            newInput;

        label.click(function (e) {
            e.preventDefault();
            var id = $(this).attr('for');
            context.find('#' + id).click();
        });

        context.delegate('input[name="attachment"]', 'change', function () {
            var input = $(this),
                inputID = input.attr('id'),
                filename = input.val().replace(/^.*\\/, '');

            counter = counter + 1;
            attachment = ich.case_attachment({
                name: filename,
                input: inputID
            });
            newInput = ich.case_attachment_input({ counter: counter });
            uploads.append(attachment);
            context.append(newInput);
            label.attr('for', 'attachment-input-' + counter);
        });

        uploads.delegate('.action-remove', 'click', function () {
            var button = $(this),
                inputID = button.data('input-id'),
                attachment = button.parent(),
                fileID,
                removeAttachment;

            if (attachment.hasClass('uploading')) {
                context.find('#' + inputID).remove();
            } else {
                fileID = attachment.data('id');
                if (fileID) {
                    removeAttachment = ich.case_attachment_remove({ id: fileID });
                    context.append(removeAttachment);
                }
            }

            attachment.remove();
        });
    };

    CC.testcaseVersioning = function (container) {
        var context = $(container),
            select = context.find('#id_version'),
            selectVal = select.val(),
            url = window.location.pathname,
            dirty = false,
            tags = context.find('.versioned .tagging .visual').html();

        context
            .delegate(
                '.versioned #id_description, .versioned .steps-form:not(.extra-row) textarea, .versioned input[name="attachment"]',
                'change',
                function () {
                    dirty = true;
                }
            )
            .delegate(
                '.versioned a.removefields, .versioned a.insert-step',
                'click',
                function () {
                    dirty = true;
                }
            );

        select.change(function (e) {
            var newVersion = $(this).val(),
                currentVersion = url.split('/')[3],
                newURL = url.replace(currentVersion, newVersion),
                updateVersion = function (data) {
                    if (data.html) {
                        var newHTML = $(data.html).hide(),
                            prefix = newHTML.find('ol.steplist').data('prefix');
                        context.find('.versioned').fadeOut('fast', function () {
                            $(this).replaceWith(newHTML);
                            dirty = false;
                            newHTML.fadeIn('fast', function () {
                                $(this).find('ol.steplist').formset({
                                    prefix: prefix,
                                    formTemplate: '#empty-step-form > li',
                                    formSelector: '.steps-form',
                                    deleteLink: '<a class="removefields" href="javascript:void(0)">remove</a>',
                                    deleteLinkSelector: '.removefields',
                                    addAnimationSpeed: 'normal',
                                    removeAnimationSpeed: 'fast',
                                    autoAdd: true,
                                    alwaysShowExtra: true,
                                    deleteOnlyActive: true,
                                    insertAbove: true
                                });
                                CC.autoCompleteCaseTags('#addcase');
                                CC.testcaseAttachments('#single-case-form .attachments');
                                tags = context.find('.versioned .tagging .visual').html();
                            });
                        });
                        context.find('#single-case-form').attr('action', url);
                    }
                };

            if (dirty || context.find('.versioned .tagging .visual').html() !== tags) {
                if (confirm("You have made changes to the form that will be lost if you switch versions. Are you sure you want to continue?")) {
                    context.find('.versioned').loadingOverlay();
                    url = newURL;
                    selectVal = select.val();
                    $.get(url, updateVersion);
                } else {
                    select.val(selectVal);
                }
            } else {
                context.find('.versioned').loadingOverlay();
                url = newURL;
                selectVal = select.val();
                $.get(url, updateVersion);
            }
        });
    };

    return CC;

}(CC || {}, jQuery));
