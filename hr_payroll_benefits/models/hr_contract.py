# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


import logging
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



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
