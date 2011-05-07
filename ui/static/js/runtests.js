(function($) {

    var accordionButtons = function(context) {
        $(context).find("button, a").click(
            function(event) {
                // prevent it from triggering the html5accordion
                event.stopPropagation();
                var button = $(this),
                    immediateContext = button.closest(context).addClass('loading');

                var addLoadingCSS = function() {
                    var vertHeight = (parseInt(immediateContext.css('height'), 10) - parseInt(immediateContext.css('line-height'), 10)) / 2 + 'px',
                        style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                    $('head').append(style);
                };
                addLoadingCSS();
            }
        );
    };

    var testCaseButtons = function(context) {
        $(context).find("button").click(
            function(event) {
                event.preventDefault();
                event.stopPropagation();
                var button = $(this),
                    testcase = button.closest(context),
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
                            $('.loadingCSS').detach();
                            $('.loading').removeClass("loading");
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
                            var newCase = "#" + id;
                            $(newCase).find('details').andSelf().html5accordion('summary');
                            accordionButtons(newCase);
                            testCaseButtons(newCase);
                            $('.loadingCSS').detach();
                        }
                    );
                }
            }
        );
    };

    var autoFocus = function(trigger) {
        $(trigger).click(function() {
            if ($(this).parent().hasClass('open')) {
                $(this).parent().find('textarea').focus();
            }
        });
    };

    $(function() {
        autoFocus('details.stepfail > summary');
        autoFocus('details.testinvalid > summary');
        accordionButtons('details');
        accordionButtons('.details');
        testCaseButtons("details.test");
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

})(jQuery);