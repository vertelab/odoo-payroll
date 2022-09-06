# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import datetime

class Lead(models.Model):
    _inherit = 'crm.lead'

    driving_record_lines_count = fields.Integer('Driving Records',
     compute='_compute_driving_record_lines_count')

    def action_get_driving_record_lines(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('payroll_driving_record.action_driving_record_lines')
        res['domain'] = [('partner_id.id', '=', self.partner_id.id)]
        return res

    def _compute_driving_record_lines_count(self):
        for lead in self:
            lead.driving_record_lines_count = self.env['driving.record.line'].search_count([
                ('partner_id.id', '=', lead.partner_id.id)])