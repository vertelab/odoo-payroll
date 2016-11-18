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
        _logger.warn(attendance)
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
                self.employee_id.contract_ids[0].working_hours.id,
                    datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
        else:
            self.get_working_hours = False
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

class hr_timesheet_sheet_sheet_day(models.Model):
    _inherit = "hr_timesheet_sheet.sheet.day"
        
    @api.one
    #~ @api.depends('account.analytic.line.date','account.analytic.line.amount','hr.attendance.action','hr.attendance.name','hr.attendance.sheet_id')
    def _total_attendance_schema(self):
        if self.sheet_id.employee_id.contract_id:
            att = self.env['hr.attendance'].search([('employee_id','=',self.sheet_id.employee_id.id),('name','>',self.date + ' 00:00:00'),('name','<',self.date + ' 23:59:59')],order='name')
            for (start,end) in zip(att,att[1:])[::2]:
                self.total_attendance_schema += self.pool.get('resource.calendar').get_working_hours(self.env.cr, self.env.uid,
                    self.sheet_id.employee_id.contract_id.working_hours.id,
                    datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
            self.total_difference_schema = self.total_attendance_schema - self.total_timesheet
        else:
            self.total_attendance_schema = 0.0
            self.total_difference_schema = 0.0
        
    total_attendance_schema = fields.Float(compute='_total_attendance_schema',string="Attendance (Schema)",store=True)
    total_difference_schema = fields.Float(compute='_total_attendance_schema',string="Difference (Schema)",store=True)
   
    
    #~ def init(self, cr):
        #~ drop_view_if_exists(cr, 'hr_timesheet_sheet_sheet_day')
        #~ cr.execute("""create or replace view hr_timesheet_sheet_sheet_day as
            #~ SELECT
                #~ id,
                #~ name,
                #~ sheet_id,
                #~ total_timesheet,
                #~ total_attendance,
                #~ total_attendance_schema,
                #~ total_difference_schema,
                #~ cast(round(cast(total_attendance - total_timesheet as Numeric),2) as Double Precision) AS total_difference
            #~ FROM
                #~ ((
                    #~ SELECT
                        #~ MAX(id) as id,
                        #~ name,
                        #~ sheet_id,
                        #~ timezone,
                        #~ SUM(total_timesheet) as total_timesheet,
                        #~ CASE WHEN SUM(orphan_attendances) != 0
                            #~ THEN (SUM(total_attendance) +
                                #~ CASE WHEN current_date <> name
                                    #~ THEN 1440
                                    #~ ELSE (EXTRACT(hour FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC')) * 60) + EXTRACT(minute FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC'))
                                #~ END
                                #~ )
                            #~ ELSE SUM(total_attendance)
                        #~ END /60  as total_attendance,
                        #~ SUM(total_attendance_schema) as total_attendance_schema,
                        #~ SUM(total_difference_schema) as total_difference_schema
                    #~ FROM
                        #~ ((
                            #~ select
                                #~ min(hrt.id) as id,
                                #~ p.tz as timezone,
                                #~ l.date::date as name,
                                #~ s.id as sheet_id,
                                #~ sum(l.unit_amount) as total_timesheet,
                                #~ 0 as orphan_attendances,
                                #~ 0.0 as total_attendance
                            #~ from
                                #~ hr_analytic_timesheet hrt
                                #~ JOIN account_analytic_line l ON l.id = hrt.line_id
                                #~ LEFT JOIN hr_timesheet_sheet_sheet s ON s.id = hrt.sheet_id
                                #~ JOIN hr_employee e ON s.employee_id = e.id
                                #~ JOIN resource_resource r ON e.resource_id = r.id
                                #~ LEFT JOIN res_users u ON r.user_id = u.id
                                #~ LEFT JOIN res_partner p ON u.partner_id = p.id
                            #~ group by l.date::date, s.id, timezone
                        #~ ) union (
                            #~ select
                                #~ -min(a.id) as id,
                                #~ p.tz as timezone,
                                #~ (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date as name,
                                #~ s.id as sheet_id,
                                #~ 0.0 as total_timesheet,
                                #~ SUM(CASE WHEN a.action = 'sign_in' THEN -1 ELSE 1 END) as orphan_attendances,
                                #~ SUM(((EXTRACT(hour FROM (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))) * 60) + EXTRACT(minute FROM (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC')))) * (CASE WHEN a.action = 'sign_in' THEN -1 ELSE 1 END)) as total_attendance
                            #~ from
                                #~ hr_attendance a
                                #~ LEFT JOIN hr_timesheet_sheet_sheet s
                                #~ ON s.id = a.sheet_id
                                #~ JOIN hr_employee e
                                #~ ON a.employee_id = e.id
                                #~ JOIN resource_resource r
                                #~ ON e.resource_id = r.id
                                #~ LEFT JOIN res_users u
                                #~ ON r.user_id = u.id
                                #~ LEFT JOIN res_partner p
                                #~ ON u.partner_id = p.id
                            #~ WHERE action in ('sign_in', 'sign_out')
                            #~ group by (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date, s.id, timezone
                        #~ )) AS foo
                        #~ GROUP BY name, sheet_id, timezone
                #~ )) AS bar""")   
    
class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
    
    @api.one
    @api.depends('attendances_ids','attendances_ids.sheet_id','period_ids')
    def _total_attendance_schema(self):
        pass
        #~ self.total_attendance_schema = sum([d.total_attendance_schema for d in self.period_ids])
        #~ self.total_attendance_schema = sum(self.period_ids.mapped('total_attendance_schema'))
        #~ self.total_attendance_schema = sum(self.period_ids.mapped('total_attendance_schema'))
        #~ self.total_difference_schema = sum(self.period_ids.mapped('total_difference_schema'))
        
    total_attendance_schema = fields.Float(compute='_total_attendance_schema',string="Attendance (Schema)",store=True)
    total_difference_schema = fields.Float(compute='_total_attendance_schema',string="Difference (Schema)",store=True)
    
    @api.one
    @api.depends('timesheet_ids','timesheet_ids.unit_amount','timesheet_ids.to_invoice.factor')
    def _total_timesheet_invoiceable(self):
        self.total_timesheet_invoiceable = sum([t.unit_amount * t.to_invoice.factor for t in self.timesheet_ids])
    total_timesheet_invoiceable = fields.Float(compute='_total_timesheet_invoiceable',string="Invoiceable",store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: