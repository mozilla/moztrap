var TCM = TCM || {};

(function($) {

    TCM.filterEnvironments = function(template, forms) {
        var allopts = $(template).find("select.environments option").clone(),

            doFilter = function(form) {
                var typeid = $(form).find("select.env_type").val(),
                    envselect = $(form).find("select.environments").empty();
                allopts.each(function() {
                    if ($(this).val().split(":")[0] == typeid) {
                        var newopt = $(this).clone();
                        newopt.appendTo(envselect);
                    }
                });
            };

        doFilter($(template));

        $(forms).find("select.env_type").live(
            "change",
            function() {
                doFilter($(this).closest(forms));
            }
        );
    };

})(jQuery);

$(function() {
    TCM.filterEnvironments("#empty-env-form > li", "ul.envlist > li");
});