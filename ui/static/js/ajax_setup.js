(function($) {
    $("body").ajaxError(
        function(event, request, settings, error) {
            var data;
            $('body').loadingOverlay('remove');
            if(error === "UNAUTHORIZED" || error === "FORBIDDEN") {
                data = $.parseJSON(request.responseText);
                window.location = data.login_url + "?next=" + window.location.pathname;
            } // @@@ any global default error handling needed?
        });

    $.ajaxSetup(
        {
            dataType: "json",
            dataFilter: function(data, type) {
                if (type == "json") {
                    var messagelist = $("#messages"),
                    parsed = $.parseJSON(data),
                    messages = $(parsed.messages);
                    messages.each(function() {
                        $(ich.message(this)).appendTo(messagelist);
                    });
                    $('#messages').messages();
                }
                return data;
            }
        }
    );
})(jQuery);
