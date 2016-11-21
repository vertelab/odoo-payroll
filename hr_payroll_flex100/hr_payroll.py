# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
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

from openerp import tools
from openerp import models, fields, api, _

import openerp.tools
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    @api.one
    def _flextime(self):
        if self.employee_id.contract_id and self._check_last_sign_out(self):
            job_intervals = self.pool.get('resource.calendar').get_working_intervals_of_day(self.env.cr,self.env.uid,
                    self.employee_id.contract_id.working_hours.id,
                    start_dt=datetime.strptime(self.name, tools.DEFAULT_SERVER_DATETIME_FORMAT).replace(hour=0,minute=0))
            att = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.name[:10] + ' 00:00:00'),('name','<',self.name[:10] + ' 23:59:59')],order='name')
            flex_begin =  job_intervals[0][0] - datetime.strptime(att[0].name, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            _logger.error('job_int %s - att %s = %s' % (job_intervals[0][0],datetime.strptime(att[0].name, tools.DEFAULT_SERVER_DATETIME_FORMAT),flex_begin))
            flex_end = datetime.strptime(att[-1].name, tools.DEFAULT_SERVER_DATETIME_FORMAT) - job_intervals[-1][1]
            self.flextime = (flex_begin + flex_end).total_seconds() / 60.0
    flextime = fields.Float(compute='_flextime', string='Flex Time (m)')
    
    @api.one
    def _flex_working_hours(self): 
        flex_working_hours = 0.0
        if self._check_last_sign_out(self):
            att = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.name[:10] + ' 00:00:00'),('name','<',self.name[:10] + ' 23:59:59')],order='name')
            for (start,end) in zip(att,att[1:])[::2]:
                flex_working_hours += (datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() / 60.0 / 60.0
        self.flex_working_hours = flex_working_hours
    flex_working_hours = fields.Float(compute='_flex_working_hours', string='Worked Flex (h)')

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def _holiday_ids(self):
        self.holiday_ids = self.env['hr.holidays.status'].search([('active','=',True),('limit','=',False)])
        self.holiday_ids += self.env['hr.holidays.status'].search([('id','in',[self.env.ref('l10n_se_hr_payroll.sick_leave_qualify').id,self.env.ref('l10n_se_hr_payroll.sick_leave_214').id,self.env.ref('l10n_se_hr_payroll.sick_leave_100').id])])
    holiday_ids = fields.Many2many(comodel_name="hr.holidays.status",compute="_holiday_ids")
    @api.one
    def _flextime(self):
        self.flextime = sum(self.env['hr_timesheet_sheet.sheet'].search([('employee_id','=',self.employee_id.id),('date_from','>=',self.date_from),('date_to','<=',self.date_to)]).mapped("flextime"))
    flextime = fields.Float(string='Flex Time (m)',compute="_flextime")
    @api.one
    def _compensary_leave(self):
        holidays = self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('holiday_status_id','=',self.env.ref("hr_payroll_flex100.compensary_leave").id)])
        self.compensary_leave = sum(holidays.filtered(lambda h: h.type == ' add').mapped("number_of_days_temp")) - sum(holidays.filtered(lambda h: h.type == 'remove').mapped("number_of_days_temp"))
        self.total_compensary_leave = self.compensary_leave + (self.flextime / 60.0 / 24.0)
    compensary_leave = fields.Float(string='Compensary Leave',compute="_compensary_leave")
    total_compensary_leave = fields.Float(string='Total Compensary Leave',compute="_compensary_leave")
    
    
    #~ @api.model
    #~ def get_worked_day_lines(self,contract_ids, date_from, date_to, context=None):
        #~ return super(hr_payslip,self).get_worked_day_lines(contract_ids,date_from,date_to)

    @api.one
    def hr_verify_sheet(self):
        #~ raise Warning(datetime(2016,11,21,8,32))
                        #~ self.get_working_hours += self.env['resource.calendar'].get_working_hours(self.employee_id.contract_ids[0].working_hours.id,
                    #~ datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    #~ datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))

        #~ raise Warning(self.pool.get('resource.calendar').get_working_intervals_of_day(self.env.cr,self.env.uid,self.employee_id.contract_id.working_hours.id,start_dt=datetime(2016,11,21,0,0),))
        #~ raise Warning(self.env['resource.calendar'].schedule_days_get_date(1,self.employee_id.contract_id.working_hours.id,date_day=datetime(2016,11,21,0,0)))
        #~ schedule_days_get_date(self, cr, uid, id, days, day_date=None, compute_leaves=False,
                               #~ resource_id=None, default_interval=None, context=None):
        #~ """ Wrapper on _schedule_days: return the beginning/ending datetime of"""
        
        number_of_days = self.flextime / 60.0 / 24.0 # minutes to days
        self.env['hr.holidays'].create({
            'holiday_status_id': self.env.ref("hr_payroll_flex100.compensary_leave").id,
            'employee_id': self.employee_id.id,
            'type': 'add' if number_of_days > 0.0 else 'remove' ,
            'state': 'validate',
            'number_of_days_temp': number_of_days,
            #~ 'date_from': self.date_from,
            #~ 'date_to': self.date_to,
            })
        return super(hr_payslip,self).hr_verify_sheet()        

    #~ def refund_sheet(self, cr, uid, ids, context=None):
        #~ mod_obj = self.pool.get('ir.model.data')
        #~ for payslip in self.browse(cr, uid, ids, context=context):
            #~ id_copy = self.copy(cr, uid, payslip.id, {'credit_note': True, 'name': _('Refund: ')+payslip.name}, context=context)
            #~ self.signal_workflow(cr, uid, [id_copy], 'hr_verify_sheet')
            #~ self.signal_workflow(cr, uid, [id_copy], 'process_sheet')
            
        #~ form_id = mod_obj.get_object_reference(cr, uid, 'hr_payroll', 'view_hr_payslip_form')
        #~ form_res = form_id and form_id[1] or False
        #~ tree_id = mod_obj.get_object_reference(cr, uid, 'hr_payroll', 'view_hr_payslip_tree')
        #~ tree_res = tree_id and tree_id[1] or False
        #~ return {
            #~ 'name':_("Refund Payslip"),
            #~ 'view_mode': 'tree, form',
            #~ 'view_id': False,
            #~ 'view_type': 'form',
            #~ 'res_model': 'hr.payslip',
            #~ 'type': 'ir.actions.act_window',
            #~ 'nodestroy': True,
            #~ 'target': 'current',
            #~ 'domain': "[('id', 'in', %s)]" % [id_copy],
            #~ 'views': [(tree_res, 'tree'), (form_res, 'form')],
            #~ 'context': {}
        #~ }
    
