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
import pytz
import time

import logging
_logger = logging.getLogger(__name__)

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    # project_work_time calculate time betweet two attendances

    def convert2utc(self, employee, lo_dt): #convert user's local timezone to UTC
        lo_tzone = self.env.ref('base.user_root').tz
        if employee.user_id.tz:
            lo_tzone = employee.user_id.tz
        return pytz.timezone(lo_tzone).localize(lo_dt).astimezone(pytz.utc)

class attendanceReport(http.Controller):

    @http.route(['/hr/attendance'], type='http', auth="user", website=True)
    def attendance(self, employees=None, **post):
        return request.website.render("hr_attendance_terminal.hr_attendance_form", {'employees': request.env['hr.employee'].search([('active', '=', True), ('id', '!=', request.env.ref('hr.employee').id)]),})

    @http.route(['/hr/attendance/employee'], type='json', auth="user", website=True)
    def attendance_report(self, rfid=None, **kw):
        e = request.env['hr.employee'].search([('rfid', '=', rfid)])
        if len(e) > 0:
            return e[0].id
        else:
            return ''

    @http.route(['/hr/attendance/state'], type='json', auth="user", website=True)
    def attendance_state(self, employee=None, **kw):
        if employee:
            e = request.env['hr.employee'].search([('id', '=', int(employee))])[0]
            return {'id': e.id, 'state': e.state}
        else:
            return {'state': None}

    @http.route(['/hr/attendance/employee_project'], type='json', auth="user", website=True)
    def employee_project(self, employee=None, **kw):
        e = request.env['hr.employee'].browse(int(employee))
        if e.user_id and e.state == 'absent':
            projects = request.env['project.project'].search([('members', '=', e.user_id.id)]).mapped(lambda p : {'id': p.id, 'name': p.name})
            if len(projects) > 0:
                return {'projects': projects}
            else:
                return {}
        else:
            return {}

    @http.route(['/hr/attendance/come_and_go'], type='json', auth="user", website=True)
    def attendance_comeandgo(self, employee_id=None, project_id=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee_id))
        try:
            employee.attendance_action_change()
            attendances = request.env['hr.attendance'].search([('employee_id', '=', employee.id), ('action', '!=', 'action')], limit=2, order='name desc')
            last_attendance = sec_last_attendance = None
            if len(attendances) == 2:
                last_attendance = attendances[0]
                sec_last_attendance = attendances[1]
                if last_attendance.action == sec_last_attendance.action:
                    raise Warning(_('You cannot %s twice' %last_attendance.action))
            else:
                last_attendance = attendances[0]
            if last_attendance.action == 'sign_in' and project_id:
                last_attendance.project_id = int(project_id)
            elif last_attendance.action == 'sign_out' and sec_last_attendance.action == 'sign_in' and sec_last_attendance.project_id:
                timesheet = request.env['hr.analytic.timesheet'].create({
                    'date': last_attendance.name[:10],
                    'account_id': sec_last_attendance.project_id.analytic_account_id.id,
                    'name': '/',
                    'unit_amount': (fields.Datetime.from_string(last_attendance.name) - fields.Datetime.from_string(sec_last_attendance.name)).total_seconds() / 3600.0,
                    'user_id': employee.user_id.id,
                    'product_id': request.env['hr.analytic.timesheet'].with_context(user_id = employee.user_id.id, employee_id = employee.id)._getEmployeeProduct(),
                    'product_uom_id': request.env['hr.analytic.timesheet'].with_context(user_id = employee.user_id.id, employee_id = employee.id)._getEmployeeUnit(),
                    'general_account_id': request.env['hr.analytic.timesheet'].with_context(user_id = employee.user_id.id, employee_id = employee.id)._getGeneralAccount(),
                    'journal_id': request.env['hr.analytic.timesheet'].with_context(user_id = employee.user_id.id, employee_id = employee.id)._getAnalyticJournal(),
                })
        except Exception as e:
            return ': '.join(e)
        return None

    @http.route(['/hr/attendance/<model("hr.attendance"):attendance>'], type='json', auth="user", website=True)
    def get_attendance(self, attendance=None, **kw):
        return {'attendance': {
                    'name': attendance.name,
                    'action': attendance.action,
                    'work_time': attendance.sudo().employee_id.contract_id.type_id.work_time,
                    'worked_hours': attendance.sudo().flex_working_hours if attendance.sudo().employee_id.contract_id.type_id.work_time == 'flex' else attendance.get_working_hours,
                    'flextime_month': attendance.flextime_month,
                    'flextime': attendance.sudo().flextime,
                    'compensary_leave': attendance.compensary_leave,
                },
                'employee': {
                    'img': attendance.employee_id.image_medium,
                    'name': attendance.employee_id.name,
                    'state': attendance.employee_id.state,
                }
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
