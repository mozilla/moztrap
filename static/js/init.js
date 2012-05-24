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
            prefix: 'filter'
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
            prefix: 'filter'
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
            prefix: 'tag'
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
            prefix: 'filter'
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

        // filtering.js
        MT.toggleAdvancedFiltering('.magicfilter');
        MT.preventCaching('#filter');
        MT.directFilterLinks();
        MT.filterFormAjax('.manage, .results, .run');
        MT.clientSideFilter({container: '#envnarrowing'});

        // manage-products.js
        MT.formOptionsFilter({
            container: '#suite-add-form, #suite-edit-form',
            trigger_sel: '#id_product',
            target_sel: '.multiunselected .select',
            option_sel: '.selectitem',
            multiselect_widget_bool: true
        });
        MT.formOptionsFilter({
            container: '#run-add-form, #run-edit-form',
            trigger_sel: '#id_productversion',
            target_sel: '.multiunselected .select',
            option_sel: '.selectitem',
            multiselect_widget_bool: true
        });
        MT.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_productversion'
        });
        MT.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_initial_suite',
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

        // manage-env.js
        MT.createEnvProfile('#profile-add-form');
        MT.addEnvToProfile('#editprofile, #editproductversionenvs', '#add-environment-form, #productversion-environments-form');
        MT.editEnvProfileName('#editprofile');
        MT.bulkSelectEnvs('#envnarrowing');

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
