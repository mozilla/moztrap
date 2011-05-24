var TCM = TCM || {};

(function($) {

    TCM.addLoading = function(trigger, context) {
        $(context).find(trigger).click(function() {
            var $container = $(this).closest(context),
                addLoadingCSS = function() {
                    var vertHeight = (parseInt($container.css('height'), 10) - parseInt($container.css('line-height'), 10)) / 2 + 'px',
                        style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
                    $('head').append(style);
                };
            $container.addClass('loading');
            addLoadingCSS();
        });
    };

    var advancedFilter = function() {
        var button = $('#filter .visual .content button[type="submit"]').hide(),
            input = $('#filter .visual .content .filter-group input[type="checkbox"]').each(function() {
                $(this).data('originallyChecked', $(this).is(':checked'));
            }),
            updateButton = function() {
                if ($('#filter .visual .content .filter-group input[type="checkbox"].changed').length) {
                    button.fadeIn();
                } else {
                    button.fadeOut();
                }
            };
        input.change(function() {
            if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                $(this).addClass('changed');
            } else {
                $(this).removeClass('changed');
            }
            updateButton();
        });
    };

    $(function() {
        advancedFilter();
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input, textarea').blur(
            function() {
                $(this).addClass('hadfocus');
            }
        );
        $('#filter .toggle a').click(
            function() {
                $('#filter .visual').toggleClass('compact').toggleClass('expanded');
                return false;
            }
        );
        if ($('html').hasClass('no-details')) {
            $('details').html5accordion('summary');
        }
        $('.details:not(html)').html5accordion('.summary');
        $('#sandbox .findertoggle').click(function() {
            $(this).add('#sandbox .finder').toggleClass('expanded').toggleClass('compact');
            return false;
        });
        $('#sandbox').html5finder( {
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder.expanded',
            headerSelector: 'header.listordering',
            sectionSelector: 'section.col',
            sectionContentSelector: 'ul.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'cases',
                'results'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="cycle"]',
                'input[name="run"]',
                'input[name="case"]',
                'input[name="result"]'
            ]
        });
        $('.subnav .findertoggle').click(function() {
            $(this).add('.subnav .finder').toggleClass('expanded').toggleClass('compact');
            return false;
        });
        $('.subnav').html5finder( {
            loading: true,
            horizontalScroll: true,
            scrollContainer: '.finder.expanded',
            headerSelector: 'header.listordering',
            sectionSelector: 'section.col',
            sectionContentSelector: 'ul.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'cases',
                'results'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="cycle"]',
                'input[name="run"]',
                'input[name="case"]',
                'input[name="result"]'
            ]
        });
        $('#selectruns').html5finder( {
            loading: true,
            headerSelector: 'header.listordering',
            sectionSelector: 'section.col',
            sectionContentSelector: 'ul.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="cycle"]',
                'input[name="run"]'
            ],
            callback: function() {
                $('#selectruns + #environment').slideUp();
            },
            lastChildCallback: function() {
                $('#selectruns + #environment').slideDown();
            }
        });
        $('#selectruns + #environment').hide();
    });

})(jQuery);