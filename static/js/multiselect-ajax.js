/*jslint    browser:    true,
 indent:     4,
 confusion:  true,
 regexp:     true */
/*global    ich, jQuery, confirm, URI */

var MT = (function (MT, $) {

    'use strict';


    // Populate the list of available and selected items on page load
    // and when the ``trigger_field`` value is changed.
    MT.populateMultiselectItems = function (opts) {
        var defaults = {
                container: 'body',
                data_attr: 'product-id',
                refetch_on_trigger: true
            },
            options = $.extend({}, defaults, opts);
        var cache = {};


        if ($(options.container).length) {
            var product = $(options.container).find(options.trigger_field);

            // if the product field is a select, then we know it's
            // editable and so we add the change handler.
            if (product.is("select") && options.refetch_on_trigger) {
                // update the item list if this field changes
                product.change(function () {
                    var trigger_id = $(this).find('option:selected').data(options.data_attr),
                        included_id = $(".edit-" + options.for_type).data(
                            options.for_type + "-id");
                    if (trigger_id) {
                        MT.doPopulateMultiselect(
                            options.ajax_url_root,
                            options.ajax_trigger_filter,
                            trigger_id,
                            options.ich_template,
                            options.ajax_for_field,
                            included_id,
                            options.use_latest
                        );
                    }
                });
            }

            // we should load the items on page load whether it's a
            // <select> or not.  But if no item is selected, it will have
            // no effect.  but ONLY do this call on page load if we have
            // a multi-select widget.  if not, it's pointless, because the
            // view has already given us the values we need to display
            // in a bulleted list.
            //
            if ($(options.container).find(".multiselect").length) {
                $(function () {
                    // the field items are filtered on (usu. product or productversion)
                    var trigger = $(options.trigger_field);
                    var trigger_id;
                    // the id to check for included items (usu. suite_id or run_id)
                    var included_id = $(".edit-" + options.for_type).data(options.for_type + "-id");

                    // Get the correct product_id, depending on the type of the
                    // id_product field.
                    if (trigger.is("select")) {
                        trigger_id = trigger.find("option:selected").data(options.data_attr);
                    }
                    else if (trigger.is("input")) {
                        trigger_id = product.val();
                    }
                    if (trigger_id) {
                        var url = options.ajax_url_root + trigger_id;
                        // This will be present when editing a suite, not creating a new one.
                        MT.doPopulateMultiselect(
                            options.ajax_url_root,
                            options.ajax_trigger_filter,
                            trigger_id,
                            options.ich_template,
                            options.ajax_for_field,
                            included_id,
                            options.use_latest
                        );
                    }

                });
            }
        }
    };

    // cache for the ajax calls for cases of suites or suites of runs.
    var cache = {};

    // Use AJAX to get a set of items filtered by product_id
    MT.doPopulateMultiselect = function (
        ajax_url_root,
        ajax_trigger_filter,
        trigger_id,
        ich_template,
        ajax_for_field,
        included_id,
        use_latest) {

        var unselect = $(".multiunselected").find(".select"),
            select = $(".multiselected").find(".select"),
            unsel_url = new URI(ajax_url_root);



        unsel_url.addSearch(ajax_trigger_filter, trigger_id);
        if (use_latest) {
            // @@@ check cookies here.  If productversion is set, then use
            // that instead.  But, garsh.. what if they have more than one
            // productversion filter pinned?  Have to check if the
            // productversion matched the product set in this form, but I
            // don't have that info.  Need it server side, or via ajax.
            // I could make the caseselection url smart enough to figure that
            // out.
            unsel_url.addSearch("latest", 1);
        }
        var sel_url = new URI(unsel_url.toString());

        if (included_id) {
            unsel_url.addSearch(ajax_for_field + "__ne", included_id);
            sel_url.addSearch(ajax_for_field, included_id);
        }

        if (unselect.length) {

            if (cache[unsel_url.toString()]) {
                unselect.html(cache[unsel_url.toString()].unsel_html);
                select.html(cache[sel_url.toString()].sel_html);
            }
            else {
                // ajax fetch selected first, then unselected

                /*
                  Had wanted to show when each list was complete.  This could
                  be useful because the included list may often be shorter
                  and the user could see it while waiting for the available
                  list to load.

                  However, I was not able to find a reliable way to disable
                  drag and drop.  And if you drag from one list to another
                  before the destination list is done loading, it will blow
                  away the item you tracked to it.

                  Disable attr didn't seem to work on article items.  There
                  is a "draggable" property, but I couldn't find what would
                  actually prevent the dragging.

                 */
                var unsel_complete = false,
                    sel_complete = false;

                // fetch selected
                if (included_id) {
                    $.ajax({
                        type: "GET",
                        url: sel_url.toString(),
                        context: document.body,
                        beforeSend: function () {
                            select.loadingOverlay();
                        },
                        success: function (response) {
                            /*
                             The selected section comes in sorted by order they fall.
                             remove the "Loading..." overlay once they're loaded up.
                             */
                            var sel_html = ich_template({items: response.objects});
                            cache[sel_url.toString()] = sel_html;

                            sel_complete = true;
                            if (unsel_complete) {
                                select.loadingOverlay("remove");
                                select.html(sel_html);
                                unselect.loadingOverlay("remove");
                                unselect.html(cache[unsel_url.toString()]);
                            }
                        },
                        error: function (response) {
                            $(".multiselected").loadingOverlay("remove");
                            console.error(response);
                        }
                    });
                }
                else {
                    select.html("");
                    sel_complete = true;
                }

                // fetch unselected / available cases
                $.ajax({
                    type: "GET",
                    url: unsel_url.toString(),
                    context: document.body,
                    beforeSend: function () {
                        unselect.loadingOverlay();
                    },
                    success: function (response) {
                        /*
                         remove the "Loading..." overlay once they're loaded up.
                         */
                        var unsel_html = ich_template({items: response.objects});
                        cache[unsel_url.toString()] = unsel_html;

                        unsel_complete = true;
                        if (sel_complete) {
                            select.loadingOverlay("remove");
                            select.html(cache[sel_url.toString()]);
                            unselect.loadingOverlay("remove");
                            unselect.html(unsel_html);
                        }

                    },
                    error: function (response) {
                        $(".multiunselected").loadingOverlay("remove");
                        console.error(response);
                    }
                });

            }
        }
    };

    return MT;

}(MT || {}, jQuery));
