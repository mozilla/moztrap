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

function autoFocusScroll(trigger) {
    var button = $(trigger);
    
    button.click(function() {
        if ($(this).parent().hasClass('open')) {
            $(this).parent().find('textarea').focus();
            $.scrollTo($(this).siblings('.failform'), 750);
        }
    });
}

$(document).ready(function() {
    autoFocusScroll('details.stepfail > summary');
});