/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011 uTest Inc.

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
*/
/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, module, test, equal, start, stop, expect, ok */

(function (CC, $) {

    'use strict';

    module('jquery.ellipsis.js', {
        setup: function () {
            $('#qunit-fixture #ellipsis').ellipsis();
        }
    });

    if (document.documentElement.style.textOverflow === undefined && document.documentElement.style.OTextOverflow === undefined) {

        test('basic functionality in non-Webkit browsers', 1, function () {
            equal($('#qunit-fixture #ellipsis').html().substr(-3), '...', 'ellipsis added');
        });

        test('use originalText when called twice in non-Webkit browsers', 2, function () {
            equal($('#qunit-fixture #ellipsis').html(), 't...', 'ellipsis added first time');
            $('#qunit-fixture #ellipsis').width('2em').ellipsis();
            equal($('#qunit-fixture #ellipsis').html(), 'thi...', 'reset to original text before adding ellipsis second time');
        });

    } else {
        test('basic functionality in Webkit/Opera', 1, function () {
            if (document.documentElement.style.textOverflow !== undefined) {
                equal($('#qunit-fixture #ellipsis').css('text-overflow'), 'ellipsis', 'set "text-overflow: ellipsis" in Webkit browsers');
            }
            if (document.documentElement.style.OTextOverflow !== undefined) {
                equal($('#qunit-fixture #ellipsis').css('-o-text-overflow'), 'ellipsis', 'set "-o-text-overflow: ellipsis" in Opera');
            }
        });
    }

    module('doTimeout');

    test('window.resize', 2, function () {
        var resize = 0,
            dt_resize = 0;

        stop();

        $(window).resize(function () {
            resize = resize + 1;
            $.doTimeout('resize', 100, function () {
                dt_resize = dt_resize + 1;
                equal(dt_resize, 1, 'doTimeout window.resize only fired once');
                start();
            });
        });

        $(window).resize();
        $(window).resize();
        $(window).resize();
        equal(resize, 3, 'normal window.resize fired 3 times');
    });

}(CC, jQuery));