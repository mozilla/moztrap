/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery */

/**
 * jQuery SuperFormset 0.2
 *
 * Based on jQuery Formset 1.1r14
 * by Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 *
 * @requires jQuery 1.2.6 or later
 *
 * original portions copyright (c) 2009, Stanislaus Madueke
 * modifications copyright (c) 2012, Jonny Gerig Meyer
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {

    'use strict';

    $.fn.formset = function (opts) {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            parent = $(this),
            $$ = $(this).children('li'),

            updateElementIndex = function (elem, prefix, ndx) {
                var idRegex = new RegExp('(' + prefix + '-(\\d+|__prefix__)-)'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) { elem.attr("for", elem.attr("for").replace(idRegex, replacement)); }
                if (elem.attr('id')) { elem.attr('id', elem.attr('id').replace(idRegex, replacement)); }
                if (elem.attr('name')) { elem.attr('name', elem.attr('name').replace(idRegex, replacement)); }
            },

            hasChildElements = function (row) {
                return row.find('input,select,textarea,label').length > 0;
            },

            showAddButton = function () {
                return maxForms.length === 0 ||   // For Django versions pre 1.2
                    (maxForms.val() === '' || (maxForms.val() - totalForms.val() > 0));
            },

            insertDeleteLink = function (row) {
                $(options.deleteLink).appendTo(row).click(function (e) {
                    var row = $(this).parents(options.formSelector),
                        del = row.find('input:hidden[id $= "-DELETE"]'),
                        forms,
                        i,
                        updateSequence = function (forms, i) {
                            forms.eq(i).find('input,select,textarea,label').each(function () {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        };
                    if (del.length) {
                        // We're dealing with an inline formset.
                        // Rather than remove this form from the DOM, we'll mark it as deleted
                        // and hide it, then let Django handle the deleting:
                        del.val('on');
                        if (options.removeAnimationSpeed) {
                            row.animate({'height': 'toggle', 'opacity': 'toggle'}, options.removeAnimationSpeed, function () {
                                $(this).hide();
                                forms = parent.find(options.formSelector).not(':hidden').not('.extra-row');
                                totalForms.val(forms.length);
                            });
                        } else {
                            row.hide();
                            forms = parent.find(options.formSelector).not(':hidden').not('.extra-row');
                            totalForms.val(forms.length);
                        }
                    } else {
                        if (options.removeAnimationSpeed) {
                            row.animate({'height': 'toggle', 'opacity': 'toggle'}, options.removeAnimationSpeed, function () {
                                $(this).remove();
                                // Update the TOTAL_FORMS count:
                                forms = parent.find(options.formSelector);
                                totalForms.val(forms.not('.extra-row').length);
                                // Update names and IDs for all child controls, if this isn't a delete-able
                                // inline formset, so they remain in sequence.
                                for (i = 0; i < forms.length; i = i + 1) {
                                    if (!del.length) {
                                        updateSequence(forms, i);
                                    }
                                }
                            });
                        } else {
                            row.remove();
                            // Update the TOTAL_FORMS count:
                            forms = parent.find(options.formSelector);
                            totalForms.val(forms.not('.extra-row').length);
                            // Update names and IDs for all child controls, if this isn't a delete-able
                            // inline formset, so they remain in sequence.
                            for (i = 0; i < forms.length; i = i + 1) {
                                if (!del.length) {
                                    updateSequence(forms, i);
                                }
                            }
                        }
                    }
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) { options.removed(row); }
                    e.preventDefault();
                });
            },

            insertAboveLink = function (row) {
                $(options.insertAboveLink).prependTo(row).click(function (e) {
                    var thisRow = $(this).closest(options.formSelector),
                        formCount = parent.find(options.formSelector).length,
                        row = options.formTemplate.clone(true).addClass('new-row'),
                        forms,
                        i,
                        updateSequence = function (forms, i) {
                            forms.eq(i).find('input,select,textarea,label').each(function () {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        };
                    if (options.addAnimationSpeed) {
                        row.hide().insertBefore(thisRow).animate({"height": "toggle", "opacity": "toggle"}, options.addAnimationSpeed);
                    } else {
                        row.insertBefore(thisRow).show();
                    }
                    row.find('input,select,textarea,label').each(function () {
                        updateElementIndex($(this), options.prefix, formCount);
                    });
                    // Update the TOTAL_FORMS count:
                    forms = parent.find(options.formSelector);
                    totalForms.val(forms.not('.extra-row').length);
                    // Update names and IDs for all child controls so they remain in sequence.
                    for (i = 0; i < forms.length; i = i + 1) {
                        updateSequence(forms, i);
                    }
                    // Check if we've exceeded the maximum allowed number of forms:
                    if (!showAddButton()) { $(this).hide(); }
                    // If a post-add callback was supplied, call it with the added form:
                    if (options.added) { options.added(row); }
                    $(this).blur();
                    e.preventDefault();
                });
            },

            hideAddButton = !showAddButton(),
            addButton,
            template,

            autoAddRow = function () {
                var formCount = parseInt(totalForms.val(), 10),
                    row = options.formTemplate.clone(true);
                if (options.addAnimationSpeed) {
                    row.hide().css('opacity', 0).appendTo(parent).addClass('extra-row').animate({'height': 'toggle', 'opacity': '0.5'}, options.addAnimationSpeed);
                } else {
                    row.css('opacity', 0.5).appendTo(parent).addClass('extra-row');
                }
                row.find('input, select, textarea, label').focus(function () {
                    $(this).closest(options.formSelector).removeClass('extra-row').css('opacity', 1);
                    if ($(this).hasClass('required')) {
                        $(this).attr('required', 'required');
                    }
                    totalForms.val(parent.find(options.formSelector).not('.extra-row').length);
                    if (options.deleteOnlyActive) {
                        $(this).closest(options.formSelector).find(options.deleteLinkSelector).fadeIn();
                    }
                    if (showAddButton() && $(this).closest(options.formSelector).is(':last-child')) {
                        autoAddRow();
                    }
                }).each(function () {
                    updateElementIndex($(this), options.prefix, formCount);
                    $(this).removeAttr('required');
                });
                if (options.deleteOnlyActive) {
                    row.find(options.deleteLinkSelector).hide();
                }
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) { options.added(row); }
            };

        $$.each(function (i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                if (del.is(':checked')) {
                    // If an inline formset containing deleted forms fails validation, make sure
                    // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                    del.before('<input type="hidden" name="' + del.attr('name') + '" id="' + del.attr('id') + '" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') + '" id="' + del.attr('id') + '" />');
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
                    if (options.insertAbove) {
                        insertAboveLink(row);
                    }
                }
            }
        });

        // Clone the form template to generate new form instances:
        template = $(options.formTemplate);
        template.removeAttr('id').find('input, select, textarea, label').each(function () {
            if ($(this).attr('required')) {
                $(this).addClass('required');
            }
        });
        insertDeleteLink(template);
        if (options.insertAbove) {
            insertAboveLink(template);
        }
        // FIXME: Perhaps using $.data would be a better idea?
        options.formTemplate = template;

        if (!options.autoAdd) {
            // Insert the add-link immediately after the last form:
            parent.after(options.addLink);
            addButton = parent.next();
            if (hideAddButton) { addButton.hide(); }
            addButton.click(function (e) {
                var formCount = parseInt(totalForms.val(), 10),
                    row = options.formTemplate.clone(true).addClass('new-row');
                if (options.addAnimationSpeed) {
                    row.hide().appendTo(parent).animate({"height": "toggle", "opacity": "toggle"}, options.addAnimationSpeed);
                } else {
                    row.appendTo($(this).prev()).show();
                }
                row.find('input,select,textarea,label').each(function () {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                totalForms.val(formCount + 1);
                // Check if we've exceeded the maximum allowed number of forms:
                if (!showAddButton()) { $(this).hide(); }
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) { options.added(row); }
                e.preventDefault();
            });
        }

        if (options.alwaysShowExtra && options.autoAdd) {
            autoAddRow();
            parent.closest('form').submit(function () {
                $(this).find(options.formSelector).filter('.extra-row').find('input,select,textarea').each(function () {
                    $(this).removeAttr('name');
                });
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
        deleteLinkSelector: '.delete-row',
                                        // Selector for HTML "remove" links
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
        removed: null,                  // Function called each time a form is deleted
        alwaysShowExtra: false,         // If true, an extra (empty) row will always be displayed (requires `autoAdd: true`)
        deleteOnlyActive: false,        // If true, extra empty rows cannot be removed until they acquire focus
        insertAbove: false,             // If true, ``insertAboveLink`` will be added to the end of each form-row
        insertAboveLink: '<a href="javascript:void(0)" class="insert-step">insert step</a>'
                                        // The HTML "insert step" link add to the end of each form-row (if `insertAbove: true`)
    };
}(jQuery));
