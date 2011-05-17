var TCM = TCM || {};

(function($) {

    var autoFocus = function(trigger) {
        $(trigger).click(function() {
            if ($(this).parent().hasClass('open')) {
                $(this).parent().find('textarea').focus();
            }
        });
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
                            testCaseButtons(newCase);
                            TCM.addLoading('button, a', testcase);
                            $('.loadingCSS').detach();
                            autoFocus('details.stepfail > summary');
                            autoFocus('details.testinvalid > summary');
                        }
                    );
                }
            }
        );
    };

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
                $('.loading').removeClass("loading");
            }
        );
        $('#selectruns').html5finder( {
            expand: '#selectruns + #environment',
            expandTrigger: '#selectruns input[name="run"]',
            loading: true,
            horizontalScroll: false,
            selected: 'input:checked',
            notSelected: 'input:not(:checked)',
            header: 'header',
            section: 'section',
            section1class: 'products',
            section1item: 'input[name="product"]',
            section2class: 'cycles',
            section2item: 'input[name="cycle"]',
            section3class: 'runs',
            section3item: 'input[name="run"]'
        });
        $('#sandbox a.findertoggle').click(function() {
            $(this).add('#sandbox .finder').toggleClass('expanded').toggleClass('compact');
            return false;
        });
    });

})(jQuery);