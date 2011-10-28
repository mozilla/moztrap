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

    CC.envNarrowing = function (container) {
        var context = $(container),
            bulkSelect = context.find('#bulk_select'),
            inputs = context.find('input[type="checkbox"][name="environments"]');

        bulkSelect.change(function () {
            if ($(this).is(':checked')) {
                inputs.prop('checked', true);
            } else {
                inputs.prop('checked', false);
            }
        });

        inputs.change(function () {
            if (inputs.not(':checked').length) {
                bulkSelect.prop('checked', false);
            }
        });
    };

    return CC;

}(CC || {}, jQuery));
