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

import logging
_logger = logging.getLogger(__name__)

#~ class hr_attendance(models.Model):
    #~ _inherit = 'hr.attendance'

    #~ @api.model
    #~ def _check_last_sign_out(self,this_attendance):
        #~ attendance = self.env['hr.attendance'].search([('employee_id','=',this_attendance.employee_id.id),('action','=','sign_out'),('name','>',this_attendance.name[:10] + ' 00:00:00'),('name','<',this_attendance.name[:10] + ' 23:59:59')],order='name')
        #~ _logger.warn(attendance)
        #~ return len(attendance)>0 and this_attendance.name == attendance[-1].name

    #~ @api.one
    #~ def _working_hours_on_day(self): # working hours on the contract
        #~ contract = self.employee_id.contract_ids[0] if self.employee_id and self.employee_id.contract_ids else False
        #~ if contract and self._check_last_sign_out(self):
            #~ self.working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(self.env.cr, self.env.uid,
                #~ contract.working_hours, fields.Datetime.from_string(self.name))
        #~ else:
            #~ self.working_hours_on_day = 0.0
    #~ working_hours_on_day = fields.Float(compute='_working_hours_on_day', string='Planned Hours')

    #~ @api.one
    #~ def _get_working_hours(self): # worked hours in schedule
        #~ contract = self.employee_id.contract_ids[0] if self.employee_id and self.employee_id.contract_ids else False
        #~ if contract and self._check_last_sign_out(self):
            #~ att = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.name[:10] + ' 00:00:00'),('name','<',self.name[:10] + ' 23:59:59')],order='name')
            #~ for (start,end) in zip(att,att[1:])[::2]:
                #~ self.get_working_hours += self.pool.get('resource.calendar').get_working_hours(self.env.cr, self.env.uid,
                #~ self.employee_id.contract_ids[0].working_hours.id,
                    #~ datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    #~ datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
        #~ else:
            #~ self.get_working_hours = False
    #~ get_working_hours = fields.Float(compute='_get_working_hours', string='Worked in schedule (h)')

    #~ @api.one
    #~ def _timesheet_amount(self):
        #~ if self.employee_id and self.employee_id.user_id and self._check_last_sign_out(self):
            #~ (self.timesheet_amount,self.timesheet_amount_invoiceable) = self.env['hr.analytic.timesheet'].get_day_amount(self.name[:10],self.employee_id)
    #~ timesheet_amount = fields.Float(compute="_timesheet_amount",string="Reported time")
    #~ timesheet_amount_invoiceable = fields.Float(compute="_timesheet_amount",string="Reported time (invoiceable)")

#~ class hr_analytic_timesheet(models.Model):
    #~ _inherit = 'hr.analytic.timesheet'

    #~ @api.model
    #~ def get_day_amount(self,date,employee):
        #~ time = self.env['hr.analytic.timesheet'].search([('user_id','=',employee.user_id.id),('date','=',date)])
        #~ amount = sum([t.unit_amount for t in time])
        #~ amount_invoiceable = sum([t.unit_amount * t.to_invoice.factor for t in time])
        #~ return (amount,amount_invoiceable)

#~ class hr_timesheet_sheet_sheet_day(osv.osv):
    #~ _name = "hr_timesheet_sheet.sheet.day"

    #~ @api.one
    #~ @api.depends('account.analytic.line.date','account.analytic.line.amount','hr.attendance.action','hr.attendance.name','hr.attendance.sheet_id')
    #~ def _total_attendance_schema(self):
        #~ contract = self.sheet_id.employee_id.contract_ids[0] if self.sheet_id.employee_id and self.sheet_id.employee_id.contract_ids else False
        #~ if contract:
            #~ att = self.env['hr.attendance'].search([('employee_id','=',self.sheet_id.employee_id.id),('name','>',self.date + ' 00:00:00'),('name','<',self.date + ' 23:59:59')],order='name')
            #~ for (start,end) in zip(att,att[1:])[::2]:
                #~ self.total_attendance_schema += self.pool.get('resource.calendar').get_working_hours(self.env.cr, self.env.uid,
                    #~ contract.working_hours.id,
                    #~ datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    #~ datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
            #~ self.total_difference_schema = self.total_attendance_schema - self.total_timesheet
        #~ else:
            #~ self.total_attendance_schema = 0.0
            #~ self.total_difference_schema = 0.0

    #~ total_attendance_schema = fields.Float(compute='_total_attendance_schema',string="Attendance (Schema)",store=True)
    #~ total_difference_schema = fields.Float(compute='_total_attendance_schema',string="Difference (Schema)",store=True)


#~ class hr_timesheet_sheet(osv.osv):
    #~ _inherit = "hr_timesheet_sheet.sheet"

    #~ @api.one
    #~ @api.depends('attendances_ids','attendances_ids.sheema_id','period_ids')
    #~ def _total_attendance_schema(self):
        #~ self.total_attendance_schema = sum([d.total_attendance_schema for d in self.period_ids])
        #~ self.total_difference_schema = sum([d.total_difference_schema for d in self.period_ids])

    #~ total_attendance_schema = fields.Float(compute='_total_attendance_schema',string="Attendance (Schema)",store=True)
    #~ total_difference_schema = fields.Float(compute='_total_attendance_schema',string="Difference (Schema)",store=True)

    #~ @api.one
    #~ @api.depends('timesheet_ids','timesheet_ids.unit_amount','timesheet_ids.to_invoice_factor')
    #~ def _total_timesheet_invoiceable(self):
        #~ self.total_timesheet_invoiceable = sum([t.unit_amount * t.to_invoice.factor for t in self.timesheet_ids])
    #~ total_timesheet_invoiceable = fields.Float(compute='_total_timesheet_invoiceable',string="Invoiceable",store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
