/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, module, test, equal */

(function ($) {

    'use strict';

    module('jquery.ellipsis.js', {
        setup: function () {
            $('#qunit-fixture').append('<div class="ellipsis" style="width: 1em">this should have an ellipsis</div>');
        }
    });

    if (document.documentElement.style.textOverflow === undefined && document.documentElement.style.OTextOverflow === undefined) {

        test('basic functionality in non-Webkit browsers', 1, function () {
            $('#qunit-fixture .ellipsis').ellipsis();
            equal($('#qunit-fixture .ellipsis').html().substr(-3), '...', 'should add ellipsis');
        });

        test('use originalText when called twice in non-Webkit browsers', 2, function () {
            $('#qunit-fixture .ellipsis').ellipsis();
            equal($('#qunit-fixture .ellipsis').html(), 't...', 'should add ellipsis');
            $('#qunit-fixture .ellipsis').width('2em').ellipsis();
            equal($('#qunit-fixture .ellipsis').html(), 'thi...', 'should reset to original text before adding ellipsis');
        });

    } else {
        test('basic functionality in Webkit/Opera', 1, function () {
            $('#qunit-fixture .ellipsis').ellipsis();
            if (document.documentElement.style.textOverflow !== undefined) {
                equal($('#qunit-fixture .ellipsis').css('text-overflow'), 'ellipsis', 'should set "text-overflow: ellipsis" in Webkit browsers');
            }
            if (document.documentElement.style.OTextOverflow !== undefined) {
                equal($('#qunit-fixture .ellipsis').css('-o-text-overflow'), 'ellipsis', 'should set "-o-text-overflow: ellipsis" in Opera');
            }
        });
    }

}(jQuery));