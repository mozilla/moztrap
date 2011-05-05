var TCM = TCM || {};

(function($) {

    TCM.testCaseButtons = function(context) {
        $(context).find("button").click(
            function(event) {
                event.preventDefault();
                event.stopPropagation();
                var button = $(this),
                    testcase = button.closest("details.test").addClass('loading'),
                    container = button.closest("div.form"),
                    data = {
                        action: button.attr("data-action")
                    },
                    inputs = container.find("input"),
                    post = true;
                container.find("textarea").add(inputs).each(
                    function() {
                        var val = $(this).val();
                        if (val) {
                            data[$(this).attr("name")] = val;
                        } else {
                            $(this).siblings("ul.errorlist").remove();
                            $(this).before(
                                "<ul class=errorlist><li>" +
                                    "This field is required." +
                                    "</li></ul>"
                            );
                            post = false;
                        }
                    }
                );
                if ( post ) {
                    $.post(
                        testcase.attr("data-action-url"),
                        data,
                        function(data) {
                            var id = testcase.attr("id");
                            testcase.replaceWith(data);
                            var newCase = $("#" + id);
                            summaryDetails(newCase);
                            testCaseButtons(newCase);
                            $('.loadingCSS').detach();
                        }
                    );
                }
                var addLoadingCSS = function() {
                    var vertHeight = (parseInt(testcase.css('height')) - parseInt(testcase.css('line-height'))) / 2 + 'px',
                        style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                    $('head').append(style);
                };
                addLoadingCSS();
            }
        );
    };

    TCM.autoFocus = function(trigger) {
        $(trigger).click(function() {
            if ($(this).parent().hasClass('open')) {
                $(this).parent().find('textarea').focus();
            }
        });
    };

})(jQuery);

$(function() {
    TCM.autoFocus('details.stepfail > summary');
    TCM.autoFocus('details.testinvalid > summary');
    TCM.testCaseButtons("details.test");
    $("div[role=main]").ajaxError(
        function(event, request, settings) {
            $(this).prepend(
                '<aside class="error">' + request.responseText + '</aside>'
            );
            $('.loadingCSS').detach();
            $('.loading').removeClass("loading");
        }
    );
});