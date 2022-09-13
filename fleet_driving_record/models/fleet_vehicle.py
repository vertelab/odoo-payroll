# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    product_id = fields.Many2one(comodel_name='product.product', string='Expense type', domain="[('can_be_expensed', '=', True)]", help="Exense type for drivers that have to pay for fuel")

    driving_record_count = fields.Integer(
        compute="_compute_driving_record_count", string="# Driving Record Count", store=True
    )

    driving_record_ids = fields.One2many(
        comodel_name="driving.record.line", inverse_name="vehicle_id"
    )

    @api.depends('driving_record_ids')
    def _compute_driving_record_count(self):
        for rec in self:
            rec.driving_record_count = len(self.env['driving.record.line'].search([('vehicle_id','=',rec.id)]))

    def action_view_driving_record(self):
        action = (
            self.env.ref("payroll_driving_record.action_driving_record_lines")
            .sudo()
            .read()[0]
        )
        action["domain"] = [("analytic_account_id", "=", self.analytic_account_id.id)]
        action["context"] = {'default_vehicle_id':self.id,
            'default_analytic_account_id':self.analytic_account_id.id}
        return action