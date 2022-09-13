# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)
import datetime

class DrivingRecord(models.Model):
    _inherit = 'driving.record'

    @api.model
    def _default_employee(self):
        res = super(DrivingRecord,self)._default_employee()
        return self.env.user.employee_id.id


    @api.model
    def _default_vehicle(self):
        vehicle = self.env['fleet.vehicle'].search([('driver_id','=',self.env.user.employee_id.user_id.partner_id.id)],limit=1)
        return vehicle.id if vehicle else None

    # ~ @api.onchange('vehicle_id')
    # ~ def _onchange_vehicle(self):
        # ~ for record in self:
            # ~ self._context['odometer'] = record.vehicle_id.odometer

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", default=_default_vehicle,required=True,domain="[('driver_id', '=', driver_id)]" )

    @api.model
    def _default_driver(self):
        return self.employee_id.user_id.partner_id

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_driver(self):
        for record in self:
            record.driver_id = record.employee_id.user_id.partner_id

    driver_id = fields.Many2one('res.partner', string="Driver", default=_default_driver, compute=_compute_driver )
    analytic_account_id = fields.Many2one(related='vehicle_id.analytic_account_id',comodel_name='account.analytic.account', string='Registration number')
    product_id = fields.Many2one(related='vehicle_id.product_id',comodel_name='product.product', string='Expense type', domain="[('can_be_expensed', '=', True)]", help="Exense type for drivers that have to pay for fuel")


    def action_create_expense(self):
        record = super(DrivingRecord,self).action_create_expense()
        odometer = self.vehicle_id.odometer
        for line in self.line_ids:
            if line.odometer_stop > odometer:
                odometer = line.odometer_stop
        if odometer > self.vehicle_id.odometer:
            self.vehicle_id.odometer = odometer
            # ~ self.env['fleet.vehicle.odometer'].create({'vehicle_id': self.vehicle_id.id,'date': self.date,'value':})

class DrivingRecordLine(models.Model):
    _inherit = 'driving.record.line'

    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle',
        related='driving_record_id.vehicle_id', store=True)


# ~ class DrivingRecordLine(models.Model):
    # ~ _inherit = 'driving.record.line'

    # ~ def _default_odometer(self):
        # ~ raise Warning(self)
        # ~ odometer = self.driving_record_id.vehicle_id.odometer
        # ~ for line in self.driving_record_id.line_ids:
            # ~ if line.odometer_stop > odometer:
                # ~ odometer = line.odometer_stop
        
        # ~ return odometer
    # ~ odoometer_start = fields.Integer(string='Odoometer start', default=_default_odometer, required=1)
    # ~ odoometer_stop = fields.Integer(string='Odoometer stop', required=1)
