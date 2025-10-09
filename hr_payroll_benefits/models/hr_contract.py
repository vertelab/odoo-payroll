import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    benefit_ids = fields.One2many(comodel_name="hr.contract.benefit",inverse_name='contract_id')

    def benefit_value(self,code):
        return sum(self[0].benefit_ids.filtered(lambda b: b.name == code).mapped('value'))

class hr_contract_benefit(models.Model):
    _name = 'hr.contract.benefit'

    contract_id = fields.Many2one(comodel_name="hr.contract")
    name = fields.Many2one(comodel_name='hr.benefit',string="Code")
    desc = fields.Char(string="Description")
    # ~ value = fields.Float(string="Value",digits_compute=dp.get_precision('Payroll'),)
    value = fields.Float(string="Value")

    #@api.depends('contract_id','name')
    @api.onchange('name')
    def onchange_name(self):
        for b in self:
            b.desc = b.name.desc

class hr_benefit(models.Model):
    _name = 'hr.benefit'

    code_id = fields.Many2one(comodel_name='hr.salary.rule')
    name = fields.Char(string="Name")
    desc = fields.Char(string="Description")
    note = fields.Text(string="Note")