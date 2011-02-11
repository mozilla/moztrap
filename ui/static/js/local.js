function testCaseButtons() {
    $("article.test button").live(
        "click",
        function(event) {
            event.preventDefault();
            // @@@ this does not work on a live event
            // event.stopPropagation();
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

function autoFocus(trigger) {
    var button = $(trigger);
    
    button.click(function() {
        if ($(this).parent().hasClass('open')) {
            $(this).parent().find('textarea').focus();
        }
    });
}

$(document).ready(function() {
    autoFocus('details.stepfail > summary');
    autoFocus('details.testinvalid > summary');
});