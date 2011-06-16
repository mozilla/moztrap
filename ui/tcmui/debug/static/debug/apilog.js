(function($) {
     var getMore = function() {
         var last = parseInt($("input[name=count]").last().val()) + 1,
         qs = window.location.search ? window.location.search + "&" : "?",
         url = window.location.pathname + qs + "start=" + last;
         $.get(url, function(data) {
                   $("body").append(data);
               });
     };

     $(window).scroll(
         function() {
             if ($(window).scrollTop() == $(document).height() - $(window).height()) {
                 getMore();
             }
         });

 })(jQuery);
