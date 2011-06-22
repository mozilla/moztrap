var TCM = TCM || {};

(function($) {

    var autoFocus = function(trigger) {
        $(trigger).click(function() {
            if ($(this).parent().hasClass('open')) {
                $(this).parent().find('textarea').focus();
            }
        });
    };

    var breadcrumb = function(context) {
        $(context).find('.colcontent').each(function() {
            $(this).data('originalHTML', $(this).html());
        });
        $('.runtests-nav .secondary .breadcrumb').click(function() {
            if (!$('.drilldown.details').hasClass('open')) {
                $('.drilldown.details > .summary').click();
            }
            $(context).find('.colcontent').each(function() {
                $(this).html($(this).data('originalHTML'));
            });
            $(context).find('#' + $(this).data('id')).click();
            return false;
        });
    };

    var testCaseButtons = function(context) {
        $(context).find("button").click(
            function(event) {
                TCM.addLoading($(this).closest(context));
                event.preventDefault();
                event.stopPropagation();
                var button = $(this),
                    testcase = button.closest(".details.test"),
                    container = button.closest("div.form"),
                    data = {
                        action: button.data("action")
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
                            $('.overlay').detach();
                            $('.loading').removeClass('loading');
                            post = false;
                        }
                    }
                );
                if ( post ) {
                    $.post(
                        testcase.data("action-url"),
                        data,
                        function(data) {
                            var id = testcase.attr("id");
                            testcase.replaceWith(data);
                            var newCase = "#" + id;
                            $(newCase).find('.details').andSelf().html5accordion('.summary');
                            testCaseButtons(newCase);
                            $('.overlay').detach();
                            autoFocus('.details.stepfail > .summary');
                            autoFocus('.details.testinvalid > .summary');
                        }
                    );
                }
            }
        );
    };

    $(function() {
        autoFocus('.details.stepfail > .summary');
        autoFocus('.details.testinvalid > .summary');
        testCaseButtons("#run .details.test");
        breadcrumb('.selectruns');
    });

})(jQuery);
