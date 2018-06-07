# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _, http, tools
from odoo.http import request
from datetime import datetime, timedelta
import pytz
import time

import logging
_logger = logging.getLogger(__name__)

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def auto_log_out(self): #auto log out in midnight
        employees = self.env['hr.employee'].search([('active', '=', True), ('id', '!=', self.env.ref('hr.employee').id)]).filtered(lambda e: e.state == 'present')
        if len(employees) > 0:
            _logger.warn('Employees to logout %s' %employees)
        for e in employees:
            if e.contract_id and e.user_id:
                atts = self.search([('employee_id', '=', e.id)], order='name')
                if len(atts) != 0:
                    if atts[-1].action == 'sign_in': #last attendance is sign in
                        hours_to = {a.dayofweek: a.hour_to for a in e.contract_id.working_hours.attendance_ids}
                        now = datetime.now()
                        yesterday_utc = datetime(now.year, now.month, now.day) - timedelta(days = 1) + timedelta(minutes = (hours_to[str(now.weekday())]* 60))
                        yesterday = self.convert2utc(e, yesterday_utc).strftime('%Y-%m-%d %H:%M:%S')
                        try:
                            e.with_context({'action_date': yesterday, 'action': 'sign_out'}).attendance_action_change()
                        except Exception as ex:
                            _logger.warn(': '.join(ex))
                            self.env['mail.message'].create({
                                'body': _("Error!\n%s\nSystem tried to signed out on %s (%s)\n Current status: %s" % (ex, yesterday_utc, yesterday, e.state)),
                                'subject': _("Error Auto sign out"),
                                'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                                'res_id': e.id,
                                'model': e._name,
                                'subtype_id': self.env.ref('mail.mt_comment').id,
                                'partner_ids': [(6, 0, [e.user_id.partner_id.id])],
                                'type': 'notification',})
                            if e.parent_id:
                                self.env['mail.message'].create({
                                    'body': _("Error!\n%s\n%sSystem tried to automatically signed out on %s\n" % (ex, e.name, yesterday_utc)),
                                    'subject': _("Error Employee auto sign out"),
                                    'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                                    'res_id': e.parent_id.id,
                                    'model': e._name,
                                    'subtype_id': self.env.ref('mail.mt_comment').id,
                                    'partner_ids': [(6, 0, [e.parent_id.user_id.partner_id.id])],
                                    'type': 'notification',})
                            continue
                        self.env['mail.message'].create({
                            'body': _("You've been automatically signed out on %s (%s)\nIf this sign out time is incorrect, please contact your supervisor. Current status: %s" % (yesterday_utc, yesterday, e.state)),
                            'subject': _("Auto sign out"),
                            'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                            'res_id': e.id,
                            'model': e._name,
                            'subtype_id': self.env.ref('mail.mt_comment').id,
                            'partner_ids': [(6, 0, [e.user_id.partner_id.id])],
                            'type': 'notification',})
                        if e.parent_id:
                            self.env['mail.message'].create({
                                'body': _("%s has been automatically signed out on %s\n" % (e.name, yesterday_utc)),
                                'subject': _("Employee auto sign out"),
                                'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                                'res_id': e.parent_id.id,
                                'model': e._name,
                                'subtype_id': self.env.ref('mail.mt_comment').id,
                                'partner_ids': [(6, 0, [e.parent_id.user_id.partner_id.id])],
                                'type': 'notification',})
                    else:
                        continue
        return None

    @api.model
    def absent_notification(self): #send notification to employee and manager when employee is absent without leave request
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        employees = self.env['hr.employee'].search([('active', '=', True), ('state', '=', 'absent'), ('id', '!=', self.env.ref('hr.employee').id)])
        employees_on_vacation = request.env['hr.holidays'].search([('date_from', '<', now), ('date_to', '>=', now), ('state', '=', 'validate'), ('type', '=', 'remove')]).mapped('employee_id')
        employees -= employees_on_vacation
        for e in employees:
            if e.user_id:
                self.env['mail.message'].create({
                    'body': _("Time to work!"),
                    'subject': _("Time to work!"),
                    'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                    'res_id': e.id,
                    'model': e._name,
                    'subtype_id': self.env.ref('mail.mt_comment').id,
                    'partner_ids': [(6, 0, [e.user_id.partner_id.id])],
                    'type': 'notification',})
            if e.parent_id and e.parent_id.user_id:
                self.env['mail.message'].create({
                    'body': _("Your employee %s is not at work" %e.name),
                    'subject': _("Your employee %s is not at work" %e.name),
                    'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                    'res_id': e.parent_id.id,
                    'model': e._name,
                    'subtype_id': self.env.ref('mail.mt_comment').id,
                    'partner_ids': [(6, 0, [e.parent_id.user_id.partner_id.id])],
                    'type': 'notification',})

    @api.model
    def sick_notification(self): #send notification to employee and manager when employee is absent after 7 sick days
        today = datetime.now()
        employees_sick = request.env['hr.holidays'].search([('date_from', '<', today.strftime('%Y-%m-%d')), ('date_to', '>=', today.strftime('%Y-%m-%d')), ('state', '=', 'validate'), ('type', '=', 'remove'), ]).mapped('employee_id')
        for e in employees_sick:
            eightday_sick = request.env['hr.holidays'].search([('date_from', '>', (today - timedelta(days=8)).strftime('%Y-%m-%d 00:00:00')), ('date_from', '<', (today - timedelta(days=8)).strftime('%Y-%m-%d 23:59:59')), ('state', '=', 'validate'), ('type', '=', 'remove'), ('holiday_status_id', 'in', [self.env.ref('l10n_se_hr_payroll.sick_leave_qualify').id, self.env.ref('l10n_se_hr_payroll.sick_leave_214').id]), ('employee_id', '=', e.id)])
            nineday_sick = request.env['hr.holidays'].search([('date_from', '<', (today - timedelta(days=8)).strftime('%Y-%m-%d 00:00:00')), ('date_to', '>', (today - timedelta(days=8)).strftime('%Y-%m-%d 00:00:00')), ('state', '=', 'validate'), ('type', '=', 'remove'), ('holiday_status_id', 'in', [self.env.ref('l10n_se_hr_payroll.sick_leave_qualify').id, self.env.ref('l10n_se_hr_payroll.sick_leave_214').id]), ('employee_id', '=', e.id)])
            if len(eightday_sick) > 0 and len(nineday_sick) == 0: #send notification when it's only 8th sick day
                #~ if e.user_id:
                    #~ self.env['mail.message'].create({
                        #~ 'body': _("You have been sick for more than 7 days"),
                        #~ 'subject': _("You have been sick for more than 7 days"),
                        #~ 'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                        #~ 'res_id': e.id,
                        #~ 'model': e._name,
                        #~ 'subtype_id': self.env.ref('mail.mt_comment').id,
                        #~ 'partner_ids': [(6, 0, [e.user_id.partner_id.id])],
                        #~ 'type': 'notification',})
                if e.parent_id and e.parent_id.user_id:
                    self.env['mail.message'].create({
                        'body': _("Your employee %s has been sick for more than 7 days" %e.name),
                        'subject': _("Your employee %s has been sick for more than 7 days" %e.name),
                        'author_id': self.env.ref('hr.employee').user_id.partner_id.id,
                        'res_id': e.parent_id.id,
                        'model': e._name,
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                        'partner_ids': [(6, 0, [e.parent_id.user_id.partner_id.id])],
                        'type': 'notification',})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
