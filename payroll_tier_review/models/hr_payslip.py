from odoo import models, fields, api, _


class Payslip(models.Model):
    _name = "hr.payslip"
    _inherit = ["hr.payslip", "tier.validation"]
    _state_from = ["verify"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

    @api.depends("need_validation")
    def _compute_hide_post_button(self):
        result = super()._compute_hide_post_button()
        for this in self:
            this.hide_post_button |= this.need_validation
        return result

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + ["move_id", "compute_date", "number", "line_ids", "state"]

    def _get_to_validate_message_name(self):
        name = super(Payslip, self)._get_to_validate_message_name()
        return name