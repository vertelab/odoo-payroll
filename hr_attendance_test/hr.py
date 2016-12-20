# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _

import random

import logging
_logger = logging.getLogger(__name__)



from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from datetime import timedelta

import openerp.addons.decimal_precision as dp


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def test_attendance(self,startdate,nbr_days):



        #~ raise Warning(self.contract_id.working_hours.attendance_ids.mapped('dayofweek','hour_from'))
        self.env['hr.attendance'].search([('employee_id','=',self.id)]).unlink()
        self.env['hr.holidays'].search([('employee_id','=',self.id)]).write({'state':'draft'})
        self.env['hr.holidays'].search([('employee_id','=',self.id)]).unlink()

        self.env['hr.payslip'].search([('employee_id','=',self.id)]).write({'state': 'draft'})
        self.env['hr.payslip'].search([('employee_id','=',self.id)]).unlink()

        hours_from = {a[0]: a[1] for a in reversed(self.contract_id.working_hours.attendance_ids.sorted(key=lambda a: a.hour_from).mapped(lambda a: (a.dayofweek,a.hour_from)))}
        #~ hours_from={a.dayofweek: a.hour_from for a in self.contract_id.working_hours.attendance_ids.sorted(key=lambda r: r.dayofweek,r.hour_from)}
        hours_to={a.dayofweek: a.hour_to for a in self.contract_id.working_hours.attendance_ids}
        _logger.warn(' from %s to %s ' % (hours_from,hours_to))

        year = startdate.year

        self.env['hr.holidays'].create({
                'employee_id': self.id,
                'date_from': datetime.datetime(year,7,1).strftime('%Y-%m-%d'),
                'date_to': datetime.datetime(year,7,24).strftime('%Y-%m-%d'),
                'state': 'validate',
                'type': 'remove',
                'holiday_status_id': self.env.ref('l10n_se_hr_holidays.holiday_status_cl1').id,
                    'number_of_days': 25.0,
            })
        for i in range(3):
            date = datetime.datetime(year,2,random.randint(1,28))
            self.env['hr.holidays'].create({
                    'employee_id': self.id,
                    'date_from': date.strftime('%Y-%m-%d'),
                    'date_to': (date + timedelta(hours=20)).strftime('%Y-%m-%d %H:%M'),
                    'state': 'validate',
                    'type': 'remove',
                    'holiday_status_id': self.env.ref('l10n_se_hr_holidays.sick_leave_qualify').id,
                    'number_of_days': 1.0,
                })

        date = startdate
        for day in range(nbr_days):
            date += timedelta(days=1)
            _logger.error('date %s start %s end %s' % (date,hours_from.get(str(date.weekday()),None),hours_to.get(str(date.weekday()),None)))
            if hours_from.get(str(date.weekday()),None) and not self.env['hr.holidays'].search([('date_from','>=',(date + timedelta(minutes=hours_from[str(date.weekday())])).strftime('%Y-%m-%d %H:%M:%S')),('date_to','<=',(date + timedelta(minutes=hours_from[str(date.weekday())])).strftime('%Y-%m-%d %H:%M:%S'))]):
                _logger.error(date + timedelta(minutes=hours_from[str(date.weekday())] * 60 + random.randint(-60,60)))
                self.with_context({'action_date': (date + timedelta(minutes=(hours_from[str(date.weekday())] * 60 + random.randint(-60,60)))).strftime('%Y-%m-%d %H:%M:%S')}).attendance_action_change()
                self.with_context({'action_date': (date + timedelta(minutes=(hours_to[str(date.weekday())] * 60 + random.randint(-60,60)))).strftime('%Y-%m-%d %H:%M:%S')}).attendance_action_change()


    @api.one
    def test_attendance_calendar_year(self):
        year = datetime.datetime.now().year
        date = datetime.datetime(year, 1, 1)
        self.test_attendance(date,365)

    @api.one
    def test_attendance2today(self):
        year = datetime.datetime.now().year
        date = datetime.datetime(year, 1, 1)
        self.test_attendance(date,(datetime.datetime.now()-date).days)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
