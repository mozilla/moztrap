var TCM = TCM || {};

(function($) {

    // Adds CSS to <head> for .loading
    TCM.addLoadingCSS = function(container) {
        var vertHeight = (parseInt(container.css('height'), 10) - parseInt(container.css('line-height'), 10)) / 2 + 'px',
            style = '<style type="text/css" class="loadingCSS">.loading::before { padding-top: ' + vertHeight + '; }</style>';
        $('head').append(style);
    };

    // On `trigger`, adds class `loading` to `context`, and calls TCM.addLoadingCSS()
    TCM.addLoading = function(trigger, context) {
        $(context).find(trigger).click(function() {
            var container = $(this).closest(context).addClass('loading');
            TCM.addLoadingCSS(container);
        });
    };

    // Filtering, autocomplete, and fake placeholder text for manage and results pages
    var filtering = function() {
        var button = $('#filter .visual .content button[type="submit"]').hide(),
            input = $('#filter .visual .filter-group input[type="checkbox"]').each(function() {
                $(this).data('originallyChecked', $(this).is(':checked'));
            }),
            textbox = $('#filter .textual #text-filter'),
            typedText = textbox.val(),
            placeholder = textbox.attr('placeholder'),
            suggestionList = $('#filter .textual .suggest').hide(),
            keywordGroups = $('#filter .visual .filter-group.keyword'),
            notKeywordGroups = $('#filter .visual .filter-group:not(.keyword)'),
            selected,
            removeFakePlaceholder = function() {
                if (textbox.val().indexOf(placeholder) !== -1) {
                    textbox.val(null);
                }
                textbox.removeClass('placeholder');
            },
            updateButton = function() {
                if (input.filter(function() {
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

        textbox.keyup(function(event) {
            if ($(this).val() !== typedText && $(this).val() !== placeholder) {
                typedText = $(this).val();
                suggestionList.empty();
                if ($(this).val().length) {
                    var relevantFilters = notKeywordGroups.find('input[type="checkbox"]:not(:checked)').parent('li').filter(function() {
                            return $(this).children('label').html().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                        });
                    relevantFilters.each(function() {
                        var typedIndex = $(this).children('label').html().toLowerCase().indexOf(typedText.toLowerCase()),
                            preText = $(this).children('label').html().substring(0, typedIndex),
                            postText = $(this).children('label').html().substring(typedIndex + typedText.length),
                            type = $(this).children('input').attr('name'),
                            id = $(this).children('input').attr('id'),
                            newHTML = '<li><a href="#" data-id="' + id + '">' + preText + '<b>' + typedText + '</b>' + postText + ' <i>[' + type + ']</i></a></li>';
                        suggestionList.append(newHTML);
                    });
                    keywordGroups.each(function() {
                        var type = $(this).children('h5').html(),
                            name = $(this).data('name'),
                            keywordHTML = '<li><a href="#" data-class="keyword" data-name="' + name + '"><b>' + typedText + '</b> <i>[' + type + ']</i></a></li>';
                        if ($(this).find('input[type="checkbox"]:checked').length) {
                            if ($(this).find('input[type="checkbox"][value^="^"][value$="$"]:checked').length === $(this).find('input[type="checkbox"]:checked').length) {
                                if (!($(this).find('input[type="checkbox"][value="' + typedText + '"]:checked').length) && typedText.indexOf('^') === 0 && typedText.lastIndexOf('$') === typedText.length - 1) {
                                    suggestionList.append(keywordHTML);
                                }
                            }
                        } else {
                            suggestionList.append(keywordHTML);
                        }
                    });
                    suggestionList.find('li:first-child a').addClass('selected');
                }
            }
        }).keydown(function(event) {
            if (textbox.hasClass('placeholder')) {
                if (!event.metaKey && event.keyCode !== 16 && event.keyCode !== 17 && event.keyCode !== 18 && event.keyCode !== 20 && event.keyCode !== 27) {
                    removeFakePlaceholder();
                }
            } else {
                if (event.keyCode === 38) {
                    event.preventDefault();
                    if (!suggestionList.find('.selected').parent().is(':first-child')) {
                        suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                    }
                    return false;
                }
                if (event.keyCode === 40) {
                    event.preventDefault();
                    if (!suggestionList.find('.selected').parent().is(':last-child')) {
                        suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                    }
                    return false;
                }
                if (event.keyCode === 13) {
                    event.preventDefault();
                    suggestionList.find('.selected').click();
                    suggestionList.show();
                    return false;
                }
                if (event.keyCode === 9) {
                    var thisFilterName = input.filter('#' + suggestionList.find('.selected').data('id')).siblings('label').html();
                    if (thisFilterName && textbox.val() !== thisFilterName) {
                        event.preventDefault();
                        textbox.val(thisFilterName);
                        return false;
                    } else {
                        if (suggestionList.find('.selected').length) {
                            event.preventDefault();
                            suggestionList.find('.selected').click();
                            suggestionList.show();
                            return false;
                        }
                    }
                }
                return true;
            }
        }).click(function() {
            if (textbox.hasClass('placeholder')) {
                removeFakePlaceholder();
            }
        }).focus(function() {
            suggestionList.show();
            textbox.data('clicked', false);
            if (textbox.val().length === 0 && textbox.hasClass('placeholder')) {
                textbox.val(placeholder);
                textbox.get(0).setSelectionRange(0, 0);
            }
        }).blur(function() {
            function hideList() {
                if (textbox.data('clicked') !== true) {
                    suggestionList.hide();
                }
            }
            removeFakePlaceholder();
            window.setTimeout(hideList, 150);
        }).addClass('placeholder').focus();

        suggestionList.hover(function() {
            selected = $(this).find('.selected').removeClass('selected');
        }, function() {
            selected.addClass('selected');
        }).find('a').live({
            mousedown: function() {
                textbox.data('clicked', true);
            },
            click: function() {
                if ($(this).data('class') === 'keyword') {
                    var name = $(this).data('name'),
                        thisGroup = keywordGroups.filter(function() {
                            return $(this).data('name') === name;
                        }),
                        existingKeyword = thisGroup.find('input[type="checkbox"][value="' + typedText + '"][name="' + name + '"]'),
                        index = thisGroup.find('li').length + 1,
                        newHTML =
                            '<li>' +
                                '<input type="checkbox" name="' + name + '" value="' + typedText + '" id="id-' + name + '-' + index + '" checked="checked" data-state="changed" data-originallyChecked="false">' +
                                '<label for="id-' + name + '-' + index + '">' + typedText + '</label>' +
                            '</li>';
                    if (existingKeyword.length) {
                        existingKeyword.attr('checked', 'checked');
                        if (existingKeyword.data('originallyChecked') !== existingKeyword.is(':checked')) {
                            existingKeyword.data('state', 'changed');
                        }
                    } else {
                        thisGroup.removeClass('empty').children('ul').append(newHTML);
                        input = input.add('#id-' + name + '-' + index);
                    }
                } else {
                    var thisFilter = input.filter('#' + $(this).data('id')).attr('checked', 'checked');
                    if (thisFilter.data('originallyChecked') !== thisFilter.is(':checked')) {
                        thisFilter.data('state', 'changed');
                    }
                }
                updateButton();
                textbox.data('clicked', false).val(null);
                typedText = null;
                suggestionList.empty().hide();
                return false;
            }
        });
    };

    var formOptionsFilter = function(context_sel, data_attr, trigger_sel, target_sel) {
        var context = $(context_sel),
        trigger = context.find(trigger_sel);
        if (context.length && trigger.is("select")) {
            var target = context.find(target_sel),
            allopts = target.find("option").clone();

            var doFilter = function() {
                var key = trigger.find("option:selected").data(data_attr);
                target.empty();
                allopts.each(function() {
                    if ($(this).data(data_attr) === key) {
                        var newopt = $(this).clone();
                        newopt.appendTo(target);
                    }
                });
            };

            doFilter();

            trigger.change(doFilter);
        }
    };

    $(function() {
        filtering();
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input:not([type=radio], [type=checkbox]), textarea').blur(
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
        $('.subnav .findertoggle').click(function() {
            $(this).add('.subnav .finder').toggleClass('expanded').toggleClass('compact');
            return false;
        });
        formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");
        $('.subnav').html5finder( {
            loading: true,
            ellipsis: true,
            horizontalScroll: true,
            scrollContainer: '.finder.expanded',
            headerSelector: '.listordering',
            sectionSelector: '.col',
            sectionContentSelector: '.colcontent',
            sectionClasses: [
                'products',
                'cycles',
                'runs',
                'cases',
                'results'
            ],
            sectionItemSelectors: [
                'input[name="product"]',
                'input[name="testcycle"]',
                'input[name="testrun"]',
                'input[name="testcase"]',
                'input[name="testresult"]'
            ]
        });
        $('.selectruns').html5finder( {
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
            callback: function() {
                $('.selectruns + .environment').slideUp('fast');
            },
            lastChildCallback: function(choice) {
                var environments = $('.selectruns + .environment').css('min-height', '169px').addClass('loading').slideDown('fast'),
                    ajaxUrl = $(choice).data("sub-url");
                TCM.addLoadingCSS(environments);
                $.get(ajaxUrl, function(data) {
                    environments.html(data);
                    $('.loadingCSS').detach();
                    $('.loading').removeClass('loading');
                });
            }
        });
        $('.selectruns + .environment.empty').hide();
    });

    $(window).load(function() {
        $('#listcontent .items .title').ellipsis(true, 250);
    });

})(jQuery);
