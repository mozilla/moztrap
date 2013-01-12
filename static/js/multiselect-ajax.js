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
                limit: 4,
                fetch_without_trigger_value: false
            },
            options = $.extend({}, defaults, opts),

            getUrls = function (
                trigger_id,
                included_id
            ) {
                var availableUrl = new URI(options.ajax_url_root),
                    includedUrl = null;

                availableUrl.addSearch("limit", options.limit);

                if (trigger_id) {
                    availableUrl.addSearch(options.ajax_trigger_filter, trigger_id);
                }
                if (options.use_latest) {
                    availableUrl.addSearch("latest", 1);
                }
                if (included_id) {
                    includedUrl = availableUrl.clone();
                    includedUrl.addSearch(options.ajax_for_field, included_id);

                    availableUrl.addSearch(options.ajax_for_field + "__ne", included_id);
                }

                return {
                    included: includedUrl,
                    available: availableUrl
                };
            };

        if ($(options.container).length) {
            var trigger = $(options.container).find(options.trigger_field),
                ms = $(".multiselect");


            // initialize the multiselect widget to use the ichTemplate
            ms.multiselect({
                ich_template: options.ich_template,
                filter_type_map: options.filter_type_map
            });


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
                        ms.closest(
                            ".formfield").removeClass("hiddenfield");

                        var urls = getUrls(trigger_id, included_id);
                        ms.multiselect("populateBothLists",
                            urls.available,
                            urls.included,
                            options.ich_template,
                            options.filter_type_map
                        );
                    }
                    else if (options.hide_without_trigger_value) {
                        ms.closest(
                            ".formfield").addClass("hiddenfield");
                    }
                    else {
                        // the user selected the "----" option, so clear
                        // multiselect
                        ms.find(".select").html("");
                        ms.closest(
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
                        ms.closest(
                            ".formfield").removeClass("hiddenfield");
                        var urls = getUrls(trigger_id, included_id);
                        ms.multiselect("populateBothLists",
                            urls.available,
                            urls.included,
                            options.ich_template,
                            options.filter_type_map
                        );
                    }
                    else if (options.hide_without_trigger_value) {
                        ms.closest(
                            ".formfield").addClass("hiddenfield");
                    }
                });
            }
        }
    };

    return MT;

}(MT || {}, jQuery));
