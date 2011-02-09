function testCaseButtons() {
    $("article.test button").live(
        "click",
        function(event) {
            event.preventDefault();
            var button = $(this);
            var testcase = button.closest("article.test");
            $.post(
                testcase.attr("data-action-url"),
                {
                    action: button.attr("data-action")
                },
                function(data) {
                    testcase.find(".status").replaceWith(data);
                });
        });
}

$(function() {
      testCaseButtons();
      $("div[role=main]").ajaxError(
          function(event, request, settings) {
              $(this).prepend(
                  '<aside class="error">' + request.responseText + '</aside>'
              );
          });
  });
