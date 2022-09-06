# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import datetime

class DrivingRecord(models.Model):
    _name = 'driving.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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

    @api.onchange('line_ids')
    @api.depends('line_ids')
    def _compute_private_length(self) :
        for record in self:
            record.private_length = 0
            for lines in record.line_ids:
                if lines.type == 'private':
                    record.private_length = record.private_length + lines.length

    @api.onchange('line_ids')
    @api.depends('line_ids')
    def _compute_business_length(self) :
        for record in self:
            record.business_length = 0
            for lines in record.line_ids:
                if lines.type == 'business':
                    record.business_length = record.business_length + lines.length

    @api.depends('date_start','date_stop')
    def _compute_name(self):
        for record in self:
            record.name = _(f'{record.employee_id.name} {record.date_start} - {record.date_stop}')
    name = fields.Char(compute=_compute_name)
    product_id = fields.Many2one(comodel_name='product.product', string='Compensation', domain="[('can_be_expensed', '=', True)]")
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', default=_default_employee, required=1)
    date_start = fields.Date(string='Start date', default=_default_date_start, required=1)
    date_stop = fields.Date(string='Stop date', default=_default_date_stop, required=1)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Registration number')
    line_ids = fields.One2many(comodel_name='driving.record.line', inverse_name='driving_record_id', string='Driving record line')
    expense_id = fields.Many2one(comodel_name='hr.expense', string='Expense report', readonly=True)
    expense_state = fields.Selection(related='expense_id.state', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ], string='State', default='draft')
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'purchase')]")
    private_length = fields.Integer(compute=_compute_private_length)
    business_length = fields.Integer(compute=_compute_business_length)


    @api.constrains('date_start','date_stop')
    def stop_before_start_date(self):
        if(not self.date_start <= self.date_stop):
            raise ValidationError("Stop date can not be before the start date.")

    @api.constrains('date_start','date_stop')
    def overlapping_dates(self):
        for records in self.env['driving.record'].search([('employee_id.id','=',self.employee_id.id), ('id','!=',self.id)]):
            _logger.warning(f"{records.id=}" + "  " f"{self.id}")
            _logger.warning(f"{records.date_start=}" + " to " + f"{records.date_stop=}" + "  vs  " + f"{self.date_start=}" + " to " + f"{self.date_stop=}")
            if not((records.date_start < self.date_start and records.date_stop < self.date_start) or
                   (records.date_start > self.date_stop and records.date_stop > self.date_stop)):
                raise ValidationError("The selected time period overlaps with an existing time period, which is not allowed.")

    def action_create_expense(self):
        self.state = 'sent'
        expense = self.env['hr.expense'].create({
            'name': _(f'{self.employee_id.name} - Driving Compensation - {fields.Date.today()}'),
            'product_uom_id': self.product_id.uom_id.id,
            'unit_amount': self.product_id.lst_price,
            'quantity': sum(self.line_ids.filtered(lambda e : e.type == "business").mapped('length'))  / 10,
            'employee_id': self.employee_id.id,
            'company_id': self.employee_id.company_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'journal_id': self.journal_id.id
        })
        expense.product_id = self.product_id.id
        self.expense_id = expense
        expense.message_post(body=_(f'Based on <A href="/web#id={self.id}&model=driving.record">Driving record</A> '))
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'hr.expense',
            'target': 'current',
            'res_id': expense.id,
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

    driving_record_id = fields.Many2one('driving.record', string='Driving record id', required=1, ondelete='cascade')

    @api.model
    def _default_date(self):
        return datetime.date.today()

    date = fields.Date(string='Date', required=1, default=_default_date)
    odometer_start = fields.Integer(string='odometer start', required=1)
    odometer_stop = fields.Integer(string='odometer stop', required=1)
    length = fields.Integer(string='Length (km)', store=True, compute='compute_length')
    note = fields.Char(string='Note', help="Purpose of trip")
    type = fields.Selection([
        ('private', 'Private'),
        ('business', 'Business')
    ], string='Type', required=1)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Destination partner')
    vehicle_id = fields.Many2one(comodel_name='account.analytic.account', string='Vehicle', related='driving_record_id.analytic_account_id',store=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', related='driving_record_id.employee_id', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ], string='State',related='driving_record_id.state', store=True)

    @api.onchange('odometer_start', 'odometer_stop')
    @api.depends('odometer_start', 'odometer_stop')
    def compute_length(self):
        for record in self:
            record.length = record.odometer_stop - record.odometer_start

    @api.constrains('date')
    def stop_before_start_date(self):
        for record in self:
            if(record.date < record.driving_record_id.date_start or record.date > record.driving_record_id.date_stop):
                raise ValidationError("Date must be within the driving range dates.")

    @api.constrains('odometer_stop')
    def stop_before_start_odometer(self):
        for record in self:
            if(not record.odometer_start <= record.odometer_stop):
                raise ValidationError("Stop odometer value can not be lower than the start odometer value.")

    @api.model
    def add_driving_line(self,date,odometer_start,odometer_stop,note,type,employee_id,return_line=False):
        record = self.env['driving.record'].search([('date_start','<=',date),('date_stop','>=',date),('employee_id','=',employee_id)],limit=1)

        if not record:
            record = self.env['driving.record'].create(self.env['driving.record.line'].add_driving_line_record(date,employee_id))
        vals = {
            'driving_record_id': record.id,
            'date': date,
            'type': type,
            'odometer_start': odometer_start,
            'odometer_stop': odometer_stop,
            'note': note,
        }
        line = self.env['driving.record.line'].create(vals)
        if return_line:
            return line
        return record != None

    def add_driving_line_record(self,date,employee_id):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return {
                'employee_id': employee_id,
                'date_start': date.replace(day=1),
                'date_stop': date.replace(month=(date.month % 12) + 1, day=1) - datetime.timedelta(days=1),
            }

    @api.model
    def create(self,values):
        if not 'driving_record_id' in values:
            _logger.warning("In the If")
            line = self.add_driving_line(
                values.get('date', fields.Date.today()),
                values.get('odometer_start'),
                values.get('odometer_stop'),
                values.get('note'),
                values.get('type', 'private'),
                values.get('employee_id', self.env.user.employee_id.id),
                True)
            _logger.warning(f"{self._context.get('partner_id')=}")
            _logger.warning(f"{self.env.context.get('partner_id')=}")
            line.partner_id = self._context.get('partner_id', None)
        else:
            _logger.warning(f"{values=}")
            line = super(DrivingRecordLine, self).create(values)
        return line