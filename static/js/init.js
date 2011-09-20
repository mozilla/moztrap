/*jslint    browser:    true,
            indent:     4 */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    $(function () {
        // add class "hadfocus" to inputs and textareas on blur
        $('input:not([type=radio], [type=checkbox]), textarea').live('blur', function () {
            $(this).addClass('hadfocus');
        });

        // hide empty run-tests environments form on initial load
        $('.selectruns + .environment.empty').hide();

        // plugins
        $('#addcase').slideshow({
            slidesSelector: '.forms form[id$="-case-form"]',
            slideLinksSelector: 'a[href^="#"][href$="-case-form"]'
        });
        $('.details:not(html)').html5accordion();
        $('#messages').messages({
            handleAjax: true,
            closeLink: '.message'
        });
        $('input[placeholder], textarea[placeholder]').placeholder();
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

        // manage-results.js
        CC.autoCompleteFiltering();
        CC.loadListItemDetails();
        CC.manageActionsAjax();
        CC.formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        CC.formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");

        // manage-env.js
        CC.createEnvProfile();
        CC.editEnvProfile();

        // runtests.js
        CC.autoFocus('.details.stepfail > .summary');
        CC.autoFocus('.details.testinvalid > .summary');
        CC.testCaseButtons("#run .item");
        CC.breadcrumb('.selectruns');
    });

    $(window).load(function () {
        // manage-results.js
        CC.addEllipses();

        // Expand list item details on direct hashtag links
        if ($('.manage').length && window.location.hash && $(window.location.hash).length) {
            $(window.location.hash).children('.summary').click();
        }
    });

    return CC;

}(CC || {}, jQuery));