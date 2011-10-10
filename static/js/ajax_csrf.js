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
/*global    jQuery */

(function ($) {

    'use strict';

    // from http://docs.djangoproject.com/en/1.3/ref/contrib/csrf/#ajax
    $('html').ajaxSend(
        function (event, xhr, settings) {
            var getCookie = function (name) {
                var cookieValue = null,
                    cookies,
                    cookie,
                    i;
                if (document.cookie && document.cookie !== '') {
                    cookies = document.cookie.split(';');
                    for (i = 0; i < cookies.length; i = i + 1) {
                        cookie = $.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            };
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    );

}(jQuery));
