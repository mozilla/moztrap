/**
 * jQuery html5accordion 0.1
 *
 * Copyright (c) 2011, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 *
 * Based on code by Mathias Bynens
 * See: http://mathiasbynens.be/notes/html5-details-jquery
 */
(function($) {
    $.fn.html5accordion = function(summary) {

        return this.each(function() {
            // Store a reference to the current `details` element in a variable
            var $details = $(this),
                // Store a reference to the `summary` element of the current `details` element (if any) in a variable
                $detailsSummary = $(summary + ':first', $details),
                // Do the same for the info within the `details` element
                $detailsNotSummary = $details.children(':not(' + summary + ':first)'),
                // This will be used later to look for direct child text nodes
                $detailsNotSummaryContents = $details.contents(':not(' + summary + ':first)');

            // If there is no `summary` in the current `details` element…
            if (!$detailsSummary.length) {
                // …create one with default text
                $detailsSummary = $(document.createElement('summary')).text('Details').prependTo($details);
            }

            // Look for direct child text nodes
            if ($detailsNotSummary.length !== $detailsNotSummaryContents.length) {
                // Wrap child text nodes in a `span` element
                $detailsNotSummaryContents.filter(function() {
                    // Only keep the node in the collection if it’s a text node containing more than only whitespace
                    return (this.nodeType === 3) && (/[^\t\n\r ]/.test(this.data));
                }).wrap('<span>');
                // There are now no direct child text nodes anymore — they’re wrapped in `span` elements
                $detailsNotSummary = $details.children(':not(' + summary + ':first)');
            }

            // Hide content unless the `open` attribute is truthy
            if ($details.attr('open')) {
                $details.addClass('open');
                $detailsNotSummary.slideDown('fast');
            } else {
                $detailsNotSummary.hide();
            }

            // Set the `tabindex` attribute of the `summary` element to 0 to make it keyboard accessible
            $detailsSummary.attr('tabindex', 0).click(function() {
                // Focus on the `summary` element
                $detailsSummary.focus();
                // Toggle the `open` attribute of the `details` element
                $details.attr('open') ? $details.removeAttr('open') : $details.attr('open', 'open');
                // Toggle the additional information in the `details` element
                $detailsNotSummary.slideToggle('fast');
                $details.toggleClass('open');
            }).keyup(function(event) {
                if (13 === event.keyCode || 32 === event.keyCode) {
                    // Enter or Space is pressed — trigger the `click` event on the `summary` element
                    // Opera already seems to trigger the `click` event when Enter is pressed
                    if (!($.browser.opera && 13 === event.keyCode)) {
                        event.preventDefault();
                        $detailsSummary.click();
                    }
                }
            });

            var preventInternalButtons = function() {
                $details.find("button, a").click(
                    function(event) {
                        // prevent it from triggering the html5accordion
                        event.stopPropagation();
                    }
                );
            };
            preventInternalButtons();
        });
    };
})(jQuery);