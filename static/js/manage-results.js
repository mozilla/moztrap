/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

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
        $('.listpage').on('click', '.itemlist .listitem .details .summary', function (event) {
            var item = $(this),
                content = item.siblings('.content'),
                url = item.attr('href');
            if (url && !content.hasClass('loaded')) {
                content.css('min-height', '4.854em').addClass('loaded');
                content.loadingOverlay();
                $.get(url, function (data) {
                    content.loadingOverlay('remove');
                    content.html(data.html);
                });
            } else { content.css('min-height', '0px'); }
            $(this).blur();
            event.preventDefault();
        });
    };

    // Expand list item details on direct hashtag links
    CC.openListItemDetails = function () {
        if ($('.manage').length && window.location.hash && $(window.location.hash).length) {
            $(window.location.hash).find('.summary').first().click();
        }
    };

    // Ajax for manage list actions (clone and delete)
    CC.manageActionsAjax = function () {
        $('.manage').on(
            'click',
            'button[name^=action-]',
            function (e) {
                e.preventDefault();
                var button = $(this),
                    form = button.closest('form'),
                    url = form.prop('action'),
                    method = form.attr('method'),
                    replace = button.closest('.action-ajax-replace'),
                    success = function (response) {
                        var replacement = $(response.html);
                        if (!response.no_replace && replacement) {
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

    // Tags, suites, environments act as filter-links on list pages
    CC.directFilterLinks = function () {
        $('.listpage').on('click', '.filter-link', function (e) {
            var thisLink = $(this),
                name = thisLink.text(),
                type = thisLink.data('type');
            $('#filterform').find('.filter-group[data-name="' + type + '"] .filter-item label').filter(function () {
                return $(this).text() === name;
            }).closest('.filter-item').children('input').click();
            e.preventDefault();
        });
    };

    // Prepare filter-form for ajax-submit
    CC.filterFormAjax = function (container) {
        var context = $(container),
            filterForm = context.find('#filterform');

        filterForm.ajaxForm({
            beforeSubmit: function (arr, form, options) {
                context.find('.action-ajax-replace').loadingOverlay();
            },
            success: function (response) {
                var newList = $(response.html);
                context.find('.action-ajax-replace').loadingOverlay('remove');
                if (response.html) {
                    context.find('.action-ajax-replace').replaceWith(newList);
                    newList.find('.details').html5accordion();
                }
            }
        });
    };

    CC.listActionAjax = function (container, trigger) {
        var context = $(container);

        context.on('click', trigger, function (e) {
            var url = $(this).attr('href'),
                replaceList = $(this).closest('.action-ajax-replace');

            replaceList.loadingOverlay();

            $.get(url, function (response) {
                var newList = $(response.html);
                replaceList.loadingOverlay('remove');
                if (response.html) {
                    replaceList.replaceWith(newList);
                    newList.find('.details').html5accordion();
                }
            });

            e.preventDefault();
        });
    };

    return CC;

}(CC || {}, jQuery));
