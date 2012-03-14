/*
Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

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
            indent:     4,
            confusion:  true */
/*global    ich, jQuery */

var CC = (function (CC, $) {

    'use strict';

    CC.owa = function () {
        var trigger = $('#owa a'),
            url = trigger.data('url'),
            installCallback = function (result) {
                // great - display a message, or redirect to a launch page
                var msg = 'Successfully registered!';
                ich.message({message: msg, tags: 'success'}).appendTo($('#messages ul'));
                $('#messages ul').messages();
            },
            errorCallback = function (result) {
                // whoops - result.code and result.message have details
                var msg = 'Unable to register due to ' + result.code + ': ' + result.message;
                ich.message({message: msg, tags: 'error'}).appendTo($('#messages ul'));
                $('#messages ul').messages();
            },
            register = function () {
                navigator.mozApps.install(
                    url,
                    {},
                    installCallback,
                    errorCallback
                );
            };

        trigger.click(function (e) {
            e.preventDefault();
            if (url) { register(); }
        });
    };

    return CC;

}(CC || {}, jQuery));