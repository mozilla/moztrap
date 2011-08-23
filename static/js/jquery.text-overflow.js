/**
 * jQuery Text-overflow
 *
 * http://devongovett.wordpress.com/2009/04/06/text-overflow-ellipsis-for-firefox-via-jquery/
 *
 */

(function($) {
	$.fn.ellipsis = function(opts){
        var options = $.extend({}, $.fn.ellipsis.defaults, opts),
		s = document.documentElement.style;
		if (!('textOverflow' in s || 'OTextOverflow' in s)) {
			return this.each(function(){
				var el = $(this);
				if(el.css("overflow") == "hidden"){
					var originalText = el.html();
					if (!el.data('originalText')){
                        el.data('originalText', originalText);
					}
					var w = el.width();

					var t = $(this.cloneNode(true)).hide().css({
                        'position': 'absolute',
                        'width': 'auto',
                        'overflow': 'visible',
                        'max-width': 'inherit'
                    });
					el.after(t);

					var text = originalText;
					while(text.length > 0 && t.width() > el.width()){
						text = text.substr(0, text.length - 1);
						t.html(text + "...");
					}
					el.html(t.html());

					t.remove();

                    // use of `delay` requires jQuery doTimeout
                    // http://benalman.com/projects/jquery-dotimeout-plugin/
                    if(options.windowResize === true){
                        var oldW = el.width();
                        $(window).resize(function(){
                            if (options.delay){
                                $.doTimeout(options.delay, function(){
                                    if(el.width() !== oldW){
                                        oldW = el.width();
                                        el.html(originalText);
                                        el.ellipsis();
                                    }
                                });
                            } else {
                                if(el.width() !== oldW){
                                    oldW = el.width();
                                    el.html(originalText);
                                    el.ellipsis();
                                }
                            }
                        });
                    }
				}
			});
		} else return this;
	};

	/* Setup plugin defaults */
    $.fn.ellipsis.defaults = {
        windowResize: false,        // If `true`, the function will run again on `$(window).resize`
        delay: null,                // Delay (in ms) to debounce $(window).resize event (if windowResize: true)
                                    // Requires jQuery doTimeout:
                                    // http://benalman.com/projects/jquery-dotimeout-plugin/
    };
})(jQuery);