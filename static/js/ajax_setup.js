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
            indent:     4 */
/*global    jQuery */

(function ($) {

    'use strict';

    $("body").ajaxError(
        function (event, request, settings, error) {
            var data;
            $('body').loadingOverlay('remove');
            if (error === "UNAUTHORIZED" || error === "FORBIDDEN") {
                data = $.parseJSON(request.responseText);
                window.location = data.login_url + "?next=" + window.location.pathname;
            } // @@@ any global default error handling needed?
        }
    );

}(jQuery));
