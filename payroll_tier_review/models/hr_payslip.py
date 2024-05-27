from odoo import models, fields, api, _


class Payslip(models.Model):
    _name = "hr.payslip"
    _inherit = ["hr.payslip", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

    def _get_to_validate_message_name(self):
        name = super(Payslip, self)._get_to_validate_message_name()
        return name
