$(
    function() {
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input, textarea').blur(
            function() {
                $(this).addClass('hadfocus');
            });
        $('summary button').click(
            function(event) {
                // prevent it from triggering the summary/details
                event.stopPropagation();
                $(this).closest('summary').addClass('loading');
            });
        $('summary a').click(
            function(event) {
                // prevent it from triggering the summary/details
                event.stopPropagation();
            });
    });
