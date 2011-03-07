function testCaseButtons(context) {
    $(context).find("button").click(
        function(event) {
            event.preventDefault();
            event.stopPropagation();
            var button = $(this);
            var testcase = button.closest("details.test").addClass('loading');
            var container = button.closest("div.form");
            var data = {
                action: button.attr("data-action")
            };
            var inputs = container.find("input");
            var post = true;
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
                    });
            }
            function addLoadingCSS() {
                var vertHeight = (parseInt(testcase.css('height')) - parseInt(testcase.css('line-height'))) / 2 + 'px';
                var style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                $('head').append(style);
            }
            addLoadingCSS();
        });
}

function autoFocus(trigger) {
    $(trigger).click(function() {
        if ($(this).parent().hasClass('open')) {
            $(this).parent().find('textarea').focus();
        }
    });
}

$(function() {
    autoFocus('details.stepfail > summary');
    autoFocus('details.testinvalid > summary');
    testCaseButtons("details.test");
    $("div[role=main]").ajaxError(
        function(event, request, settings) {
            $(this).prepend(
                '<aside class="error">' + request.responseText + '</aside>'
            );
            $('.loadingCSS').detach();
        });
});
