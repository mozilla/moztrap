(function($) {
    $("body").ajaxError(function(event, request, settings, error) {
        $('.loadingCSS').detach();
        $('.loading').removeClass("loading");
        var data = $.parseJSON(request.responseText);
        if(error === "UNAUTHORIZED" || error === "FORBIDDEN") {
            window.location = data.login_url + "?next=" + window.location.pathname;
        } else {
            // @@@ do something nicer than an alert()?
            alert("Halp! Something broke, and we're not sure just what. Try reloading the page.");
        }
    });
 })(jQuery);