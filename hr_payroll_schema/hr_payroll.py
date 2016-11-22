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

from openerp import models, fields, api, _, tools
import openerp.tools
from datetime import datetime, timedelta
import time
import re

from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    drop_view_if_exists,
)

import logging
_logger = logging.getLogger(__name__)

class hr_attendance(models.Model):
    #_inherit = ['hr.attendance', 'mail.thread']
    _inherit = 'hr.attendance'

    @api.model
    def _check_last_sign_out(self,this_attendance):
        attendance = self.env['hr.attendance'].search([('employee_id','=',this_attendance.employee_id.id),('action','=','sign_out'),('name','>',this_attendance.name[:10] + ' 00:00:00'),('name','<',this_attendance.name[:10] + ' 23:59:59')],order='name')
        return len(attendance)>0 and this_attendance.name == attendance[-1].name

    @api.one
    def _working_hours_on_day(self): # working hours on the contract
        contract = self.employee_id.contract_ids[0] if self.employee_id and self.employee_id.contract_ids else False
        if contract and self._check_last_sign_out(self):
            self.working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(self.env.cr, self.env.uid,
                contract.working_hours, fields.Datetime.from_string(self.name))
        else:
            self.working_hours_on_day = 0.0
    working_hours_on_day = fields.Float(compute='_working_hours_on_day', string='Planned Hours')

    @api.one
    def _get_working_hours(self): # worked hours in schedule
        contract = self.employee_id.contract_ids[0] if self.employee_id and self.employee_id.contract_ids else False
        if contract and self._check_last_sign_out(self):
            att = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.name[:10] + ' 00:00:00'),('name','<',self.name[:10] + ' 23:59:59')],order='name')
            for (start,end) in zip(att,att[1:])[::2]:
                self.get_working_hours += self.pool.get('resource.calendar').get_working_hours(self.env.cr, self.env.uid,
                self.employee_id.contract_id.working_hours.id,
                    datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
        else:
            self.get_working_hours = 0.0
    get_working_hours = fields.Float(compute='_get_working_hours', string='Worked in schedule (h)')
    
    @api.one
    def _timesheet_amount(self):
        if self.employee_id and self.employee_id.user_id and self._check_last_sign_out(self):
            (self.timesheet_amount,self.timesheet_amount_invoiceable) = self.env['hr.analytic.timesheet'].get_day_amount(self.name[:10],self.employee_id)
    timesheet_amount = fields.Float(compute="_timesheet_amount",string="Reported time")
    timesheet_amount_invoiceable = fields.Float(compute="_timesheet_amount",string="Reported time (invoiceable)")

class hr_analytic_timesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'
    
    @api.model
    def get_day_amount(self,date,employee):
        time = self.env['hr.analytic.timesheet'].search([('user_id','=',employee.user_id.id),('date','=',date)])
        amount = sum([t.unit_amount for t in time])
        amount_invoiceable = sum([t.unit_amount * t.to_invoice.factor for t in time])
        return (amount,amount_invoiceable)

    @api.one
    def _timesheet_amount(self):
        pass
        #~ if self.employee_id and self._check_last_sign_out(self):
            #~ (self.timesheet_amount,self.timesheet_amount_invoiceable) = self.env['hr.analytic.timesheet'].get_day_amount(self.name[:10],self.employee_id)
    timesheet_amount = fields.Float(compute="_timesheet_amount",string="Reported time")
    timesheet_amount_invoiceable = fields.Float(compute="_timesheet_amount",string="Reported time (invoiceable)")

    
class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
    
    @api.one
    @api.depends('attendances_ids','attendances_ids.sheet_id')
    def _total_attendance_schema(self):
        self.total_attendance_schema = sum(self.attendances_ids.mapped('get_working_hours'))
        self.total_difference_schema = self.total_attendance_schema - sum(self.attendances_ids.mapped('working_hours_on_day')) 
    total_attendance_schema = fields.Float(compute='_total_attendance_schema',string="Attendance (Schema)",store=True)
    total_difference_schema = fields.Float(compute='_total_attendance_schema',string="Difference (Schema)",store=True)

    @api.one
    @api.depends('timesheet_ids','timesheet_ids.timesheet_amount','timesheet_ids.timesheet_amount_invoiceable')
    def _timesheet_amount(self):
        self.timesheet_amount = sum(self.timesheet_ids.mapped("timesheet_amount"))
        self.timesheet_amount_invoiceable = sum(self.timesheet_ids.mapped("timesheet_amount_invoiceable"))
    timesheet_amount = fields.Float(compute="_timesheet_amount",string="Reported time")
    timesheet_amount_invoiceable = fields.Float(compute="_timesheet_amount",string="Reported time (invoiceable)")
    


class hr_payslip_worked_days(models.Model):
    
    _inherit = 'hr.payslip.worked_days'
    
    schema_number_of_days = fields.Float(string="Schema numer of days")
    

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def _get_nbr_of_days(self):
        slip = self[0]
        nbr = 0.0
        for day in range(0, (fields.Date.from_string(slip.date_to) - fields.Date.from_string(slip.date_from)).days + 1):
            #~ working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(self.env.cr, self.env.uid, slip.employee_id.contract_id.working_hours.id, fields.Date.from_string(slip.date_from) + timedelta(days=day), self.env.context)
            working_hours_on_day = slip.employee_id.contract_id.working_hours.get_working_hours_of_date(start_dt=fields.Datetime.from_string(slip.date_from) + timedelta(days=day))[0]
            _logger.warn('working_h_on day %s' %working_hours_on_day )
            if working_hours_on_day:
                nbr += 1.0
        return nbr

    @api.one
    def _schema_number_of_days(self):
        nbr = 0.0
        for day in range(0, (fields.Date.from_string(self.date_to) - fields.Date.from_string(self.date_from)).days + 1):
            #~ working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(self.env.cr, self.env.uid, slip.employee_id.contract_id.working_hours.id, fields.Date.from_string(slip.date_from) + timedelta(days=day), self.env.context)
            working_hours_on_day = self.employee_id.contract_id.working_hours.get_working_hours_of_date(start_dt=fields.Datetime.from_string(self.date_from) + timedelta(days=day))[0]
            _logger.warn('working_h_on day %s' %working_hours_on_day )
            if working_hours_on_day:
                nbr += 1.0
        self.schema_number_of_days = nbr
    schema_number_of_days = fields.Float(string="Schema numer of days", compute='_schema_number_of_days')
    @api.one
    def _percent_number_of_days(self):
        work100 = self.worked_days_line_ids.filtered(lambda l: l.code == 'WORK100').mapped('number_of_days')
        if work100 and work100 < self.schema_number_of_days:
            self.percent_number_of_days = self.worked_days_line_ids.filtered(lambda l: l.code == 'WORK100').mapped('number_of_days') / self.schema_number_of_days
        self.percent_number_of_days = 1.0
    percent_number_of_days = fields.Float(string="Percent numer of days", compute='_percent_number_of_days')
    
    @api.multi
    def get_schema_number_of_days(self):
        return 32.0

    @api.model
    def get_worked_day_lines(self,contract_ids, date_from, date_to):
        res = super(hr_payslip, self).get_worked_day_lines(contract_ids,date_from,date_to)
        for r in res:
            if r['code'] == 'WORK100':
                r['schema_number_of_days'] = 32.0
        #~ raise Warning(res)
        return res
        
        #~ """
        #~ @param contract_ids: list of contract id
        #~ @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        #~ """
        #~ def was_on_leave(employee_id, datetime_day, context=None):
            #~ res = False
            #~ day = datetime_day.strftime("%Y-%m-%d")
            #~ holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            #~ if holiday_ids:
                #~ res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            #~ return res

        #~ res = []
        #~ for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            #~ if not contract.working_hours:
                #~ #fill only if the contract as a working schedule linked
                #~ continue
            #~ attendances = {
                 #~ 'name': _("Normal Working Days paid at 100%"),
                 #~ 'sequence': 1,
                 #~ 'code': 'WORK100',
                 #~ 'number_of_days': 0.0,
                 #~ 'number_of_hours': 0.0,
                 #~ 'contract_id': contract.id,
            #~ }
            #~ leaves = {}
            #~ day_from = datetime.strptime(date_from,"%Y-%m-%d")
            #~ day_to = datetime.strptime(date_to,"%Y-%m-%d")
            #~ nb_of_days = (day_to - day_from).days + 1
            #~ for day in range(0, nb_of_days):
                #~ working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                #~ if working_hours_on_day:
                    #~ #the employee had to work
                    #~ leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    #~ if leave_type:
                        #~ #if he was on leave, fill the leaves dict
                        #~ if leave_type in leaves:
                            #~ leaves[leave_type]['number_of_days'] += 1.0
                            #~ leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        #~ else:
                            #~ leaves[leave_type] = {
                                #~ 'name': leave_type,
                                #~ 'sequence': 5,
                                #~ 'code': leave_type,
                                #~ 'number_of_days': 1.0,
                                #~ 'number_of_hours': working_hours_on_day,
                                #~ 'contract_id': contract.id,
                            #~ }
                    #~ else:
                        #~ #add the input vals to tmp (increment if existing)
                        #~ attendances['number_of_days'] += 1.0
                        #~ attendances['number_of_hours'] += working_hours_on_day
            #~ leaves = [value for key,value in leaves.items()]
            #~ res += [attendances] + leaves
        #~ return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: