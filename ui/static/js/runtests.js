/*jslint    browser:    true,
            indent:     4,
            confusion:  true
*/
/*global    ich,
            jQuery
*/

(function ($) {

    'use strict';

    // Add focus to ``invalid`` and ``fail`` textboxes when expanded
    var autoFocus = function (trigger) {
        $(trigger).click(function () {
            if ($(this).parent().hasClass('open')) {
                $(this).parent().find('textarea').focus();
            }
        });
    },

        // Open hierarchical navigation directly to clicked breadcrumb link
        breadcrumb = function (context) {
            $(context).find('.colcontent').each(function () {
                $(this).data('originalHTML', $(this).html());
            });
            $('.runtests-nav .secondary .breadcrumb').click(function () {
                if (!$('.drilldown.details').hasClass('open')) {
                    $('.drilldown.details > .summary').click();
                }
                $(context).find('.colcontent').each(function () {
                    $(this).html($(this).data('originalHTML'));
                });
                $(context).find('#' + $(this).data('id')).click();
                return false;
            });
        },

        // Ajax submit runtest forms
        testCaseButtons = function (context) {
            $(context).find("button").click(
                function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    var button = $(this),
                        testcase = button.closest(".details.test"),
                        container = button.closest("div.form"),
                        data = { action: button.data("action") },
                        inputs = container.find("input"),
                        post = true;
                    testcase.loadingOverlay();
                    container.find("textarea").add(inputs).each(function () {
                        var val = $(this).val();
                        if (val) {
                            data[$(this).attr("name")] = val;
                        } else {
                            $(this).siblings("ul.errorlist").remove();
                            $(this).before(ich.runtests_form_error());
                            testcase.loadingOverlay('remove');
                            post = false;
                        }
                    });
                    if (post) {
                        $.post(
                            testcase.data("action-url"),
                            data,
                            function (data) {
                                var id = testcase.attr("id"),
                                    newCase;
                                testcase.replaceWith(data.html);
                                newCase = "#" + id;
                                $(newCase).find('.details').andSelf().html5accordion('.summary');
                                testCaseButtons(newCase);
                                $(newCase).loadingOverlay('remove');
                                autoFocus('.details.stepfail > .summary');
                                autoFocus('.details.testinvalid > .summary');
                            }
                        );
                    }
                }
            );
        };

    $(function () {
        autoFocus('.details.stepfail > .summary');
        autoFocus('.details.testinvalid > .summary');
        testCaseButtons("#run .details.test");
        breadcrumb('.selectruns');
    });

}(jQuery));
