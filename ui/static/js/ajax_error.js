(function($) {
    $("body").ajaxError(function(event, request, settings, error) {
        $('.loadingCSS').detach();
        $('.loading').removeClass("loading");
        var data = $.parseJSON(request.responseText);
        if(error === "UNAUTHORIZED" || error === "FORBIDDEN") {
            window.location = data.login_url + "?next=" + window.location.pathname;
        } else {
            // @@@ do something nicer than an alert()?
            alert("An unexpected error occurred. Try reloading the page.");
        }
    });
 })(jQuery);
