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

from odoo import models, fields, api, _, tools

import logging
_logger = logging.getLogger(__name__)

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def _attendance_working_hours(self):
        self.attendance_working_hours = sum(self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('check_in','>=',self.date_from + ' 00:00:00'),('check_out','<=',self.date_to + ' 23:59:59')]).mapped("get_working_hours"))
    attendance_working_hours = fields.Float(string='Attendance Schema Time',compute="_attendance_working_hours")

    @api.multi
    def get_worked_time(self, date_from, date_to):
        #TODO: how to identify worked time based on contract?
        amount = 0.0
        for line in self.env['account.analytic.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('user_id', '=', self.employee_id.user_id.id)]):
            if line.to_invoice:
                amount += line.unit_amount * (100.00 - line.to_invoice.factor) / 100.00
            else:
                amount += line.unit_amount
        return amount

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(hr_payslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        #fill all contracts that type are hourly
        hourly_contracts = self.env['hr.contract'].browse(contract_ids).filtered(lambda contract: contract.type_id.work_time == 'schema_hour')
        number_of_hours = 0.0
        if len(hourly_contracts) > 0:
            number_of_hours = self.get_worked_time(date_from, date_to)
        attendances = []
        for contract in hourly_contracts:
            attendances.append({
                 'name': _("Normal Working Hours paid at 100%"),
                 'sequence': 1,
                 'code': 'HOUR',
                 'number_of_days': 0.0,
                 'number_of_hours': number_of_hours,
                 'contract_id': contract.id,
            })
        return res + attendances


class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'

    work_time = fields.Selection(selection_add=[('schema_hour','Hourly Schema')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
