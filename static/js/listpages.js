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
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    // Ajax-load list-page list item contents
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
    CC.openListItemDetails = function (context) {
        if ($(context).length && window.location.hash && $(window.location.hash).length) {
            $(window.location.hash).find('.summary').first().click();
            window.location.hash = '';
        }
    };

    // Ajax for manage list actions (clone and delete)
    CC.manageActionsAjax = function (context) {
        $(context).on(
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

    // Hijack Manage/Results list sorting and pagination links to use Ajax
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
                    newList.trigger('after-replace', [newList]);
                }
            });

            e.preventDefault();
        });
    };

    // Show/hide item-status dropdown
    CC.itemStatusDropdown = function (container) {
        var context = $(container),
            counter = 0;

        context.on('click', '.itemlist .listitem .status .status-select .status-title', function (e) {
            var summary = $(this),
                status = summary.closest('.status-select'),
                details = status.find('.status-options'),
                thisCounter = status.data('counter');

            status.toggleClass('open');

            if (status.hasClass('open')) {
                details.slideDown('fast');
                if (!thisCounter) {
                    counter = counter + 1;
                    thisCounter = counter;
                    status.data('counter', thisCounter);
                }
                $(document).on('click.statusDropdown.' + thisCounter, function (e) {
                    if ($(e.target).parents().andSelf().index(status) === -1) {
                        if (status.hasClass('open')) {
                            status.removeClass('open');
                            details.slideUp('fast');
                        }
                        $(document).off('click.statusDropdown.' + thisCounter);
                    }
                });
            } else {
                details.slideUp('fast');
                $(document).off('click.statusDropdown.' + thisCounter);
            }
        });

        context.on('before-replace', '.itemlist.action-ajax-replace', function () {
            $(document).off('click.statusDropdown');
        });
    };

    return CC;

}(CC || {}, jQuery));