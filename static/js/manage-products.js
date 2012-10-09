/*jslint    browser:    true,
            indent:     4,
            confusion:  true,
            regexp:     true */
/*global    ich, jQuery, confirm */

var MT = (function (MT, $) {

    'use strict';

    // Filter form options based on trigger form selection
    MT.formOptionsFilter = function (opts) {
        var defaults = {
                container: 'body',
                data_attr: 'product-id',
                trigger_sel: '.trigger',
                target_sel: '.target',
                option_sel: 'option',
                multiselect_widget_bool: false,
                optional: false,
                callback: null
            },
            options = $.extend({}, defaults, opts),
            context = $(options.container),
            trigger = context.find(options.trigger_sel),
            target,
            allopts,
            doFilter,
            filterFilters;
        if (context.length) {
            target = context.find(options.target_sel);
            allopts = target.find(options.option_sel).clone();

            filterFilters = function (items) {
                context.find('.multiunselected .visual .filter-group:not(.keyword) input[type="checkbox"]').each(function () {
                    var thisFilter = $(this),
                        type = thisFilter.data('name'),
                        filter = thisFilter.closest('.filter-item').find('.onoffswitch').text().toLowerCase(),
                        excludeThisFilter = false;

                    if (type === 'status') {
                        if (!(items.find('.status span').filter(function () { return $(this).text().toLowerCase() === filter; }).length)) {
                            excludeThisFilter = true;
                        }
                    } else if (type === 'tag') {
                        if (!(items.find('.tags a').filter(function () { return $(this).text().toLowerCase() === filter; }).length)) {
                            excludeThisFilter = true;
                        }
                    } else if (type === 'author') {
                        if (!(items.find('.author span').filter(function () { return $(this).text().toLowerCase() === filter; }).length)) {
                            excludeThisFilter = true;
                        }
                    } else {
                        if (!(items.filter(function () { return $(this).find('.' + type).text().toLowerCase() === filter; }).length)) {
                            excludeThisFilter = true;
                        }
                    }

                    if (excludeThisFilter) {
                        thisFilter.attr('disabled', 'disabled');
                    } else {
                        thisFilter.removeAttr('disabled');
                    }
                });
            };

            doFilter = function () {
                var key = trigger.find('option:selected').data(options.data_attr),
                    newopts = allopts.clone().filter(function () {
                        return $(this).data(options.data_attr) === key;
                    });
                if (options.optional && key) {
                    target.find(options.option_sel).filter(function () { return $(this).val(); }).remove();
                    target.append(newopts);
                } else {
                    target.html(newopts);
                }
                if (options.multiselect_widget_bool) {
                    context.find('.visual .filter-group input[type="checkbox"]:checked').prop('checked', false).change();
                    context.find('.multiselected .select').empty();
                    filterFilters(newopts);
                }
                if (options.callback) {
                    options.callback(context);
                }
            };

            if (trigger.is('select') && !(context.find('.multiselected .select').find(options.option_sel).length)) {
                doFilter();
                trigger.change(doFilter);
            } else if (options.multiselect_widget_bool) {
                filterFilters(target.add(context.find('.multiselected .select')).find(options.option_sel));
            }
        }
    };

    // Filter product-specific tags when changing case product
    MT.filterProductTags = function (container) {
        var context = $(container),
            trigger = context.find('#id_product'),
            tags,
            filterTags = function () {
                console.log("mac");
                if (trigger.find('option:selected').data('product-id')) {
                    tags = context.find('.tagging .taglist .tag-item');
                    tags.filter(function () {
                        var input = $(this).find('input');
                        if (input.data('product-id')) {
                            return input.data('product-id') !== trigger.find('option:selected').data('product-id');
                        } else {
                            return false;
                        }
                    }).each(function () {
                        $(this).find('label').click();
                    });
                }
            };

        trigger.change(filterTags);
    };

    // Filter product-specific cases when changing product
    MT.filterProductCasesOnChange = function (container) {
        if ($(container).length > 0) {
            $('#id_product').change(MT.filterCasesNewSuite);
        }
    };

    // Filter product-specific cases on page load
    MT.filterProductCasesOnReady = function (container) {
        if ($(container).length > 0) {
            $(MT.filterCasesEditSuite);
        }
        else if ($(container).length > 0) {
            $('#id_product').change(MT.filterCasesNewSuite);
        }
    };

    // load product cases on the new suite page
    MT.filterCasesNewSuite = function () {
        MT.doFilterProductCases($('option:selected').data('product-id'), null);
    }

    // load product cases on the edit suite page
    MT.filterCasesEditSuite = function() {
        MT.doFilterProductCases($("#id_product").val(), $(".edit-suite").data("suite-id"));

    }

    // Use AJAX to get a set of cases filtered by product_id
    MT.doFilterProductCases = function (product_id, suite_id) {
        var cases_url = "/api/v1/suitecaseselection/?format=json&productversion__product=" + product_id
        if (suite_id) {
            cases_url += "&for_suite=" + suite_id
        }
        $.ajax({
            type: "GET",
            url: cases_url,
            context: document.body,
            success: function(response) {
                /*
                  We need to fetch those that are NOT selected, and those that
                  are.  So use two separate AJAX calls.
                  1. all possible cases
                  2. selected for this suite (if any)
                  3. remove list 2 from list 1
                  or
                  Perhaps we can call 1 with the suite ID and not return them?
                 */
                var unselect = $(".multiunselected").find(".select");
                var unsel_html = ich.case_select_item({"cases": response.objects.unsel});
                unselect.html(unsel_html);

                var select = $(".multiselected").find(".select");
                var sel_html = ich.case_select_item({"cases": response.objects.sel});
                select.html(sel_html);

            },
            error: function(response) {
                console.error(response);
            },
            loading: function() {
                var select = $(".multiunselected").find(".select");
                select.html("<p>Loading...</p>");
            }
        });
    };

    // Adding/removing attachments on cases
    MT.testcaseAttachments = function (container) {
        var context = $(container),
            counter = 0,
            label = context.find('label[for="id_add_attachment"]'),
            attachmentList = context.find('.attachlist'),
            inputList = context.find('.add-attachment-field');

        label.click(function (e) {
            e.preventDefault();
            var id = $(this).attr('for');
            context.find('#' + id).click();
        });

        context.on('change', 'input[name="add_attachment"]', function () {
            var input = $(this),
                inputID = input.attr('id'),
                filename = input.val().replace(/^.*\\/, ''),
                attachment,
                newInput;

            attachment = ich.case_attachment({
                name: filename,
                input: inputID,
                counter: counter
            });
            counter = counter + 1;
            newInput = ich.case_attachment_input({ counter: counter });
            attachmentList.append(attachment);
            attachmentList.find('.none').remove();
            inputList.append(newInput);
            label.attr('for', 'id_add_attachment_' + counter);
        });

        attachmentList.on('change', '.check', function () {
            var input = $(this),
                inputID = input.data('id'),
                attachment = input.closest('.attachment-item');

            if (attachment.hasClass('new')) {
                context.find('#' + inputID).remove();
                attachment.remove();
            }
        });
    };

    return MT;

}(MT || {}, jQuery));
