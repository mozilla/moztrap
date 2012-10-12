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
    MT.populateMultiselectItems = function (opts) {
        var defaults = {
                container: 'body',
                data_attr: 'product-id',
                refetch_on_trigger: true
            },
            options = $.extend({}, defaults, opts)


        if ($(opts.container).length > 0) {
            var product = $(opts.container).find(opts.trigger_field);

            // if the product field is a select, then we know it's
            // editable and so we add the change handler.
            if (product.is("select") && options.refetch_on_trigger) {
                // update the cases list if this field changes
                product.change(function () {
                    var product = $(opts.trigger_field);
                    var trigger_id = product.find('option:selected').data(options.data_attr)
                    var url = opts.ajax_url_root + trigger_id
                    var included_id = $(".edit-" + opts.for_type).data(opts.for_type + "-id");
                    if (included_id) {
                        url += "&for_" + opts.for_type + "=" + included_id
                    }
                    MT.doPopulateMultiselect(url, opts.ich_template);
                });
            }

            // we should load the cases on page load whether it's a
            // select or not.  But if no item is selected, it will have
            // no effect.
            $(function() {
                // the field items are filtered on (usu. product or productversion)
                var trigger = $(opts.trigger_field);
                var trigger_id;
                // the id to check for included items (usu. suite_id or run_id)
                var included_id = $(".edit-" + opts.for_type).data(opts.for_type + "-id");

                // Get the correct product_id, depending on the type of the
                // id_product field.
                if (trigger.is("select")) {
                    // if none is selected, this will return "" which is
                    // caught in the doFilterProductCases method.
                    trigger_id = trigger.find("option:selected").data(options.data_attr);
                }
                else if (trigger.is("input")) {
                    trigger_id = product.val();
                }
                if (trigger_id != "") {
                    var url = opts.ajax_url_root + trigger_id
                    // This will be present when editing a suite, not creating a new one.
                    if (included_id) {
                        url += "&for_" + opts.for_type + "=" + included_id
                    }

                    MT.doPopulateMultiselect(url, opts.ich_template);
                }

            });

        }
    };

    // Use AJAX to get a set of cases filtered by product_id
    MT.doPopulateMultiselect = function (url, ich_template) {
        var unselect = $(".multiunselected").find(".select");
        var select = $(".multiselected").find(".select");

        $.ajax({
            type: "GET",
            url: url,
            context: document.body,
            beforeSend: function() {
                unselect.loadingOverlay()
                select.loadingOverlay()
            },
            success: function(response) {
                /*
                    This ajax call will fetch 2 lists of items.  It will look
                    like this:
                        objects: { selected: [item1, item2, ...],
                                   unselected: [item1, item2, ...]
                                   }
                    The selected section comes in sorted by order they fall.
                    remove the "Loading..." overlay once they're loaded up.
                 */
                unselect.html(ich_template({"items": response.objects.unselected}));
                unselect.loadingOverlay("remove")

                var sel_html = ich_template({"items": response.objects.selected});
                select.html(sel_html);
                select.loadingOverlay("remove")

            },
            error: function(response) {
                $(".multiselected").loadingOverlay("remove")
                $(".multiunselected").loadingOverlay("remove")
                console.error(response);
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
