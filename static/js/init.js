/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var MT = (function (MT, $) {

    'use strict';

    $(function () {
        // plugins
        $('.details:not(html)').html5accordion();
        $('#messages ul').messages({
            handleAjax: true,
            closeLink: '.message'
        });
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('.multiselect').multiselect();
        $('#filter').customAutocomplete({
            textbox: '#text-filter',
            inputList: '.visual .filter-group:not(.keyword)',
            newInputList: '.visual .filter-group.keyword',
            multipleCategories: true,
            allowNew: true,
            autoSubmit: true,
            newInputTextbox: 'input[type="text"]',
            fakePlaceholder: true,
            initialFocus: true,
            inputsNeverRemoved: true,
            prefix: 'filter',
            debounce: true
        });
        $('#clientfilter').customAutocomplete({
            textbox: '#text-filter',
            inputList: '.visual .filter-group:not(.keyword)',
            newInputList: '.visual .filter-group.keyword',
            multipleCategories: true,
            allowNew: true,
            newInputTextbox: 'input[type="text"]',
            triggerSubmit: null,
            fakePlaceholder: true,
            initialFocus: true,
            inputsNeverRemoved: true,
            prefix: 'filter',
            debounce: true
        });
        $('.tagging').customAutocomplete({
            textbox: '#id_add_tags',
            ajax: true,
            url: $('#id_add_tags').data('autocomplete-url'),
            extraDataName: 'product-id',
            extraDataFn: function () {
                var product_sel = $('#id_product'),
                    selectedIndex = product_sel.prop('selectedIndex'),
                    tagging_container = $('.case-form .tagging'),
                    productID;
                if (tagging_container.data('product-id')) {
                    productID = tagging_container.data('product-id');
                } else if (selectedIndex && selectedIndex !== 0) {
                    productID = product_sel.find('option:selected').data('product-id');
                }
                return productID;
            },
            inputList: '.taglist',
            triggerSubmit: null,
            allowNew: true,
            restrictAllowNew: true,
            inputType: 'tag',
            noInputsNote: true,
            prefix: 'tag',
            pinable: false
        });
        $('#editprofile .add-item, #editproductversionenvs .add-item').customAutocomplete({
            textbox: '#env-elements-input',
            inputList: '.env-element-list',
            ajax: true,
            url: $('#env-elements-input').data('autocomplete-url'),
            hideFormActions: true,
            inputType: 'element',
            caseSensitive: true,
            prefix: 'element'
        });
        $('.multiselect .multiunselected .selectsearch').customAutocomplete({
            textbox: '#search-add',
            inputList: '.visual .filter-group:not(.keyword)',
            newInputList: '.visual .filter-group.keyword',
            multipleCategories: true,
            allowNew: true,
            triggerSubmit: null,
            inputsNeverRemoved: true,
            prefix: 'filter',
            debounce: true,
            pinable: false
        });
        $('.runsdrill').html5finder({
            loading: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            callback: function () {
                $('.runsdrill .runenvselect').slideUp('fast');
            },
            lastChildCallback: function (choice) {
                var environments = $('.runsdrill .runenvselect').css('min-height', '169px').slideDown('fast'),
                    ajaxUrl = $(choice).data('sub-url');
                environments.loadingOverlay();
                $.get(ajaxUrl, function (data) {
                    environments.loadingOverlay('remove');
                    environments.replaceWith(data.html);
                    MT.filterEnvironments('#runtests-environment-form');
                });
            }
        });
        $('.managedrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            numberCols: 4
        });
        $('.resultsdrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            numberCols: 4
        });

        // local.js
        MT.inputHadFocus();

        // account.js
        MT.changePwdCancel();

        // listpages.js
        MT.loadListItemDetails();
        MT.manageActionsAjax('.manage, .manage-form');
        MT.listActionAjax(
            '.manage, .results, .run',
            '.listordering .sortlink, .pagination .prev, .pagination .next, .pagination .page, .perpage a'
        );
        MT.itemStatusDropdown('.manage');
        MT.shareListUrlDropdown('.listpage');

        // filtering.js
        MT.toggleAdvancedFiltering('.magicfilter');
        MT.preventCaching('#filter');
        MT.directFilterLinks();
        MT.filterFormAjax('.manage, .results, .run');
        MT.clientSideFilter({container: '#envnarrowing'});
        MT.pinFilter();
        MT.updatePageForExistingPinnedFilters();

        // manage-products.js
        MT.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_productversion',
            no_default: true
        });
        MT.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_suite',
            optional: true
        });
        MT.formOptionsFilter({
            container: '#productversion-add-form',
            trigger_sel: '#id_product',
            target_sel: '#id_clone_from',
            optional: true,
            callback: function (context) {
                context.find('#id_clone_from option:last-child').prop('selected', true);
            }
        });
        MT.filterProductTags('#single-case-add, #bulk-case-add');
        MT.testcaseAttachments('.case-form .attach');

        // multiselect-ajax.js
        MT.populateMultiselectItems({
            container: '#suite-edit-form, #suite-add-form',
            trigger_field: '#id_product',
            ajax_url_root: "/api/v1/caseselection/?format=json&limit=0",
            ajax_trigger_filter: "productversion__product",
            ajax_for_field: "case__suites",
            for_type: "suite",
            ich_template: ich.case_select_item,
            use_latest: true
        });
        MT.populateMultiselectItems({
            container: '#tag-add-form, #tag-edit-form',
            trigger_field: '#id_product',
            ajax_url_root: "/api/v1/caseversionselection/?format=json&limit=0",
            ajax_trigger_filter: "productversion__product",
            ajax_for_field: "tags",
            for_type: "tag",
            ich_template: ich.caseversion_select_item,
            hide_without_trigger_value: true
        });
        MT.populateMultiselectItems({
            container: '#run-add-form',
            trigger_field: '#id_productversion',
            ajax_url_root: "/api/v1/suiteselection/?format=json&limit=0",
            ajax_trigger_filter: "product",
            ajax_for_field: "runs",
            for_type: "run",
            ich_template: ich.suite_select_item
        });
        MT.populateMultiselectItems({
            container: '#run-edit-form',
            trigger_field: '#id_productversion',
            ajax_url_root: "/api/v1/suiteselection/?format=json&limit=0",
            ajax_trigger_filter: "product",
            ajax_for_field: "runs",
            for_type: "run",
            ich_template: ich.suite_select_item,
            refetch_on_trigger: false
        });

        // manage-env.js
        MT.createEnvProfile('#profile-add-form');
        MT.addEnvToProfile('#editprofile, #editproductversionenvs', '#add-environment-form, #productversion-environments-form');
        MT.editEnvProfileName('#editprofile');
        MT.bulkSelectEnvs('#envnarrowing');

        // manage.js
        MT.disableOnChecked({
            container: '#run-add-form, #run-edit-form',
            trigger_field: '#id_is_series',
            target_field: '#id_build'
        });

        // runtests.js

        MT.hideEmptyRuntestsEnv();
        MT.autoFocus('.details.stepfail > .summary', '#runtests');
        MT.autoFocus('.details.testinvalid > .summary', '#runtests');
        MT.breadcrumb('.drilldown');
        MT.expandAllTests('#runtests');
        MT.runTests('#runtests');
        MT.failedTestBug('#runtests');
        MT.expandTestDetails('#runtests');
        MT.filterEnvironments('#runtests-environment-form');
        MT.startRefreshTimer('#runtests');

        // owa.js
        MT.owa();

    });

    $(window).load(function () {
        // listpages.js
        MT.openListItemDetails('.listpage');

        // filtering.js
        MT.removeInitialFilterParams('#filter');
    });

    return MT;

}(MT || {}, jQuery));
