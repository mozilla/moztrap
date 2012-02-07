/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
*/
/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    $(function () {
        // plugins
        $('.details:not(html)').html5accordion();
        $('#messages').messages({
            handleAjax: true,
            closeLink: '.message'
        });
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#suite-form .caseselect').multiselect();
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
        $('#editprofile .add-item').customAutocomplete({
            textbox: '#env-elements-input',
            inputList: '.env-element-list',
            ajax: true,
            url: $('#env-elements-input').data('autocomplete-url'),
            hideFormActions: true,
            expiredList: '.env-element-list',
            inputType: 'element',
            caseSensitive: true,
            prefix: 'element'
        });
        $('#suite-form .caseselect .multiunselected .selectsearch').customAutocomplete({
            textbox: '#search-add',
            inputList: '.groups .filter-group:not(.keyword)',
            newInputList: '.groups .filter-group.keyword',
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
                    CC.filterEnvironments('#runtests-environment-form');
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
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'cases'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]',
                'input[name="testrunincludedtestcase"]'
            ]
        });

        // local.js
        CC.inputHadFocus();

        // manage-results.js
        CC.toggleAdvancedFiltering('#filter');
        CC.loadListItemDetails();
        CC.manageActionsAjax();
        CC.directFilterLinks();
        CC.filterFormAjax('.manage, .results');

        // manage-products.js
        CC.formOptionsFilter({
            container: '#addsuite',
            trigger_sel: '#id_product',
            target_sel: '.multiunselected .select',
            option_sel: '.selectitem',
            multiselect_widget_bool: true
        });
        CC.formOptionsFilter({
            container: '#addrun',
            trigger_sel: '#id_test_cycle',
            target_sel: '#id_suites'
        });
        CC.formOptionsFilter({
            container: '#single-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_productversion'
        });
        CC.formOptionsFilter({
            container: '#single-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_initial_suite',
            optional: true
        });
        CC.formOptionsFilter({
            container: '#bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_productversion'
        });
        CC.formOptionsFilter({
            container: '#bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_initial_suite',
            optional: true
        });
        CC.filterProductTags('#single-case-add, #bulk-case-add');
        CC.testcaseAttachments('.attach');
        CC.testcaseVersioning('#addcase');
        CC.envNarrowing('#envnarrowlist');

        // manage-env.js
        CC.createEnvProfile();
        CC.editEnvProfile();

        // manage-tags.js
        CC.manageTags('#managetags');

        // runtests.js
        CC.hideEmptyRuntestsEnv();
        CC.autoFocus('.details.stepfail > .summary', '#run');
        CC.autoFocus('.details.testinvalid > .summary', '#run');
        CC.runTests('#runtests');
        CC.breadcrumb('.drilldown');
        CC.failedTestBug('#runtests');
        CC.filterEnvironments('#runtests-environment-form');
    });

    $(window).load(function () {
        // manage-results.js
        CC.openListItemDetails();
    });

    return CC;

}(CC || {}, jQuery));
