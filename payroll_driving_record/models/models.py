# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import datetime

class DrivingRecord(models.Model):
    _name = 'driving.record'
    _description = 'Driving Record'


    @api.model
    def _default_employee(self):
        return self.env.user.employee_id.id

    @api.model
    def _default_date_start(self):
        return datetime.date.today().replace(day=1)

    @api.model
    def _default_date_stop(self):
        return datetime.date.today().replace(month=(datetime.date.today().month % 12) + 1, day=1) - datetime.timedelta(days=1)

    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee, required=1)
    date_start = fields.Date('Start date', default=_default_date_start, required=1)
    date_stop = fields.Date('Stop date', default=_default_date_stop, required=1)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Registration number')
    line_ids = fields.One2many('driving.record.line', 'driving_record_id', string='Driving record line')
    expense_id = fields.Many2one('hr.expense', string='Expense report', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ], string='State', default='draft')



    @api.constrains('date_stop')
    def stop_before_start_date(self):
        if(not self.date_start <= self.date_stop):
            raise ValidationError("Stop date can not be before the start date.")

    def action_create_wizard(self):
        return {'type': 'ir.actions.act_window',
               'name': _('Select Compensation'),
               'res_model': 'create.expense.wizard',
               'target': 'new',
               'view_id': self.env.ref('payroll_driving_record.driving_record_Wizard_form').id,
               'view_mode': 'form',
               'context': {'driving_record_id': self.id}
              }

    def action_set_to_draft(self):
        if self.expense_id.state != 'done':
            self.state = 'draft'
            self.expense_id.unlink()
        else:
            raise UserError('Expense has already been paid, therefore this driving report cannot be set back to draft')
class DrivingRecordLine(models.Model):
    _name = 'driving.record.line'
    _description = 'Driving Record Line'

    driving_record_id = fields.Many2one('driving.record', string='Driving record id', required=1)

    @api.model
    def _default_date(self):
        return datetime.date.today()

    date = fields.Date('Date', required=1, default=_default_date)
    odoometer_start = fields.Integer('Odoometer start', required=1)
    odoometer_stop = fields.Integer('Odoometer stop', required=1)
    length = fields.Integer('Length (km)', store=True, compute='compute_length')
    note = fields.Char('Note', help="Purpose of trip")
    type = fields.Selection([
        ('private', 'Private'),
        ('business', 'Business')
    ], string='Type', required=1)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Destination partner')
    


    @api.onchange('odoometer_start', 'odoometer_stop')
    @api.depends('odoometer_start', 'odoometer_stop')
    def compute_length(self):
        for record in self:
            record.length = record.odoometer_stop - record.odoometer_start

    @api.constrains('date')
    def stop_before_start_date(self):
        for record in self:
            if(record.date < record.driving_record_id.date_start or record.date > record.driving_record_id.date_stop):
                raise ValidationError("Date must be within the driving range dates.")

    @api.constrains('odoometer_stop')
    def stop_before_start_odoometer(self):
        for record in self:
            if(not record.odoometer_start <= record.odoometer_stop):
                raise ValidationError("Stop odoometer value can not be lower than the start odoometer value.")




class CreateExpenseWizard(models.TransientModel):
    _name = 'create.expense.wizard'

    product_id = fields.Many2one(comodel_name='product.product', string='Compensation', domain="[('can_be_expensed', '=', True)]")

    def action_done(self):
        driving_record = self.env['driving.record'].browse(self.env.context['driving_record_id'])
        driving_record.state = 'sent'
        quantity = 0
        for line in driving_record.line_ids:
            quantity += line.length
        expense = self.env['hr.expense'].create({
            'name': driving_record.employee_id.name + _(' - Driving Compensation - ') + datetime.date.today().strftime("%d/%m/%Y"),
            'product_id': self.product_id.id,
            'unit_amount': self.product_id.lst_price,
            'quantity': quantity,
            'employee_id': driving_record.employee_id.id,
            'company_id': driving_record.employee_id.company_id.id,
        })
        driving_record.expense_id = expense
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'hr.expense',
            'target': 'current',
            'res_id': expense.id,
        }
