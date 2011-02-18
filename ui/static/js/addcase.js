function filterEnvironments(forms) {
    var allopts = $(forms).eq(0).find("select.environments option").clone();

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
    $(forms).each(
        function() {
            doFilter(this);
        });
    $(forms).find("select.env_type").live(
        "change",
        function() {
            // @@@ this selector should be passed in somehow
            doFilter($(this).closest("li.env-form"));
        });

}

$(document).ready(
    function() {
        filterEnvironments("ul.envlist > li");
    });
