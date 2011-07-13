/**
 * jQuery SuperFormset 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * @requires jQuery 1.2.6 or later
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 *
 * Based on jQuery Formset 1.1r14
 * by Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 */
;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            parent = $(this),
            $$ = $(this).children('li'),

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp('(' + prefix + '-(\\d+|__prefix__)-)'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find('input,select,textarea,label').length > 0;
            },

            showAddButton = function() {
                return maxForms.length == 0 ||   // For Django versions pre 1.2
                    (maxForms.val() == '' || (maxForms.val() - totalForms.val() > 0));
            },

            insertDeleteLink = function(row) {
                $(options.deleteLink).appendTo(row).click(function() {
                    var row = $(this).parents(options.formSelector),
                        del = row.find('input:hidden[id $= "-DELETE"]'),
                        forms;
                    if (del.length) {
                        // We're dealing with an inline formset.
                        // Rather than remove this form from the DOM, we'll mark it as deleted
                        // and hide it, then let Django handle the deleting:
                        del.val('on');
                        if (options.removeAnimationSpeed) {
                            row.animate({"height": "toggle", "opacity": "toggle"}, options.removeAnimationSpeed, function () {
                                $(this).hide();
                            });
                        } else {
                            row.hide();
                        }
                        forms = parent.find(options.formSelector).not(':hidden');
                    } else {
                        if (options.removeAnimationSpeed) {
                            row.animate({"height": "toggle", "opacity": "toggle"}, options.removeAnimationSpeed, function () {
                                $(this).remove();
                            });
                        } else {
                            row.remove();
                        }
                        // Update the TOTAL_FORMS count:
                        forms = parent.find(options.formSelector);
                        totalForms.val(forms.length);
                    }
                    // Update names and IDs for all child controls, if this isn't a delete-able
                    // inline formset, so they remain in sequence.
                    for (var i=0, formCount=forms.length; i<formCount; i++) {
                        if (!del.length) {
                            forms.eq(i).find('input,select,textarea,label').each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                if (del.is(':checked')) {
                    // If an inline formset containing deleted forms fails validation, make sure
                    // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                }
                // Hide any labels associated with the DELETE checkbox:
                $('label[for="' + del.attr('id') + '"]').hide();
                del.remove();
            }
            if (hasChildElements(row)) {
                if (row.is(':visible')) {
                    if (!options.deleteOnlyNew) {
                        insertDeleteLink(row);
                    }
                }
            }
        });

        var hideAddButton = !showAddButton(),
            addButton, template;
        // Clone the form template to generate new form instances:
        template = $(options.formTemplate);
        template.removeAttr('id');
        insertDeleteLink(template);
        // FIXME: Perhaps using $.data would be a better idea?
        options.formTemplate = template;

        if (options.autoAdd) {
            parent.find('input, select, textarea, label').live('keyup', function () {
                if (showAddButton() && $(this).closest(options.formSelector).is(':last-child') && $(this).is($(this).closest(options.formSelector).find('input, select, textarea, label').last()) && $(this).val().length) {
                    var formCount = parseInt(totalForms.val()),
                        row = options.formTemplate.clone(true);
                    if (options.addAnimationSpeed) {
                        row.hide().css('opacity', 0).appendTo(parent).animate({"height": "toggle", "opacity": 0.5}, options.addAnimationSpeed).find('input, select, textarea, label').focus(function () {
                            $(this).closest(options.formSelector).css('opacity', 1);
                        });
                    } else {
                        row.css('opacity', 0.5).appendTo(parent).find('input, select, textarea, label').focus(function () {
                            $(this).closest(options.formSelector).css('opacity', 1);
                        });
                    }
                    row.find('input, select, textarea, label').each(function() {
                        updateElementIndex($(this), options.prefix, formCount);
                    });
                    totalForms.val(formCount + 1);
                    // If a post-add callback was supplied, call it with the added form:
                    if (options.added) options.added(row);
                    return false;
                }
            });
        } else {
            // Insert the add-link immediately after the last form:
            parent.after(options.addLink);
            addButton = parent.next();
            if (hideAddButton) addButton.hide();
            addButton.click(function() {
                var formCount = parseInt(totalForms.val()),
                    row = options.formTemplate.clone(true).addClass('new-row');
                if (options.addAnimationSpeed) {
                    row.hide().appendTo(parent).animate({"height": "toggle", "opacity": "toggle"}, options.addAnimationSpeed);
                } else {
                    row.appendTo($(this).prev()).show();
                }
                row.find('input,select,textarea,label').each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                totalForms.val(formCount + 1);
                // Check if we've exceeded the maximum allowed number of forms:
                if (!showAddButton()) $(this).hide();
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                 // The form prefix for your django formset
        formTemplate: null,             // The jQuery selection cloned to generate new form instances
                                        // This empty-form must be outside the parent (element on which
                                        // formset is called)
        deleteLink: '<a class="delete-row" href="javascript:void(0)">remove</a>',
                                        // The HTML "remove" link added to the end of each form-row
        addLink: '<a class="add-row" href="javascript:void(0)">add</a>',
                                        // The HTML "add" link added to the end of all forms
        autoAdd: false,                 // If true, the "add" link will be removed, and a row will be automatically
                                        // added when text is entered in the final textarea of the last row
        addAnimationSpeed: false,       // Speed (ms) to animate adding rows
                                        // If false, new rows will appear without animation
        removeAnimationSpeed: false,    // Speed (ms) to animate removing rows
                                        // If false, new rows will disappear without animation
        deleteOnlyNew: false,           // If true, only newly-added rows can be deleted
        formSelector: '.dynamic-form',  // jQuery selector used to match each form in a formset
        added: null,                    // Function called each time a new form is added
        removed: null                   // Function called each time a form is deleted
    };
})(jQuery);
