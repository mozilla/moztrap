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

    var selectRuns = function(context) {
        var context = $(context),
            products = context.find('input[name="product"]'),
            cycles = context.find('input[name="cycle"]'),
            headers = context.find('h3 > a').click(function() {
                context.find('section').removeClass('focus');
                $(this).closest('section').addClass('focus');
            });
        products.live('click', function() {
            var product = $(this).data('id'),
                fakeAjaxCall = function(product, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + product + '_cycle_name_01" data-product="' + product + '" data-cycle="01">' +
                            '<label for="' + product + '_cycle_name_01">' +
                                '<span class="completion" data-perc="75">75%</span>' +
                                '<span class="title">' + product + ' cycle name 01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + product + '_cycle_name_02" data-product="' + product + '" data-cycle="02">' +
                            '<label for="' + product + '_cycle_name_02">' +
                                '<span class="completion" data-perc="100">100%</span>' +
                                '<span class="title">' + product + ' cycle name 02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + product + '_cycle_name_03" data-product="' + product + '" data-cycle="03">' +
                            '<label for="' + product + '_cycle_name_03">' +
                                '<span class="completion" data-perc="25">25%</span>' +
                                '<span class="title">' + product + ' cycle name 03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    callback(response);
                };
            fakeAjaxCall(
                product,
                function(data) {
                    $('section.cycles ul').html(data);
                    $('section.runs ul').html('');
                }
            );
            $(this).closest('section.products').removeClass('focus');
            context.find('section.runs').removeClass('focus');
            context.find('section.cycles').addClass('focus');
        });
        cycles.live('click', function() {
            var product = $(this).data('product'),
                cycleNumber = $(this).data('cycle'),
                fakeAjaxCall = function(product, cycleNumber, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + product + '_run_0' + cycleNumber + '_01">' +
                            '<label for="' + product + '_run_0' + cycleNumber + '_01">' +
                                '<span class="title">' + product + ' run 0' + cycleNumber + '-01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + product + '_run_0' + cycleNumber + '_02">' +
                            '<label for="' + product + '_run_0' + cycleNumber + '_02">' +
                                '<span class="title">' + product + ' run 0' + cycleNumber + '-02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + product + '_run_0' + cycleNumber + '_03">' +
                            '<label for="' + product + '_run_0' + cycleNumber + '_03">' +
                                '<span class="title">' + product + ' run 0' + cycleNumber + '-03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    callback(response);
                };
            fakeAjaxCall(
                product,
                cycleNumber,
                function(data) {
                    $('section.runs ul').html(data);
                }
            );
            $(this).closest('section.cycles').removeClass('focus');
            context.find('section.products').removeClass('focus');
            context.find('section.runs').addClass('focus');
        });
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
        selectRuns('#selectruns');
    });

})(jQuery);