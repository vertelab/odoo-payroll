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
            record.name = f'{record.employee_id.name} {record.date_start} - {record.date_stop}'

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
            raise ValidationError(_("Stop date can not be before the start date."))

    @api.constrains('date_start','date_stop','employee_id','analytic_account_id')
    def overlapping_dates(self):
        for record in self.env['driving.record'].search([('employee_id.id','=',self.employee_id.id), ('analytic_account_id.id','=',self.analytic_account_id.id), ('id','!=',self.id)]):
            if not((record.date_start < self.date_start and record.date_stop < self.date_start) or
                   (record.date_start > self.date_stop and record.date_stop > self.date_stop)):
                raise ValidationError(_("The selected time period overlaps with an existing time period for this employee, which is not allowed."))

    @api.constrains('analytic_account_id')
    def check_odometer_on_vehicle_change(self):
        for record in self.env['driving.record'].search([('analytic_account_id.id','=',self.analytic_account_id.id)]):
            for line in record.line_ids:
                line.odomoter_constraints()

    @api.depends('analytic_account_id')
    def check_overlaping_odometer(self):
        for lines in self.line_ids:
            lines.overlaping_odometer()
            lines.gap_odometer()

    def action_create_expense(self):
        self.state = 'sent'
        expense = self.env['hr.expense'].create({
            'name': (f'{self.employee_id.name}' + ' - ' + _('Driving Compensation') + ' - ' + f'{fields.Date.today()}'),
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
        expense.message_post(body=(f'Based on <A href="/web#id={self.id}&model=driving.record">' + _('Driving record') + '</A> '))
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
            raise UserError(_('Expense has already been paid, therefore this driving report cannot be set back to draft'))


class DrivingRecordLine(models.Model):
    _name = 'driving.record.line'
    _description = 'Driving Record Line'

    driving_record_id = fields.Many2one('driving.record', string='Driving record id', ondelete='cascade')

    @api.model
    def _default_date(self):
        return datetime.date.today()

    date = fields.Date(string='Date', required=1, default=_default_date)
    length = fields.Integer(string='Length (km)', store=True, compute='compute_length')
    odometer_start = fields.Integer(string='Odometer start', required=1, store=True)
    odometer_stop = fields.Integer(string='Odometer stop', required=1)
    note = fields.Char(string='Note', help=_("Purpose of trip"))
    type = fields.Selection([
        ('private', 'Private'),
        ('business', 'Business')
    ], string='Type', required=1)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Destination partner')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Vehicle', related='driving_record_id.analytic_account_id',store=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', related='driving_record_id.employee_id', store=True)
    state = fields.Selection(string='State',related='driving_record_id.state', store=True)

    @api.onchange('odometer_start', 'odometer_stop')
    @api.depends('odometer_start', 'odometer_stop')
    def compute_length(self):
        for record in self:
            record.length = record.odometer_stop - record.odometer_start

    @api.constrains('date')
    def stop_before_start_date(self):
        for record in self:
            if record.driving_record_id.date_start is False or record.driving_record_id.date_stop is False:
                continue
            if(record.date < record.driving_record_id.date_start or record.date > record.driving_record_id.date_stop):
                raise ValidationError(_("Date must be within the driving range dates."))

    # Performs several odometer constraints in the correct order:
    @api.constrains('odometer_start', 'odometer_stop', 'type')
    def odomoter_constraints(self):
        # Checks that odometer_start and odometer_stop are not left as 0 and 0
        self.odometer_both_zero()
        # Checks that start and stop dates are not in the wrong order
        self.stop_before_start_odometer()
        # Checks that the odometer readings never overlap with eachother, per vehicle.
        self.overlapping_odometer()
        # Checks that there are no gaps between odometer records, per vehicle.
        self.gaps_odometer()

    def odometer_both_zero(self):
        for record in self:
            if record.odometer_start == 0 and record.odometer_stop == 0:
                raise ValidationError(_("Start odometer and stop odometer may not both be 0."))

    def stop_before_start_odometer(self):
        for record in self:
            if(not record.odometer_start <= record.odometer_stop):
                raise ValidationError(_("Stop odometer value can not be lower than the start odometer value."))

    def overlapping_odometer(self):
        if self.analytic_account_id.id == False:
            lines = self.env['driving.record.line'].search([('analytic_account_id','=',False), ('id','!=',self.id)])
        else:
            lines = self.env['driving.record.line'].search([('analytic_account_id.id','=',self.analytic_account_id.id), ('id','!=',self.id)])

        for line in lines:
            if not((line.odometer_start <= self.odometer_start and line.odometer_stop <= self.odometer_start) or
                   (line.odometer_start >= self.odometer_stop and line.odometer_stop >= self.odometer_stop)):
                raise ValidationError(_("There is overlap of the odometer records for the following Driving Record lines:") + '\n' +
                f"{line.date} " + _("start:") + f" {line.odometer_start} " + _("stop:") + f" {line.odometer_stop} " + '\n' +
                f"{self.date} " + _("start:") + f" {self.odometer_start} " + _("stop:") + f" {self.odometer_stop} ")

    def gaps_odometer(self):
        odometer_lowest = self.odometer_start
        odometer_higest = self.odometer_stop
        sum_distance = self.odometer_stop - self.odometer_start

        if self.analytic_account_id.id == False:
            lines = self.env['driving.record.line'].search([('analytic_account_id','=',False), ('id','!=',self.id)])
        else:
            lines = self.env['driving.record.line'].search([('analytic_account_id.id','=',self.analytic_account_id.id), ('id','!=',self.id)])

        for line in lines:
            sum_distance = sum_distance + line.odometer_stop - line.odometer_start
            if line.odometer_start < odometer_lowest:
                odometer_lowest = line.odometer_start
            if line.odometer_stop > odometer_higest:
                odometer_higest = line.odometer_stop
        if odometer_higest - odometer_lowest != sum_distance:
                raise ValidationError(_("Expected total distance, based on highest and lowest odometer values,") + '\n' +
                _("did not match actual total distance:") + '\n' +
                _("Was expected to be:") + f" {odometer_higest - odometer_lowest} " + '\n' +
                _("But was found to be:") + f" {sum_distance}" + '\n' + '\n' +
                _("Is there a gap between Odometer records?"))

    @api.model
    def add_driving_line(self,date,odometer_start,odometer_stop,note,type,employee_id,partner_id,return_line=False):
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
            'partner_id': partner_id,
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
        if (not 'driving_record_id' in values) or values.get('driving_record_id') == False:
            line = self.add_driving_line(
                values.get('date', fields.Date.today()),
                values.get('odometer_start'),
                values.get('odometer_stop'),
                values.get('note'),
                values.get('type', 'private'),
                values.get('employee_id', self.env.user.employee_id.id),
                values.get('partner_id', False),
                True)
            if line.partner_id == False:
                line.partner_id = self._context.get('partner_id', None)
        else:
            _logger.warning(f"{values=}")
            line = super(DrivingRecordLine, self).create(values)
        return line