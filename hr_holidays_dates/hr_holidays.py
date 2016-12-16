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

import logging
_logger = logging.getLogger(__name__)


class hr_holidays(models.Model):
    _inherit = "hr.holidays"
    
    number_of_days_temp_show = fields.Float('Allocation', compute = '_get_number_of_days_temp_show')
    number_of_hours = fields.Float('Hours', compute = '_get_number_of_hours')
    
    @api.one
    def _get_number_of_days_temp_show(self):
        self.number_of_days_temp_show = self.number_of_days_temp
    
    @api.one
    @api.onchange('number_of_days_temp')
    def onchange_number_of_days_temp(self):
        self._get_number_of_days_temp_show()
        self._get_number_of_hours()
    
    @api.one
    def _get_number_of_hours(self):
        if self.employee_id and self.employee_id.contract_id and self.employee_id.contract_id.working_hours and self.number_of_days_temp <= 1:
            self.number_of_hours = self.number_of_days_temp * self.employee_id.contract_id.working_hours.get_working_hours_of_date(
                fields.Datetime.from_string(self.date_from),
                fields.Datetime.from_string(self.date_to))[0]
    
    def _get_default_date_from(self, employee, date_from):
        date = fields.Datetime.from_string(date_from)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        intervals = employee.contract_id.working_hours.get_working_intervals_of_day(date)[0]
        return  intervals and fields.Datetime.to_string(intervals[0][0]) or date_from
    
    def _get_default_date_to(self, employee, date_to):
        date = fields.Datetime.from_string(date_to)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        intervals = employee.contract_id.working_hours.get_working_intervals_of_day(date)[0]
        return  intervals and fields.Datetime.to_string(intervals[-1][-1]) or date_to
    
    def _get_number_of_days_temp(self, employee, date_from, date_to):
        if employee and employee.contract_id and employee.contract_id.working_hours:
            hours = employee.contract_id.working_hours.get_working_hours_of_date(fields.Datetime.from_string(date_from), fields.Datetime.from_string(date_to))[0]
            hours_on_day = employee.contract_id.working_hours.get_working_hours_of_date(fields.Datetime.from_string(date_from).replace(hour = 0, minute = 0))[0]
            if hours_on_day != 0:
                return hours / hours_on_day
        return 1
    
    @api.cr_uid_ids
    def onchange_employee(self, cr, uid, ids, employee_id, date_to = None, date_from = None):
        env = api.Environment(cr, uid, {})
        result = super(hr_holidays, self).onchange_employee(cr, uid, ids, employee_id)
        employee = env['hr.employee'].browse(employee_id)
        if employee.contract_id and employee.contract_id.working_hours:
            if date_from:
                result['value']['date_from'] = self._get_default_date_from(employee, date_from)
            if date_to:
                result['value']['date_to'] = self._get_default_date_to(employee, date_to)
        return result
         
    @api.cr_uid_ids
    def onchange_date_from(self, cr, uid, ids, date_to, date_from, employee_id = []):
        result = super(hr_holidays, self).onchange_date_from(cr, uid, ids, date_to, date_from)
        env = api.Environment(cr, uid, {})
        employee = env['hr.employee'].browse(employee_id)
        if employee:
            if date_from and not date_to:
                date_to = result['value']['date_to'] = self._get_default_date_to(employee, date_from)
            if date_from and date_to and result['value'].get('number_of_days_temp', 2) <= 1.0:
                result['value']['number_of_days_temp'] = self._get_number_of_days_temp(employee, date_from, date_to)
        return result
        
    @api.cr_uid_ids
    def onchange_date_to(self, cr, uid, ids, date_to, date_from, employee_id = []):
        result = super(hr_holidays, self).onchange_date_to(cr, uid, ids, date_to, date_from)
        _logger.warn(result)
        env = api.Environment(cr, uid, {})
        employee = env['hr.employee'].browse(employee_id)
        if employee:
            if date_to and not date_from:
                date_from = result['value']['date_from'] = self._get_default_date_from(employee, date_to)
            if date_from and date_to and result['value'].get('number_of_days_temp', 2) <= 1.0:
                result['value']['number_of_days_temp'] = self._get_number_of_days_temp(employee, date_from, date_to)
        return result
        
        
    #~ def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        #~ """
        #~ If there are no date set for date_to, automatically set one 8 hours later than
        #~ the date_from.
        #~ Also update the number_of_days.
        #~ """
        #~ # date_to has to be greater than date_from
        #~ if (date_from and date_to) and (date_from > date_to):
            #~ raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        #~ result = {'value': {}}

        #~ # No date_to set so far: automatically compute one 8 hours later
        #~ if date_from and not date_to:
            #~ date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            #~ result['value']['date_to'] = str(date_to_with_delta)

        #~ # Compute and update the number of days
        #~ if (date_to and date_from) and (date_from <= date_to):
            #~ diff_day = self._get_number_of_days(date_from, date_to)
            #~ result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        #~ else:
            #~ result['value']['number_of_days_temp'] = 0

        #~ return result

    #~ def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        #~ """
        #~ Update the number_of_days.
        #~ """

        #~ # date_to has to be greater than date_from
        #~ if (date_from and date_to) and (date_from > date_to):
            #~ raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        #~ result = {'value': {}}

        #~ # Compute and update the number of days
        #~ if (date_to and date_from) and (date_from <= date_to):
            #~ diff_day = self._get_number_of_days(date_from, date_to)
            #~ result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        #~ else:
            #~ result['value']['number_of_days_temp'] = 0

        #~ return result


    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
