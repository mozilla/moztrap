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
            versionList = context.find('.versioning .version-select'),
            versions = versionList.find('.version .item-select'),
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

        versionList.find('.summary').click(function () { $(this).blur(); });

        versions.click(function (e) {
            var clickedVersion = $(this).closest('.version');
            if (clickedVersion.find('.item-input').is(':checked')) {
                versionList.find('.summary').click();
                console.log('same version');
            } else {
                var newVersion = clickedVersion.attr('id').split('-')[2],
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
                                    versionList.find('.summary').click();
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
                                    context.customAutocomplete({
                                        textbox: 'input[name="text-tag"]',
                                        ajax: true,
                                        url: $('#addcase input[name="text-tag"]').data('autocomplete-url'),
                                        triggerSubmit: null,
                                        allowNew: true,
                                        inputType: 'tag'
                                    });
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
                        $.get(url, updateVersion);
                    } else {
                        e.preventDefault();
                    }
                } else {
                    context.find('.versioned').loadingOverlay();
                    url = newURL;
                    $.get(url, updateVersion);
                }
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

    CC.filterIncludedTestCases = function (container) {
        var context = $(container),
            inputLists = context.find('.groups .filter-group'),
            inputSelector = 'input[type="checkbox"]',
            casesContainer = context.find('.select'),
            cases,

            filterCases = function () {
                cases = context.find('.select .selectitem');
                cases.each(function () {
                    var thisCase = $(this),
                        excludeThisCase = false;
                    inputLists.find(inputSelector + ':checked').each(function () {
                        var type = $(this).attr('name'),
                            filter = $(this).siblings('label').text().toLowerCase();

                        if (type === 'name') {
                            if (!(thisCase.find('.title').text().toLowerCase().indexOf(filter) !== -1)) {
                                excludeThisCase = true;
                            }
                        } else if (type === 'status') {
                            if (!(thisCase.find('.status').children('span').text().toLowerCase() === filter)) {
                                excludeThisCase = true;
                            }
                        } else if (type === 'author') {
                            if (!(thisCase.find('.author').text().toLowerCase() === filter)) {
                                excludeThisCase = true;
                            }
                        }
                    });

                    if (excludeThisCase) {
                        thisCase.hide();
                    } else {
                        thisCase.show();
                    }
                });
            };

        inputLists.delegate(inputSelector, 'change', function () {
            filterCases();
        });
    };

    CC.selectIncludedTestCases = function (container) {
        var context = $(container),
            availableList = context.find('.multiunselected .select'),
            includedList = context.find('.multiselected .select'),
            bulkInclude = context.find('.multiunselected .listordering .action-include'),
            bulkExclude = context.find('.multiselected .listordering .action-exclude'),
            form = $('#suite-form');

        context.find('.multiunselected, .multiselected').sortable({
            items: '.selectitem',
            connectWith: '.sortable',
            revert: 200,
            delay: 50,
            opacity: 0.7,
            update: function (event, ui) {
                ui.item.closest('.sortable').find('.groups .filter-group input[type="checkbox"]:checked').prop('checked', false).change();
            }
        });

        context.delegate('.select label.bulkselect', 'click', function (e) {
            var thisLabel = $(this),
                thisInput = thisLabel.closest('.selectitem').find('.item-input'),
                labels = thisLabel.closest('.select').find('label.bulkselect'),
                thisIndex,
                recentlyClicked,
                recentlyClickedIndex,
                filteredLabels;

            if (e.shiftKey) {
                if (labels.filter(function () { return $(this).data('clicked') === true; }).length) {
                    recentlyClicked = labels.filter(function () { return $(this).data('clicked') === true; });
                } else if (labels.filter(function () { return $(this).data('unclicked') === true; }).length) {
                    recentlyClicked = labels.filter(function () { return $(this).data('unclicked') === true; });
                }
                thisIndex = thisLabel.closest('.selectitem').index();
                recentlyClickedIndex = recentlyClicked.closest('.selectitem').index();
                filteredLabels = labels.filter(function () {
                    if (thisIndex > recentlyClickedIndex) {
                        return $(this).closest('.selectitem').index() >= recentlyClickedIndex && $(this).closest('.selectitem').index() <= thisIndex;
                    } else if (recentlyClickedIndex > thisIndex) {
                        return $(this).closest('.selectitem').index() >= thisIndex && $(this).closest('.selectitem').index() <= recentlyClickedIndex;
                    }
                });
                if (labels.filter(function () { return $(this).data('clicked') === true; }).length) {
                    filteredLabels.closest('.selectitem').find('.item-input').prop('checked', true);
                    labels.data('clicked', false).data('unclicked', false);
                    thisLabel.data('clicked', true);
                    e.preventDefault();
                } else if (labels.filter(function () { return $(this).data('unclicked') === true; }).length) {
                    filteredLabels.closest('.selectitem').find('.item-input').prop('checked', false);
                    labels.data('clicked', false).data('unclicked', false);
                    thisLabel.data('unclicked', true);
                    e.preventDefault();
                } else {
                    labels.data('clicked', false).data('unclicked', false);
                    if (thisInput.is(':checked')) {
                        thisLabel.data('unclicked', true);
                    } else {
                        thisLabel.data('clicked', true);
                    }
                }
            } else {
                labels.data('clicked', false).data('unclicked', false);
                if (thisInput.is(':checked')) {
                    thisLabel.data('unclicked', true);
                } else {
                    thisLabel.data('clicked', true);
                }
            }
        });

        bulkInclude.click(function (e) {
            e.preventDefault();
            var selectedCases = context.find('.multiunselected .select .selectitem input.item-input:checked');
            selectedCases.prop('checked', false).closest('.selectitem').detach().prependTo(includedList);
            context.find('.multiselected .groups .filter-group input[type="checkbox"]:checked').prop('checked', false).change();
        });

        bulkExclude.click(function (e) {
            e.preventDefault();
            var selectedCases = context.find('.multiselected .select .selectitem input.item-input:checked');
            selectedCases.prop('checked', false).closest('.selectitem').detach().prependTo(availableList);
            context.find('.multiunselected .groups .filter-group input[type="checkbox"]:checked').prop('checked', false).change();
        });

        form.submit(function (e) {
            includedList.find('.item-input').each(function () {
                var id = $(this).attr('value'),
                    hiddenInput = ich.suite_included_case_input({ id: id });
                includedList.append(hiddenInput);
            });
        });
    };

    CC.sortIncludedTestCases = function (container) {
        var context = $(container),
            headers = context.find('.sortable .listordering li[class^="by"] a');

        // Sorting requires jQuery Element Sorter plugin ( http://plugins.jquery.com/project/ElementSort )
        headers.click(function (e) {
            var casesContainer = $(this).closest('.sortable').find('.select'),
                sortByClass = $(this).parent().attr('class').substring(2),
                direction;

            if ($(this).hasClass('asc') || $(this).hasClass('desc')) {
                $(this).toggleClass('asc desc');
                $(this).parent().siblings().find('a').removeClass('asc desc');
            } else {
                $(this).addClass('asc');
                $(this).parent().siblings().find('a').removeClass('asc desc');
            }
            if ($(this).hasClass('asc')) {
                direction = 'asc';
            }
            if ($(this).hasClass('desc')) {
                direction = 'desc';
            }
            if ($(this).parent().hasClass('bystatus')) {
                sortByClass = sortByClass + ' span';
            }
            casesContainer.sort({
                sortOn: '.' + sortByClass,
                direction: direction
            });
            $(this).blur();
            return false;
        });
    };

    return CC;

}(CC || {}, jQuery));
