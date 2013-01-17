/*jslint    browser:    true,
 indent:     4,
 confusion:  true,
 regexp:     true */
/*global    ich, jQuery, confirm, URI */

var MT = (function (MT, $) {

    'use strict';


    // Populate the list of available and included items on page load
    // and when the ``trigger_field`` value is changed.
    MT.populateMultiselectItems = function (opts) {
        var defaults = {
                container: 'body',
                data_attr: 'product-id',
                refetch_on_trigger: true,
                fetch_without_trigger_value: false
            },
            options = $.extend({}, defaults, opts);

        if ($(options.container).length) {
            var trigger = $(options.container).find(options.trigger_field);

            ////////
            //
            // ON CHANGE: when user changes the trigger field (product,
            // productversion, etc)
            //
            ////////

            // if the trigger field is a select, then we know it's
            // editable and so we add the change handler.
            if (trigger.is("select") && options.refetch_on_trigger) {
                // update the item list if this field changes
                trigger.change(function () {
                    var trigger_id = $(this).find('option:selected').data(
                            options.data_attr),
                        included_id = $(".edit-" + options.for_type).data(
                            options.for_type + "-id");
                    if (trigger_id || options.fetch_without_trigger_value) {
                        $(".multiselect").closest(
                            ".formfield").removeClass("hiddenfield");
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
                    else if (options.hide_without_trigger_value) {
                        $(".multiselect").closest(
                            ".formfield").addClass("hiddenfield");
                    }
                    else {
                        // the user selected the "----" option, so clear
                        // multiselect
                        $(".multiselect").find(".select").html("");
                        $(".multiselect").closest(
                            ".formfield").removeClass("hiddenfield");
                    }
                });
            }

            ////////
            //
            // ON PAGE LOAD
            //
            ////////

            // we should load the items on page load whether it's a
            // <select> or not.  But if no item is selected, it will have
            // no effect.  but ONLY do this call on page load if we have
            // a multi-select widget.  if not, it's pointless, because the
            // view has already given us the values we need to display
            // in a bulleted list.
            //
            if ($(options.container).find(".multiselect").length) {
                $(function () {
                    // the field items are filtered on (usu. product or
                    // productversion)
                    var trigger = $(options.trigger_field),
                        trigger_id,
                        // the id to check for included items (usu. suite_id,
                        // tag_id or run_id)
                        included_id = $(".edit-" + options.for_type).data(
                            options.for_type + "-id");

                    // Get the correct id, depending on whether it's readonly
                    // or rw.
                    if (trigger.is("select")) {
                        trigger_id = trigger.find("option:selected").data(
                            options.data_attr);
                    }
                    else if (trigger.is("input")) {
                        trigger_id = trigger.val();
                    }

                    // for some screens, you don't want to fetch if no product
                    // is set,
                    // but for some screens you may.
                    // usually this is set when editing, not set when creating
                    if (trigger_id || options.fetch_without_trigger_value) {
                        $(".multiselect").closest(
                            ".formfield").removeClass("hiddenfield");
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
                    else if (options.hide_without_trigger_value) {
                        $(".multiselect").closest(
                            ".formfield").addClass("hiddenfield");
                    }
                });
            }
        }
    };

    // cache for the ajax calls for multiselect items.
    var cache = {};

    // any ajax requests currently in progress so we can abort them if
    // we want to start a new one.
    var current_xhrs = {};

    // Use AJAX to get a set of items filtered by product_id
    MT.doPopulateMultiselect = function (
        ajax_url_root,
        ajax_trigger_filter,
        trigger_id,
        ich_template,
        ajax_for_field,
        included_id,
        use_latest) {

        var available = $(".multiunselected").find(".select"),
            included = $(".multiselected").find(".select"),
            avail_url = new URI(ajax_url_root);

        // if there are currently doing any ajax fetches for items, abort them
        // so we can do this new one.
        if (current_xhrs.include) {
            current_xhrs.include.abort();
        }
        if (current_xhrs.available) {
            current_xhrs.available.abort();
        }

        if (trigger_id) {
            // we may not have a trigger_id if the form supports fetching
            // without it.  (like tags)
            avail_url.addSearch(ajax_trigger_filter, trigger_id);
        }

        if (use_latest) {
            // get the ``latest`` case versions to display here

            // @@@ maybe we could check cookies here.  If productversion is
            // set, then use that instead.  But, garsh.. what if they have more
            // than one productversion filter pinned?  Have to check if the
            // productversion matched the product set in this form, but I
            // don't have that info.  Need it server side, or via ajax.
            // I COULD make the caseselection url smart enough to figure that
            // out, perhaps.
            avail_url.addSearch("latest", 1);
        }
        var incl_url = new URI(avail_url.toString());

        if (included_id) {
            avail_url.addSearch(ajax_for_field + "__ne", included_id);
            incl_url.addSearch(ajax_for_field, included_id);
        }

        if (available.length) {

            if (cache[avail_url.toString()]) {
                available.html(cache[avail_url.toString()]);
                if (included_id) {
                    // included_id means we're editing existing, not a new tag
                    included.html(cache[incl_url.toString()]);
                }
                else {
                    // if we switch products for a new case, we want to be sure
                    // we empty the included section, so you don't include
                    // cases from two different products
                    included.html("");
                }
            }
            else {
                // ajax fetch included first, then available

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
                var avail_complete = false,
                    incl_complete = false;

                // set the items of the available and included lists
                var setItems = function () {
                    if (incl_complete && avail_complete) {
                        included.loadingOverlay("remove");
                        included.html(cache[incl_url.toString()]);
                        available.loadingOverlay("remove");
                        available.html(cache[avail_url.toString()]);
                    }
                };

                // fetch included
                if (included_id) {
                    current_xhrs.include = $.ajax({
                        type: "GET",
                        url: incl_url.toString(),
                        context: document.body,
                        beforeSend: function () {
                            included.html("");
                            included.loadingOverlay();
                            included.find(".select").attr("disabled", true);
                        },
                        success: function (response) {
                            /*
                             The included section comes in sorted by order they
                             fall.
                             remove the "Loading..." overlay once they're
                             loaded up.
                             */
                            cache[incl_url.toString()] = ich_template(
                                {items: response.objects});
                            incl_complete = true;
                            setItems();
                            included.find(".select").attr("disabled", false);
                        },
                        error: function (response) {
                            $(".multiselected").loadingOverlay("remove");

                            // so that if the form is submitted when the ajax
                            // has failed, we don't try to update the items
                            // list, only update the other fields in the form.
                            included.find(".select").attr("disabled", true);

                            console.error(response);
                        },
                        always: function () {
                            delete current_xhrs.include;
                        }
                    });
                }
                else {
                    // if there's no included_id, this in a new item, and
                    // we just want it to be blank
                    included.html("");
                    incl_complete = true;
                }

                // fetch available items
                current_xhrs.available = $.ajax({
                    type: "GET",
                    url: avail_url.toString(),
                    context: document.body,
                    beforeSend: function () {
                        available.html("");
                        available.loadingOverlay();
                    },
                    success: function (response) {
                        /*
                         remove the "Loading..." overlay once they're loaded
                         up.
                         */
                        cache[avail_url.toString()] = ich_template(
                            {items: response.objects});
                        avail_complete = true;
                        setItems();

                    },
                    error: function (response) {
                        $(".multiunselected").loadingOverlay("remove");
                        console.error(response);
                    },
                    always: function () {
                        delete current_xhrs.include;
                    }
                });

            }
        }
    };

    return MT;

}(MT || {}, jQuery));
