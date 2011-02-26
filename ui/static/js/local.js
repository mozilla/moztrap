$(
    function() {
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('input, textarea').blur(function() {
            $(this).addClass('hadfocus');
        });
    });
