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

    var filtering = function() {
        var button = $('#filter .visual .content button[type="submit"]').hide(),
            input = $('#filter .visual .filter-group input[type="checkbox"]').each(function() {
                $(this).data('originallyChecked', $(this).is(':checked'));
            }),
            textbox = $('#filter .textual #text-filter'),
            typedText = textbox.val(),
            suggestionList = $('#filter .textual ul.suggest').hide(),
            keywordGroups = $('#filter .visual .filter-group.keyword'),
            updateButton = function() {
                if ($('#filter .visual .filter-group input[type="checkbox"]').filter(function() {
                    return $(this).data('state') === 'changed';
                }).length) {
                    button.fadeIn('fast');
                } else {
                    button.fadeOut('fast');
                }
            };

        input.live('change', function() {
            if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                $(this).data('state', 'changed');
            } else {
                $(this).data('state', null);
            }
            updateButton();
        });

        textbox.keyup(function() {
            if ($(this).val() !== typedText) {
                if ($(this).val().length) {
                    typedText = $(this).val();
                    var relevantFilters = $('#filter .visual .filter-group:not(.keyword) input[type="checkbox"]').not(':checked').parent('li').filter(function() {
                            return $(this).children('label').html().toLowerCase().substring(0, typedText.length) === typedText.toLowerCase();
                        });
                    suggestionList.empty();
                    relevantFilters.each(function() {
                        var remainingText = $(this).children('label').html().substring(typedText.length),
                            type = $(this).children('input').attr('name'),
                            id = $(this).children('input').attr('id'),
                            newHTML = '<li><a href="#" data-id="' + id + '"><b>' + typedText + '</b>'+ remainingText + ' <i>[' + type + ']</i></a></li>';
                        suggestionList.append(newHTML);
                    });
                    keywordGroups.each(function() {
                        var type = $(this).children('h5').html(),
                            name = $(this).data('name'),
                            keywordHTML = '<li><a href="#" data-class="keyword" data-name="' + name + '"><b>' + typedText + '</b> <i>[' + type + ']</i></a></li>';
                        if (!$('#filter .visual .filter-group input[type="checkbox"][value="' + typedText.replace(/\*/g,'%') + '"][name="' + name + '"]').length) {
                            suggestionList.append(keywordHTML);
                        }
                    });
                } else {
                    typedText = $(this).val();
                    suggestionList.empty();
                }
            }
        });

        textbox.focus(function() {
            suggestionList.show();
            textbox.data('clicked', false);
        });

        textbox.blur(function() {
            function hideList() {
                if (textbox.data('clicked') !== true) {
                    suggestionList.hide();
                }
            }
            window.setTimeout(hideList, 150);
        });

        suggestionList.find('a').live('mousedown', function() {
            textbox.data('clicked', true);
        });

        suggestionList.find('a').live('click', function() {
            if ($(this).data('class') === 'keyword') {
                var name = $(this).data('name'),
                    thisGroup = keywordGroups.filter(function() {
                        return $(this).data('name') === name;
                    }).removeClass('empty'),
                    typedText = textbox.val(),
                    index = thisGroup.find('li').length + 1;
                    newHTML =
                        '<li>' +
                            '<input type="checkbox" name="' + name + '" value="' + typedText.replace(/\*/g,'%') + '" id="id-' + name + '-' + index + '" checked="checked" data-state="changed" data-originallyChecked="false">' +
                            '<label for="id-' + name + '-' + index + '">' + typedText + '</label>' +
                        '</li>';
                thisGroup.children('ul').append(newHTML);
                updateButton();
                textbox.data('clicked', false).val(null);
                suggestionList.empty().hide();
                return false;
            } else {
                var thisFilter = $('#filter .visual .filter-group input#' + $(this).data('id')).attr('checked', 'checked');
                if (thisFilter.data('originallyChecked') !== thisFilter.is(':checked')) {
                    thisFilter.data('state', 'changed');
                }
                updateButton();
                textbox.data('clicked', false).val(null);
                typedText = textbox.val();
                suggestionList.empty().hide();
                return false;
            }
        });
    };

    $(function() {
        filtering();
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