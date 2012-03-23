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
            numberCols: 4
        });

        // local.js
        CC.inputHadFocus();

        // account.js
        CC.changePwdCancel();

        // listpages.js
        CC.loadListItemDetails();
        CC.manageActionsAjax('.manage, .manage-form');
        CC.listActionAjax(
            '.manage, .results, .run',
            '.listordering .sortlink, .pagination .prev, .pagination .next, .pagination .page, .perpage a'
        );
        CC.itemStatusDropdown('.manage');

        // filtering.js
        CC.toggleAdvancedFiltering('.magicfilter');
        CC.preventCaching('#filter');
        CC.directFilterLinks();
        CC.filterFormAjax('.manage, .results, .run');
        CC.clientSideFilter({container: '#envnarrowing'});

        // manage-products.js
        CC.formOptionsFilter({
            container: '#suite-add-form, #suite-edit-form',
            trigger_sel: '#id_product',
            target_sel: '.multiunselected .select',
            option_sel: '.selectitem',
            multiselect_widget_bool: true
        });
        CC.formOptionsFilter({
            container: '#run-add-form, #run-edit-form',
            trigger_sel: '#id_productversion',
            target_sel: '.multiunselected .select',
            option_sel: '.selectitem',
            multiselect_widget_bool: true
        });
        CC.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_productversion'
        });
        CC.formOptionsFilter({
            container: '#single-case-add, #bulk-case-add',
            trigger_sel: '#id_product',
            target_sel: '#id_initial_suite',
            optional: true
        });
        CC.formOptionsFilter({
            container: '#productversion-add-form',
            trigger_sel: '#id_product',
            target_sel: '#id_clone_envs_from',
            optional: true,
            callback: function (context) {
                context.find('#id_clone_envs_from option:last-child').prop('selected', true);
            }
        });
        CC.filterProductTags('#single-case-add, #bulk-case-add');
        CC.testcaseAttachments('.case-form .attach');

        // manage-env.js
        CC.createEnvProfile('#profile-add-form');
        CC.addEnvToProfile('#editprofile, #editproductversionenvs');
        CC.editEnvProfileName('#editprofile');
        CC.bulkSelectEnvs('#envnarrowing');

        // runtests.js
        CC.hideEmptyRuntestsEnv();
        CC.autoFocus('.details.stepfail > .summary', '#runtests');
        CC.autoFocus('.details.testinvalid > .summary', '#runtests');
        CC.breadcrumb('.drilldown');
        CC.expandAllTests('#runtests');
        CC.runTests('#runtests');
        CC.failedTestBug('#runtests');
        CC.expandTestDetails('#runtests');
        CC.filterEnvironments('#runtests-environment-form');
    });

    $(window).load(function () {
        // listpages.js
        CC.openListItemDetails('.listpage');

        // filtering.js
        CC.removeInitialFilterParams('#filter');
    });

    return CC;

}(CC || {}, jQuery));
