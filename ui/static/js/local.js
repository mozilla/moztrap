var TCM = TCM || {};

(function($) {

    // Filtering, autocomplete, and fake placeholder text for manage and results pages

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
    },

    filtering = function() {
        var formActions = $('#filter .form-actions').hide(),
        toggle = $('#filter .toggle a'),
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
        updateFormActions = function() {
            if (input.filter(function() { return $(this).data('state') === 'changed'; }).length) {
                formActions.fadeIn('fast');
                $('.managelist').addClass('expired');
            } else {
                formActions.fadeOut('fast');
                $('.managelist').removeClass('expired');
            }
        };

        toggle.click(function() {
            $('#filter .visual').toggleClass('compact').toggleClass('expanded');
            return false;
        });

        formActions.find('.reset').click(function() {
            formActions.fadeOut('fast');
            $('.managelist').removeClass('expired');
            input.each(function() {
                $(this).data('state', null);
                $(this).attr('checked', $(this).data('originallyChecked'));
            });
            return false;
        });

        input.live('change', function() {
            if ($(this).data('originallyChecked') !== $(this).is(':checked')) {
                $(this).data('state', 'changed');
            } else {
                $(this).data('state', null);
            }
            updateFormActions();
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
                    if (textbox.val() === '' && $('.managelist').hasClass('expired')) {
                        formActions.find('button[type="submit"]').click();
                    } else {
                        suggestionList.find('.selected').click();
                        suggestionList.show();
                    }
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
                updateFormActions();
                textbox.data('clicked', false).val(null);
                typedText = null;
                suggestionList.empty().hide();
                return false;
            }
        });
    },

    listDetails = function() {
        $('#listcontent .items .item.details').live(
            'click',
            function(event) {
                if ($(event.target).is("button, a")) {
                    return;
                }
                var item = $(this),
                content = item.find('.content'),
                url = item.data('details-url');
                if (url && !content.hasClass('loaded')) {
                    content.css('min-height', '4.854em').addClass('loaded');
                    content.loadingOverlay();
                    $.get(url,
                          function(data) {
                              content.loadingOverlay('remove');
                              content.html(data.html);
                          });
                }
            });
    },

    manageActionsAjax = function() {
        $('.manage button[name^=action-]').live(
            'click',
            function() {
                var button = $(this),
                form = button.closest('form'),
                token = form.find('input[name=csrfmiddlewaretoken]'),
                url = form.attr('action'),
                method = form.attr('method'),
                replace = button.closest('.action-ajax-replace'),
                success = function(data) {
                    var replacement = $(data.html);
                    replace.replaceWith(replacement);
                    replacement.find('.details').html5accordion('.summary');
                    replace.loadingOverlay('remove');
                },
                data = {};
                data[button.attr('name')] = button.val();
                data['csrfmiddlewaretoken'] = token.val();
                replace.loadingOverlay();
                $.ajax(url, {
                           type: method,
                           data: data,
                           success: success
                       });
                return false;
            }
        );
    };

    $(function() {
        filtering();
        listDetails();
        manageActionsAjax();
        $('#messages').messages({handleAjax: true});
        $('.details:not(html)').html5accordion('.summary');
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input:not([type=radio], [type=checkbox]), textarea').blur(function() {
            $(this).addClass('hadfocus');
        });
        formOptionsFilter("#addsuite", "product-id", "#id_product", "#id_cases");
        formOptionsFilter("#addrun", "product-id", "#id_test_cycle", "#id_suites");
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
            callback: function() {
                $('.selectruns + .environment').slideUp('fast');
            },
            lastChildCallback: function(choice) {
                var environments = $('.selectruns + .environment').css('min-height', '169px').slideDown('fast'),
                    ajaxUrl = $(choice).data("sub-url");
                environments.loadingOverlay();
                $.get(ajaxUrl, function(data) {
                    environments.loadingOverlay('remove');
                    environments.html(data.html);
                });
            }
        });
        $('.selectruns + .environment.empty').hide();
        // $('.subnav .findertoggle').click(function() {
        //     $(this).add('.subnav .finder').toggleClass('expanded').toggleClass('compact');
        //     return false;
        // });
        // $('.subnav').html5finder( {
        //     loading: true,
        //     ellipsis: true,
        //     horizontalScroll: true,
        //     scrollContainer: '.finder.expanded',
        //     headerSelector: '.listordering',
        //     sectionSelector: '.col',
        //     sectionContentSelector: '.colcontent',
        //     sectionClasses: [
        //         'products',
        //         'cycles',
        //         'runs',
        //         'cases',
        //         'results'
        //     ],
        //     sectionItemSelectors: [
        //         'input[name="product"]',
        //         'input[name="testcycle"]',
        //         'input[name="testrun"]',
        //         'input[name="testcase"]',
        //         'input[name="testresult"]'
        //     ]
        // });
    });

    $(window).load(function() {
        $('#listcontent .items').find('.title, .product, .cycle, .run').ellipsis(true, 300);
        if ($('.manage').length && window.location.hash) {
            var hash = window.location.hash;
            $(hash).children('.summary').click();
        }
    });

})(jQuery);
