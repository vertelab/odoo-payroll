# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class DrivingRecord(models.Model):
    _name = 'driving.record'
    _description = 'Driving Record'
    

    employee_id = fields.Many2one('hr.employee', string='Employee', required=1) # TODO:  defualt=FUNCTION!)
    date_start = fields.Date('Start date', required=1)
    date_stop = fields.Date('Stop date', required=1) # TODO: Should not be able to be before date_start
    analytic_account_id = fields.Many2one('account.analytic.account', string='Account', required=1)
    line_ids = fields.One2many('driving.record.line', 'driving_record_id', string='Driving record line')



    @api.constrains('date_stop')
    def stop_before_start_date(self):
        if(not self.date_start <= self.date_stop):
            raise ValidationError("Stop date can not be before the start date.")

class DrivingRecordLine(models.Model):
    _name = 'driving.record.line'
    _description = 'Driving Record Line'

    driving_record_id = fields.Many2one('driving.record', string='Driving record id', required=1)
    date = fields.Date('Date', required=1) # TODO:  default=FUNCTION!)
    type = fields.Selection([
        ('Private', 'private'),
        ('Business', 'business')
    ], string='Type', default='private') # TODO: Should be required
    odoometer_start = fields.Integer('Odoometer start', required=1) # TODO: defualt=FUNCTION!)
    odoometer_stop = fields.Integer('Odoometer stop', required=1)
    length = fields.Integer('Length', store=True, compute='compute_length')
    note = fields.Char('Note', help="Purpose of trip")


    @api.onchange('odoometer_start', 'odoometer_stop')
    @api.depends('odoometer_start', 'odoometer_stop')
    def compute_length(self):
        _logger.warning("WOOF"*999)
        _logger.warning(f"{self.odoometer_start=}, {self.odoometer_stop=}")
        self.length = self.odoometer_stop - self.odoometer_start

    #api.depends('odoometer_start', 'odoometer_stop')
    #def depent_length(self):

    # TODO: THIS CONSTRAINT DOES NOT WORK!
    @api.constrains('date')
    def stop_before_start_date(self):
        if(not self.date in range(self.driving_record_id.start_date, self.driving_record_id.stop_date)):
            raise ValidationError("Date must be within the driving range dates.")

    @api.constrains('odoometer_stop')
    def stop_before_start_date(self):
        if(not self.odoometer_start <= self.odoometer_stop):
            raise ValidationError("Stop odoometer value can not be lower than the start odoometer value.")
