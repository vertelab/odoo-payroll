# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018- Vertel (<http://vertel.se>).
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


class HRExpense(models.Model):
    _inherit = 'hr.expense'

    # #if VERSION < "19.0"
    # Odoo 19+ owns hr.expense.journal_id (related to the payment method line's
    # journal, readonly). Redeclaring it here would clash with core, so the
    # field is only declared where core does not have it.
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'purchase')]")

    def _create_sheet_from_expenses(self):
        # Renamed to action_submit()/_create_sheets_from_expense() in 19.0.
        res = super()._create_sheet_from_expenses()
        if self.journal_id:
            res.journal_id = self.journal_id
        return res
    # #endif



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
