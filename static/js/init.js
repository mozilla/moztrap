/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011 uTest Inc.

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
        $('#filter').customAutocomplete({
            textbox: '#text-filter',
            inputList: '.visual .filter-group:not(.keyword)',
            newInputList: '.visual .filter-group.keyword',
            multipleCategories: true,
            allowNew: true,
            restrictNewInputs: true,
            newInputTextbox: 'input[type="text"]',
            hideFormActions: true,
            fakePlaceholder: true,
            expiredList: '.managelist',
            initialFocus: true,
            inputsNeverRemoved: true
        });
        $('#addcase').customAutocomplete({
            textbox: 'input[name="text-tag"]',
            ajax: true,
            url: $('#addcase input[name="text-tag"]').data('autocomplete-url'),
            triggerSubmit: null,
            allowNew: true,
            inputType: 'tag',
            inputList: '.visual .taglist',
            expiredList: null
        });
        $('#editprofile .add-item').customAutocomplete({
            textbox: '#env-elements-input',
            suggestionList: '.suggest',
            inputList: '.env-element-list',
            ajax: true,
            url: $('#env-elements-input').data('autocomplete-url'),
            hideFormActions: true,
            expiredList: '.env-element-list',
            inputType: 'element'
        });
        // $('#suite-form .caseselect .unselected').customAutocomplete({
        //     textbox: '#search-add',
        //     inputList: '.terms',
        //     allowNew: true,
        //     expiredList: '.select',
        //     triggerSubmit: null
        // });
        // $('#suite-form .caseselect .selected').customAutocomplete({
        //     textbox: '#search-remove',
        //     inputList: '.terms',
        //     allowNew: true,
        //     expiredList: '.select',
        //     triggerSubmit: null
        // });
        $('.selectruns').html5finder({
            loading: true,
            ellipsis: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]'
            ],
            callback: function () {
                $('.selectruns + .environment').slideUp('fast');
            },
            lastChildCallback: function (choice) {
                var environments = $('.selectruns + .environment').css('min-height', '169px').slideDown('fast'),
                    ajaxUrl = $(choice).data("sub-url");
                environments.loadingOverlay();
                $.get(ajaxUrl, function (data) {
                    environments.loadingOverlay('remove');
                    environments.html(data.html);
                });
            }
        });
        $('.managedrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            ellipsis: true,
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'suites'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]',
                'input[name="testsuite"]'
            ]
        });
        $('.resultsdrill').html5finder({
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder',
            ellipsis: true,
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
        CC.formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        CC.formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");
        CC.testcaseAttachments('#single-case-form .attachments');
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
        CC.runTests("#run");
        CC.breadcrumb('.selectruns');
        CC.failedTestBug('#run');
    });

    $(window).load(function () {
        // manage-results.js
        CC.addEllipses();
        CC.openListItemDetails();
    });

    return CC;

}(CC || {}, jQuery));