# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    product_id = fields.Many2one(comodel_name='product.product', string='Expense type', domain="[('can_be_expensed', '=', True)]", help="Exense type for drivers that have to pay for fuel")


    driving_record_ids = fields.One2many(
        "driving.record.line", "vehicle_id", "Driving Record Logs"
    )

    driving_record_count = fields.Integer(
        compute="_compute_driving_record_count", string="# Driving Record Count"
    )

    @api.depends("driving_record_ids")
    def _compute_driving_record_count(self):
        for rec in self:
            rec.driving_record_count = len(rec.driving_record_ids)

    def action_view_inspection(self):
        action = (
            self.env.ref("fleet_driving_record.fleet_driving_record_act_window")
            .sudo()
            .read()[0]
        )
        if self.inspection_count > 1:
            action["domain"] = [("id", "in", self.driving_record_ids.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref(
                        "fleet_driving_record.fleet_driving_record_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = (
                self.driving_record_ids and self.driving_record_ids.ids[0] or False
            )
        return action