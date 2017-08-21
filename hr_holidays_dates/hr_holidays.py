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

from openerp import models, fields, api, _
from datetime import timedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare


import logging
_logger = logging.getLogger(__name__)


class hr_holidays(models.Model):
    _inherit = "hr.holidays"
    
    number_of_days_temp_show = fields.Float('Allocation', compute = '_get_number_of_days_temp_show')
    number_of_hours = fields.Float('Hours', compute = '_get_converted_time', inverse = '_set_converted_time', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
    number_of_minutes = fields.Float('Minutes', compute='_get_converted_time', inverse = '_set_converted_time', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
    time_unit = fields.Selection(related = 'holiday_status_id.time_unit', readonly = True)
    
    @api.one
    def _get_converted_time(self):
        self.number_of_hours = self.number_of_days_temp * (self.employee_id.get_working_hours_per_day() or 8)
        self.number_of_minutes = self.number_of_hours * 60
    
    @api.one
    @api.onchange('number_of_hours', 'number_of_minutes')
    def _set_converted_time(self):
        if self.holiday_status_id.time_unit == 'hour':
            number_of_days_temp = self.number_of_hours / (self.employee_id.get_working_hours_per_day() or 8)   # Assume 8 hours if 0
            if self.number_of_days_temp != number_of_days_temp:
                self.number_of_days_temp  = number_of_days_temp
        elif self.holiday_status_id.time_unit == 'minute':
            number_of_days_temp = (self.number_of_minutes / (self.employee_id.get_working_hours_per_day() or 8)) / 60
            if self.number_of_days_temp != number_of_days_temp:
                self.number_of_days_temp  = number_of_days_temp
    
    @api.one
    def _get_number_of_days_temp_show(self):
        self.number_of_days_temp_show = self.number_of_days_temp
    
    @api.one
    @api.onchange('number_of_days_temp')
    def onchange_number_of_days_temp(self):
        self._get_number_of_days_temp_show()
        self._get_converted_time()
    
    def _get_default_date_from(self, employee, date_from):
        if employee and employee.sudo().contract_id and employee.sudo().contract_id.working_hours and date_from:
            date = fields.Datetime.from_string(date_from)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            intervals = employee.sudo().contract_id.working_hours.get_working_intervals_of_day(date)[0]
            return  intervals and fields.Datetime.to_string(intervals[0][0]) or date_from
    
    def _get_default_date_to(self, employee, date_to):
        if employee and employee.sudo().contract_id and employee.sudo().contract_id.working_hours and date_to:
            date = fields.Datetime.from_string(date_to)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            intervals = employee.sudo().contract_id.working_hours.get_working_intervals_of_day(date)[0]
            return  intervals and fields.Datetime.to_string(intervals[-1][-1]) or date_to
    
    @api.one
    def _update_number_of_days_temp(self):
        if self.employee_id and self.employee_id.sudo().contract_id and self.employee_id.sudo().contract_id.working_hours and self.date_from and self.date_to and self.number_of_days_temp <= 1.0:
            hours = self.employee_id.sudo().contract_id.working_hours.get_working_hours_of_date(fields.Datetime.from_string(self.date_from), fields.Datetime.from_string(self.date_to))[0]
            #hours_on_day = self.employee_id.sudo().contract_id.working_hours.get_working_hours_of_date(fields.Datetime.from_string(self.date_from).replace(hour = 0, minute = 0))[0]
            self.number_of_days_temp = hours / (self.employee_id.get_working_hours_per_day() or 8) #Assume 8 if 0
        self.onchange_number_of_days_temp()
    
    @api.one
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        res = self.onchange_employee(self.employee_id.id)['value']
        for v in res:
            setattr(self, v, res[v])
        if self.sudo().employee_id.contract_id and self.sudo().employee_id.contract_id.working_hours:
            self.date_from = self._get_default_date_from(self.employee_id, self.date_from)
            self.date_to = None
            self._onchange_date_from()
    
    @api.one
    @api.onchange('date_from')
    def _onchange_date_from(self):
        res = self.onchange_date_from(self.date_to, self.date_from)['value']
        date_to = self.date_to
        for v in res:
            setattr(self, v, res[v])
        if not date_to:
            self.date_to = self._get_default_date_to(self.employee_id, self.date_from)
        self._update_number_of_days_temp()
    
    @api.one
    @api.onchange('date_to')
    def _onchange_date_to(self):
        res = self.onchange_date_to(self.date_to, self.date_from)['value']
        date_from = self.date_from
        for v in res:
            setattr(self, v, res[v])
        if not date_from:
            self.date_from = self._get_default_date_from(self.employee_id, self.date_to)
        self._update_number_of_days_temp()
    
    @api.model
    def create(self,values):
        if values.get('holiday_type') == 'category' or values.get('type') == 'add' or values.get('employee_id') == None:
            pass
        else:
            leave = self.env['hr.holidays.status'].browse(values['holiday_status_id'])
            if not leave.limit:
                leave_days = leave.get_days(values.get('employee_id'))[leave.id]
                if float_compare(leave_days['remaining_leaves'], values.get('number_of_days_temp'), precision_digits=2) == -1 or \
                   float_compare(leave_days['virtual_remaining_leaves'], values.get('number_of_days_temp'), precision_digits=2) == -1:
                    # Raising a warning gives a more user-friendly feedback than the default constraint error
                    raise Warning(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                'Please verify also the leaves waiting for validation.'))
        return super(hr_holidays, self).create(values)

class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"
    
    time_unit = fields.Selection([('day', 'Days'), ('hour', 'Hours'), ('minute', 'Minutes')], 'Time Unit', default='day')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
