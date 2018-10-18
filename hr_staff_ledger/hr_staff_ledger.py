# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2018 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


import logging
_logger = logging.getLogger(__name__)


class hr_staff_ledger(models.Model):
    """
        Holding a Staff ledger is requierd by goverment for certain industries
        
        En staff_ledger för varje plats, datum och anställd. Skapas när första hr.staff.ledger.transaction
        skapas. 
        
        Rapportering:
        * inloggade personer på en plats (skatteverkets krav)
           Datum + utskriftstid, plats, ev idnummer, personer: namn (personnummer) företag (organisationsnummer) tid in, ev tid ut
           möjlighet att maila till en tjänsteman på skatteverket
        * Översikt för en plats
          Personer: namn, status, ev note, tid in
        
    
    """
    _name = 'hr.staff.ledger'

    date = fields.Date(string='Date')
    location_id = fields.Many2one(comodel_name="hr.staff.ledger.location")
    employee_id = fields.Many2one(comodel_name="hr.employee")
    status = fields.Selection([('open', 'Open'),('closed', 'Closed'),], string='Status', readonly=True)    
    comment = fields.Text(string='Notes')


class hr_staff_ledger_transaction(models.Model):
    """
        In/ut-loggning för en plats / person
        
        Inloggningsformulär backoffice (val av plats)
            
    """
    _name = 'hr.staff.ledger.transaction'

    date = fields.Datetime(string='Date')
    employee_id = fields.Many2one(comodel_name="hr.employee")
    location_id = fields.Many2one(comodel_name="hr.staff.ledger.location")
    status = fields.Selection([('in', 'Log In'),('out', 'Logiut'),], string='Status', readonly=True)
    longitude = fields.Float()
    latitude = fields.Float()
    
  
class hr_staff_ledger_location(models.Model):
    """
        En plats där man kan föra personalliggare. Vissa platser måste registreras hos skattemyndigheten, 
        t ex byggarbetsplatser. Platsen får då ett skatteid
    
    """
    _name = 'hr.staff.ledger.location'

    name = fields.Char(string="Name",index=True)
    comment = fields.Text(string='Notes')
    registered = fields.Boolean(help="Check this box if this location is registered by the goverment.")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    idnumber = fields.Char(string="Identification number",help="Identification number given by goverment when location was registered")
    longitude = fields.Float()
    latitude = fields.Float()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
