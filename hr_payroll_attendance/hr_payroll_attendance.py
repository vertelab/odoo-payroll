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

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    # project_work_time calculate time betweet two attendances

    @api.model
    def auto_log_out(self):
        employees = request.env['hr.employee'].search([('active', '=', True), ('id', '!=', request.env.ref('hr.employee').id)])
        for e in employees:
            if e.state == 'present':
                if e.contract_id:
                    hours_to = {a.dayofweek: a.hour_to for a in e.contract_id.working_hours.attendance_ids}
                    now = datetime.now()
                    yesterday = (datetime(now.year, now.month, now.day) - timedelta(days = 1) + timedelta(minutes = (hours_to[str(now.weekday())]* 60))).strftime('%Y-%m-%d %H:%M:%S')
                    e.with_context({'action_date': yesterday}).attendance_action_change()
                    self.env['mail.message'].create({
                        'body': _("You've been automatically signed out on' %s\nIf this sign out time is incorrect, please contact your supervisor." % (yesterday)),
                        'subject': _("Auto sign out"),
                        'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                        'res_id': e.id,
                        'model': e._name,
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                        'partner_ids': [(6, 0, [e.user_id.partner_id.id])],
                        'type': 'notification',})
                    if e.parent_id:
                        self.env['mail.message'].create({
                            'body': _("%s has been automatically signed out on' %s\n" % (e.name, yesterday)),
                            'subject': _("Employee auto sign out"),
                            'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                            'res_id': e.parent_id.id,
                            'model': e._name,
                            'subtype_id': self.env.ref('mail.mt_comment').id,
                            'partner_ids': [(6, 0, [e.parent_id.user_id.partner_id.id])],
                            'type': 'notification',})
        return None

class attendanceReport(http.Controller):

    @http.route(['/hr/attendance'], type='http', auth="user", website=True)
    def attendance(self, employees=None, **post):
        return request.website.render("hr_payroll_attendance.hr_attendance_form", {'employees': request.env['hr.employee'].search([('active', '=', True), ('id', '!=', request.env.ref('hr.employee').id)]),})

    @http.route(['/hr/attendance/report'], type='json', auth="user", website=True)
    def attendance_report(self, employee=None, **kw):
        state = request.env['hr.employee'].search_read([('id', '=', int(employee))], ['state'])[0]['state']
        return state

    @http.route(['/hr/attendance/employee_project'], type='json', auth="user", website=True)
    def employee_project(self, employee=None, **kw):
        employee = request.env['hr.employee'].browse(int(employee))
        if employee.user_id and employee.state == 'absent':
            projects = request.env['project.project'].search([('members', '=', employee.user_id.id)]).mapped(lambda p : {'id': p.id, 'name': p.name})
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
                    'flex_working_hours': attendance.flex_working_hours,
                    'flextime': attendance.flextime,
                },
                'employee': {
                    'img': attendance.employee_id.image_medium,
                    'name': attendance.employee_id.name,
                    'state': attendance.employee_id.state,
                }
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
