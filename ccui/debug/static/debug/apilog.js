(function($) {
     var getMore = function() {
         var last = parseInt($("input[name=count]").last().val()),
         qs = window.location.search ? window.location.search + "&" : "?",
         url = window.location.pathname + qs + "last=" + last;
         if (last) {
             $.get(url, function(data) {
                       $("body").append(data.html);
                   });
         }
     };

     $(window).scroll(
         function() {
             if ($(window).scrollTop() == $(document).height() - $(window).height()) {
                 getMore();
             }
         });

 })(jQuery);
