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
            if len(job_intervals) > 0:
                flex_begin =  job_intervals[0][0] - datetime.strptime(att[0].name, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                #~ _logger.error('job_int %s - att %s = %s' % (job_intervals[0][0],datetime.strptime(att[0].name, tools.DEFAULT_SERVER_DATETIME_FORMAT),flex_begin))
                flex_end = datetime.strptime(att[-1].name, tools.DEFAULT_SERVER_DATETIME_FORMAT) - job_intervals[-1][1]
                self.flextime = (flex_begin + flex_end).total_seconds() / 60.0
    flextime = fields.Float(compute='_flextime', string='Flex Time (m)')

    @api.one
    def _flex_working_hours(self):
        flex_working_hours = 0.0
        #~ get_working_hours = 0.0
        leaves = 0.0
        if self._check_last_sign_out(self):
            att = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.name[:10] + ' 00:00:00'),('name','<',self.name[:10] + ' 23:59:59')],order='name')
            for (start,end) in zip(att,att[1:])[::2]:
                #~ get_working_hours += self.pool.get('resource.calendar').get_working_hours(self.env.cr, self.env.uid,
                                                                                            #~ self.employee_id.contract_id.working_hours.id,
                                                                                            #~ datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT),
                                                                                            #~ datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT))
                flex_working_hours += (datetime.strptime(end.name, tools.DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(start.name, tools.DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() / 60.0 / 60.0
            job_intervals = self.pool.get('resource.calendar').get_working_intervals_of_day(self.env.cr,self.env.uid,
                    self.employee_id.contract_id.working_hours.id,
                    start_dt=datetime.strptime(self.name, tools.DEFAULT_SERVER_DATETIME_FORMAT).replace(hour=0,minute=0))
            for f,s in zip(job_intervals,job_intervals[1::])[::2]:
                leaves += (f[1] - s[0]).total_seconds() / 60.0 / 60.0
        #~ _logger.warn('leaves %s ' % leaves)
        self.flex_working_hours = flex_working_hours + leaves
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
        self.flextime = sum(self.env['hr.attendance'].search([('employee_id', '=',self.employee_id.id), ('name', '>', self.date_from + ' 00:00:00'), ('name', '<', self.date_to + ' 23:59:59')]).mapped("flextime"))
        self.flex_working_hours = sum(self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('name','>',self.date_from + ' 00:00:00'),('name','<',self.date_to + ' 23:59:59')]).mapped("flex_working_hours"))
    flextime = fields.Float(string='Flex Time (m)',compute="_flextime")
    flex_working_hours = fields.Float(compute='_flextime', string='Worked Flex (h)')
    @api.one
    def _compensary_leave(self):
        _logger.warn('\n\n\nbuu\n\n\n')
        # TODO: Fix issues with leaves spanning two or more months.
        if self.state == 'draft':
            holidays = self.env['hr.holidays'].search([('employee_id', '=', self.employee_id.id), ('holiday_status_id', '=', self.env.ref("hr_payroll_flex100.compensary_leave").id), ('date_to', '<', self.date_to + ' 23:59:59')])
            self.write({'compensary_leave': sum(holidays.filtered(lambda h: h.type == 'add').mapped("number_of_days_temp")) - sum(holidays.filtered(lambda h: h.type == 'remove').mapped("number_of_days_temp"))})
        self.total_compensary_leave = self.compensary_leave + (self.flextime / 60.0 / 24.0)
    compensary_leave = fields.Float(string='Compensary Leave') #,compute="_compensary_leave", store=True)
    total_compensary_leave = fields.Float(string='Total Compensary Leave',compute="_compensary_leave")
    


    #~ @api.model
    #~ def get_worked_day_lines(self,contract_ids, date_from, date_to, context=None):

        #~ return super(hr_payslip,self).get_worked_day_lines(contract_ids,date_from,date_to)



    @api.one
    def Xcompute_sheet(self):
        super(hr_payslip,self).compute_sheet()
        work100 = self.worked_days_line_ids.filtered(lambda l: l.code == 'WORK100' or l.code == 'FLEX100')
        number_of_hours = work100.number_of_hours
        number_of_days  = work100.number_of_days
        work100.write({'code': 'WORK100'})
        work100.write({'number_of_hours': self.flex_working_hours})
        _logger.warn('hours %s days %s flex %s days %s' % (number_of_hours,number_of_days,self.flex_working_hours,self._get_nbr_of_days()))
        return True

    def Xget_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res




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

        #raise Warning(self.worked_days_line_ids)
        self.employee_id.set_flex_time_pot(self.flextime / 60.0 / 24.0, self.date_to) # minutes to days
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

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    flex_holiday_id = fields.Many2one(comodel_name='hr.holidays', string='Flex Time Bank')
    
    def set_flex_time_pot(self, days, date = fields.Datetime.now()):
        date_to = fields.Datetime.from_string('1970-01-01 00:00:00') + timedelta(days = days)
        if self.flex_holiday_id:
            self.flex_holiday_id.write({
                'name': 'Time Bank for %s (%s)' % (self.name, date),
                'type': 'add' if days > 0.0 else 'remove',
                'number_of_days_temp': abs(days),
                'date_to': date_to,
            })
        else:
            self.flex_holiday_id = self.env['hr.holidays'].create({
                'name': 'Time Bank for %s (%s)' % (self.name, date),
                'holiday_status_id': self.env.ref("hr_payroll_flex100.compensary_leave").id,
                'employee_id': self.id,
                'type': 'add' if days > 0.0 else 'remove' ,
                'state': 'validate',
                'number_of_days_temp': abs(days),
                'date_from': '1970-01-01 00:00:00',
                'date_to': date_to,
            })

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

class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"
    
    @api.multi
    def name_get(self):
        """Add flex time to name."""
        res = super(hr_holidays_status, self).name_get()
        for hs in self:
            if hs == self.env.ref("hr_payroll_flex100.compensary_leave"):
                for i in range(0, len(res)):
                    if res[i][0] == hs.id:
                        res[i] = (hs.id, res[i][1] + ('  (%g/%g)' % ((hs.leaves_taken or 0.0) * 24 * 60, (hs.max_leaves or 0.0) * 24 * 60)))
        return res

class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'

    work_time = fields.Selection(selection_add=[('flex','Flex Time')])


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
