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

                    if (type === 'tag') {
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
    // in the add case form.
    MT.filterProductTags = function (container) {
        var context = $(container),
            trigger = context.find('#id_product'),
            tags,
            filterTags = function () {
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
    // in the suite edit or add form
    MT.filterProductCases = function (container) {
        if ($(container).length > 0) {
            var product = $(container).find('#id_product');

            // if the product field is a select, then we know it's
            // editable and so we add the change handler.
            if (product.is("select")) {
                // update the cases list if this field changes
                product.change(function () {
                    var product = $('#id_product');
                    MT.doFilterProductCases(product.find('option:selected').data('product-id'), null);
                });
            }

            // we should load the cases on page load whether it's a
            // select or not.  But if no item is selected, it will have
            // no effect.
            $(function() {
                var product = $('#id_product');
                var product_id = null;
                var suite_id = $(".edit-suite").data("suite-id");

                // Get the correct product_id, depending on the type of the
                // id_product field.
                if (product.is("select")) {
                    // if none is selected, this will return "" which is
                    // caught in the doFilterProductCases method.
                    product_id = product.find("option:selected").val();
                }
                else if (product.is("input")) {
                    product_id = product.val();
                }
                MT.doFilterProductCases(product_id, suite_id);

            });

        }
    };

    // Use AJAX to get a set of cases filtered by product_id
    MT.doFilterProductCases = function (product_id, suite_id) {
        var cases_url = "/api/v1/suitecaseselection/?format=json&productversion__product=" + product_id
        var unselect = $(".multiunselected").find(".select");
        var select = $(".multiselected").find(".select");

        // This will be present when editing a suite, not creating a new one.
        // if a suite_id was passed in, then add it to the query params so that
        // we check for included cases.
        if (suite_id) {
            cases_url += "&for_suite=" + suite_id
        }
        if (product_id != "") {
            $.ajax({
                type: "GET",
                url: cases_url,
                context: document.body,
                beforeSend: function() {
                    unselect.loadingOverlay()
                    select.loadingOverlay()
                },
                success: function(response) {
                    /*
                        This ajax call will fetch 2 lists of cases.  It will look
                        like this:
                            objects: { selected: [case1, case2, ...],
                                       unselected: [case1, case2, ...]
                                       }
                        The selected section comes in sorted by order they fall in the suite.
                        remove the "Loading..." overlay once they're loaded up.
                     */
                    unselect.html(ich.case_select_item({"cases": response.objects.unselected}));
                    unselect.loadingOverlay("remove")

                    var sel_html = ich.case_select_item({"cases": response.objects.selected});
                    select.html(sel_html);
                    select.loadingOverlay("remove")

                },
                error: function(response) {
                    $(".multiselected").loadingOverlay("remove")
                    $(".multiunselected").loadingOverlay("remove")
                    console.error(response);
                }
            });
        }
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