class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
        
    @api.one
    @api.depends('attendances_ids','attendances_ids.sheet_id')
    def _flex_working_hours(self): 
        self.flex_working_hours = sum(self.attendances_ids.mapped('flex_working_hours'))
        self.flextime = sum(self.attendances_ids.mapped('flextime'))
    flex_working_hours = fields.Float(compute='_flex_working_hours', string='Worked Flex (h)')
    flextime = fields.Float(compute='_flex_working_hours', string='Flex Time (m)')

class hr_holidays(models.Model):
    _inherit='hr.holidays.status'
    
    @api.one
    def _ps_max_leaves(self):
        slip = self.env['hr.payslip'].browse(self._context.get('slip_id',None))
        if slip:
            holiday_ids = self.env['hr.holidays'].search([('holiday_status_id','=',self.id),('state','=','validate'),('employee_id','=',slip.employee_id.id),('date_from','>=',slip.date_from),('date_to','<=',slip.date_to)])
            self.ps_max_leaves = sum(holiday_ids.filtered(lambda h: h.type == 'add').mapped('number_of_days_temp'))
            self.ps_leaves_taken = sum(holiday_ids.filtered(lambda h: h.type == 'remove').mapped('number_of_days_temp'))
    ps_max_leaves = fields.Integer(string='Max Leaves',compute='_ps_max_leaves')
    ps_leaves_taken = fields.Integer(string='Max Leaves',compute='_ps_max_leaves')
      
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
