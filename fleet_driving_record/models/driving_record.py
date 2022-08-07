# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import datetime

class DrivingRecord(models.Model):
    _inherit = 'driving.record'


    @api.model
    def _default_vehicle(self):
        vehicles = self.env['fleet.vehicle'].search([('driver_id','=',self.employee_id.partner_id.id)])
        return vehicle[0].id if len(vehicles) > 0 else None

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", default=_default_vehicle,required=True)

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

    @api.model
    def _default_odometer(self):
        odometer = self.driving_record_id.vehicle_id.odometer
        for line in self.driving_record_id.line_ids:
            if line.odometer_stop > odometer:
                odometer = line.odometer_stop
        return odometer
    odoometer_start = fields.Integer(string='Odoometer start', default=_default_odometer, required=1)
    # ~ odoometer_stop = fields.Integer(string='Odoometer stop', required=1)
