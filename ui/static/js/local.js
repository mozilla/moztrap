(function($) {

    var preventAccordion = function(button, loading) {
        $(button).click(
            function(event) {
                // prevent it from triggering the html5accordion
                event.stopPropagation();
                if (loading) {
                    $(this).closest(loading).addClass('loading');
                }
            }
        );
    };

    $(function() {
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
        $('details').html5accordion('summary');
        $('.details').html5accordion('.summary');
        preventAccordion('summary button', 'details');
        preventAccordion('.summary button', '.details');
        preventAccordion('summary a');
        preventAccordion('.summary a');
    });

})(jQuery);