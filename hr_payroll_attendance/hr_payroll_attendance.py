# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _, http, tools
from openerp.http import request
from datetime import datetime, timedelta
import time

import logging
_logger = logging.getLogger(__name__)

class attendanceReport(http.Controller):

    @http.route(['/hr/attendance'], type='http', auth="user", website=True)
    def attendance(self, employees=None, **post):
        employees = request.env['hr.employee'].search([])

        return request.website.render("hr_payroll_attendance.hr_attendance_form", {'employees': employees,})

    @http.route(['/hr/attendance/report'], type='json', auth="user", website=True)
    def attendance_report(self, employee=None, **kw):
        state = request.env['hr.employee'].browse(int(employee)).state
        return state

    @http.route(['/hr/attendance/source'], type='http', auth="public", website=True)
    def attendance_source(self, employee=None, **post):
        while True:
            employee_login = request.env['hr.employee'].search([('state', '=', 'present')])
            while employee_login - request.env['hr.employee'].search([('state', '=', 'present')]):
                # send to client
                headers=[('Content-Type', 'text/plain; charset=utf-8')]
                r = werkzeug.wrappers.Response(request_id, headers=headers)
                break
        state = request.env['hr.employee'].browse(int(employee)).state
        return state

    #~ @http.route(['/hr/attendance/log'], type='http', auth="user", website=True)
    #~ def attendance_log(self, employee=None, **post):
        #~ employees = request.env['hr.employee'].search([])
        #~ return request.website.render("hr_payroll_attendance.hr_attendance_form", {'employee': employee,})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
