/*jslint    browser:    true,
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    // Ajax-load list-page list item contents
    MT.loadListItemDetails = function () {
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
    MT.openListItemDetails = function (context) {
        if ($(context).length && window.location.hash && $(window.location.hash).length) {
            $(window.location.hash).find('.summary').first().click();
            window.location.hash = '';
        }
    };

    // Ajax for manage list actions (clone and delete)
    MT.manageActionsAjax = function (context) {
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
    MT.listActionAjax = function (container, trigger) {
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
    MT.itemStatusDropdown = function (container) {
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

    // Show/hide "share this list" dropdown to display url with filtering
    // so the user can copy and share it.
    MT.shareListUrlDropdown = function (container) {
        var context = $(container),
            counter = 0;

        context.on('click', '.share-list', function (e) {
            var shareList = $(this),
                popup = shareList.find('.share-list-popup'),
                text = popup.find('.url-text');


            var actionUrl = $(".action-ajax-replace").attr("action");
            var dataUrl = $(".action-ajax-replace").data("ajax-update-url");
            var url = null;
            if (actionUrl != undefined && actionUrl != false) {
                url = $(location).attr("host") + actionUrl
            } else {
                url = $(location).attr("host") + dataUrl
            }

                    text.val(url);

            shareList.toggleClass('open');
            if (shareList.hasClass('open')) {
                popup.slideDown('fast');
                text.focus();
                text.select();
                $(document).on('click.shareDropdown', function (e) {
                    if ($(e.target).parents().andSelf().index(shareList) === -1) {
                        if (shareList.hasClass('open')) {
                            shareList.removeClass('open');
                            popup.slideUp('fast');
                        }
                        $(document).off('click.shareDropdown');
                    }
                });
            } else {
                popup.slideUp('fast');
                $(document).off('click.shareDropdown');
            }
        });
    };

    return MT;

}(MT || {}, jQuery));