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
        $('#listcontent').on('click', '.items .item.details', function (event) {
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

    return CC;

}(CC || {}, jQuery));
