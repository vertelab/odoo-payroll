from odoo import fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employee_fund_invoice_state_is_draft = fields.Boolean(string='Employee Fund Invoice Status', config_parameter='hr_payroll_employeefund_expenses.employee_fund_invoice_state_is_draft')
    fill_employee_fund_invoice_state_is_draft = fields.Boolean(string='Fill Employee Fund Invoice Status', config_parameter='hr_payroll_employeefund_expenses.fill_employee_fund_invoice_state_is_draft')
