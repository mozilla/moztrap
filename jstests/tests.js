/*jslint    browser:    true,
            indent:     4 */
/*global    jQuery, module, test, equal, start, stop */

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

    module('slideshow');

    test('basic functionality (slide 2)', function () {
        expect(5);
        stop();
        CC.slideshow('#qunit-fixture #slideshow', '.slide', 'a[href^="#slide"]', function() {
            ok($('#slide1').is(':hidden'), 'slide 1 is hidden');
            start();
        });
        $('#slideshow a[href="#slide2"]').click();
        ok($('#slide2').is(':visible'), 'slide 2 is visible');
        ok(!$('#slideshow a[href="#slide1"]').hasClass('active'), 'slide 1 link is not active');
        ok($('#slideshow a[href="#slide2"]').hasClass('active'), 'slide 2 link is active');
        ok($('#slideshow a:focus').length === 0, 'none of the slide links have focus');
    });

    test('hashtag (slide 1)', function () {
        expect(5);
        stop();
        window.location.hash = '#slide1';
        CC.slideshow('#qunit-fixture #slideshow', '.slide', 'a[href^="#slide"]', function() {
            ok($('#slide2').is(':hidden'), 'slide 2 is hidden');
            start();
        });
        ok($('#slide1').is(':visible'), 'slide 1 is visible');
        ok($('#slideshow a[href="#slide1"]').hasClass('active'), 'slide 1 link is active');
        ok(!$('#slideshow a[href="#slide2"]').hasClass('active'), 'slide 2 link is not active');
        ok($('#slideshow a:focus').length === 0, 'none of the slide links have focus');
        window.location.hash = '';
    });

}(CC, jQuery));