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

    var selectRuns = function(context, environments) {
        var context = $(context),
            environments = $(environments).hide(),
            products = context.find('input[name="product"]:not(".selected")'),
            cycles = context.find('input[name="cycle"]:not(".selected")'),
            runs = context.find('input[name="run"]:not(".selected")'),
            headers = context.find('h3 > a').click(function() {
                context.find('section').removeClass('focus');
                $(this).closest('section').addClass('focus');
                $(this).blur();
            }),
            addSelectedClass = function() {
                context.find('input:checked').addClass('selected');
                context.find('input:not(:checked)').removeClass('selected');
            };
        context.find('header').each(function() {
            var scrollbarWidth = $(this).closest('section').css('width') - $(this).children('li').css('width');
            $(this).css('right', scrollbarWidth);
        });
        products.live('click', function() {
            var productName = $(this).data('id'),
                fakeAjaxCall = function(productName, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_01" data-product="' + productName + '" data-cycle="01">' +
                            '<label for="' + productName + '_cycle_name_01">' +
                                '<span class="completion" data-perc="75">75%</span>' +
                                '<span class="title">' + productName + ' cycle name 01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_02" data-product="' + productName + '" data-cycle="02">' +
                            '<label for="' + productName + '_cycle_name_02">' +
                                '<span class="completion" data-perc="100">100%</span>' +
                                '<span class="title">' + productName + ' cycle name 02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_03" data-product="' + productName + '" data-cycle="03">' +
                            '<label for="' + productName + '_cycle_name_03">' +
                                '<span class="completion" data-perc="25">25%</span>' +
                                '<span class="title">' + productName + ' cycle name 03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_04" data-product="' + productName + '" data-cycle="04">' +
                            '<label for="' + productName + '_cycle_name_04">' +
                                '<span class="completion" data-perc="17">17%</span>' +
                                '<span class="title">' + productName + ' cycle name 04</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_05" data-product="' + productName + '" data-cycle="05">' +
                            '<label for="' + productName + '_cycle_name_05">' +
                                '<span class="completion" data-perc="50">50%</span>' +
                                '<span class="title">' + productName + ' cycle name 05</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_06" data-product="' + productName + '" data-cycle="06">' +
                            '<label for="' + productName + '_cycle_name_06">' +
                                '<span class="completion" data-perc="83">83%</span>' +
                                '<span class="title">' + productName + ' cycle name 06</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    if (productName === 'tcm') {
                        var response =
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_01" data-product="' + productName + '" data-cycle="01">' +
                                '<label for="' + productName + '_cycle_name_01">' +
                                    '<span class="completion" data-perc="75">75%</span>' +
                                    '<span class="title">' + productName + ' cycle name 01</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_02" data-product="' + productName + '" data-cycle="02">' +
                                '<label for="' + productName + '_cycle_name_02">' +
                                    '<span class="completion" data-perc="100">100%</span>' +
                                    '<span class="title">' + productName + ' cycle name 02</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="cycle" value="" id="' + productName + '_cycle_name_03" data-product="' + productName + '" data-cycle="03">' +
                                '<label for="' + productName + '_cycle_name_03">' +
                                    '<span class="completion" data-perc="25">25%</span>' +
                                    '<span class="title">' + productName + ' cycle name 03</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>';
                    }
                    function callbackfn() { callback(response); }
                    window.setTimeout(callbackfn, 300);
                };
            fakeAjaxCall(
                productName,
                function(data) {
                    $('section.cycles ul').html(data);
                    $('.loadingCSS').detach();
                    $('.loading').removeClass("loading");
                }
            );
            $('section.runs ul, section.cycles ul').empty();
            environments.slideUp();
            context.find('section.products, section.runs').removeClass('focus');
            context.find('section.cycles').addClass('focus');
            addSelectedClass();
        });
        cycles.live('click', function() {
            var productName = $(this).data('product'),
                cycleNumber = $(this).data('cycle'),
                fakeAjaxCall = function(productName, cycleNumber, callback) {
                    var response =
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_01">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_01">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-01</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_02">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_02">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-02</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_03">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_03">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-03</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_04">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_04">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-04</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_05">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_05">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-05</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>' +
                        '<li>' +
                            '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_06">' +
                            '<label for="' + productName + '_run_0' + cycleNumber + '_06">' +
                                '<span class="title">' + productName + ' run 0' + cycleNumber + '-06</span>' +
                                '<time class="start">01/07/2011</time>' +
                                '<time class="end">11/10/2011</time>' +
                            '</label>' +
                        '</li>';
                    if (cycleNumber === 1) {
                        var response =
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_01">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_01">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-01</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_02">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_02">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-02</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_03">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_03">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-03</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>' +
                            '<li>' +
                                '<input type="radio" name="run" value="" id="' + productName + '_run_0' + cycleNumber + '_04">' +
                                '<label for="' + productName + '_run_0' + cycleNumber + '_04">' +
                                    '<span class="title">' + productName + ' run 0' + cycleNumber + '-04</span>' +
                                    '<time class="start">01/07/2011</time>' +
                                    '<time class="end">11/10/2011</time>' +
                                '</label>' +
                            '</li>';
                    }
                    function callbackfn() { callback(response); }
                    window.setTimeout(callbackfn, 300);
                };
            fakeAjaxCall(
                productName,
                cycleNumber,
                function(data) {
                    $('section.runs ul').html(data);
                    $('.loadingCSS').detach();
                    $('.loading').removeClass("loading");
                }
            );
            $('section.runs ul').empty();
            environments.slideUp();
            context.find('section.products, section.cycles').removeClass('focus');
            context.find('section.runs').addClass('focus');
            addSelectedClass();
        });
        runs.live('click', function() {
            environments.slideDown();
            addSelectedClass();
        });
        $('input.selected').live('click', function() {
            context.find('section').removeClass('focus');
            $(this).closest('section').addClass('focus');
        });
        var addLoading = function(trigger, target) {
            $(trigger).live('click', function() {
                var container = $(this).closest(target).next(target),
                    addLoadingCSS = function() {
                        var vertHeight = (parseInt(container.css('height'), 10) - parseInt(container.css('line-height'), 10)) / 2 + 'px',
                            style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                        $('head').append(style);
                    };
                container.addClass('loading');
                addLoadingCSS();
            });
        };
        addLoading('input[name="product"]:not(".selected"), input[name="cycle"]:not(".selected")', 'section.col');
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
        selectRuns('#selectruns', '#selectruns + #environment');
        $('#sandbox a.findertoggle').click(function() {
            $(this).add('#sandbox .finder').toggleClass('expanded').toggleClass('compact');
            return false;
        });
    });

})(jQuery);