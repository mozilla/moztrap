function filterEnvironments(template, forms) {
    var allopts = $(template).find("select.environments option").clone();

    function doFilter(form) {
        var typeid = $(form).find("select.env_type").val();
        var envselect = $(form).find("select.environments");
        envselect.empty();
        allopts.each(
            function() {
                if ($(this).val().split(":")[0] == typeid) {
                    var newopt = $(this).clone();
                    newopt.appendTo(envselect);
                }
        });
    }

    doFilter($(template));

    $(forms).each(
        function() {
            doFilter(this);
        });

    $(forms).find("select.env_type").live(
        "change",
        function() {
            doFilter($(this).closest(forms));
        });
}

$(document).ready(
    function() {
        filterEnvironments("#empty-env-form > li", "ul.envlist > li");
    });
