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

from odoo import models, fields, api, _
from odoo.http import request
from odoo import http
import werkzeug

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
    _inherit = ['mail.thread']
    
    color = fields.Integer()
    date = fields.Datetime(string='Date', readonly=True)
    date_in = fields.Datetime(string='Date In', readonly=True)
    date_out = fields.Datetime(string='Date Out', readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee")
    identification_id = fields.Char(related="employee_id.identification_id")
    location_id = fields.Many2one(comodel_name="hr.staff.ledger.location")
    idnumber = fields.Char(related="location_id.idnumber")
    status = fields.Selection([('checked_in', 'Log In'),('checked_out', 'Log Out'),], string='Status', readonly=True, track_visibility='always')
    address_id = fields.Many2one(related="employee_id.address_id")
    company_registry = fields.Char(related="employee_id.company_id.company_registry")
    longitude = fields.Float(digits=(8,6))
    latitude = fields.Float(digits=(8,6))
    # ~ device = fields.Char()
    

class hr_employee(models.Model):
    
    _inherit = 'hr.employee'
    
    location_ids = fields.Many2many(comodel_name="hr.staff.ledger.location")
  
  
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
    longitude = fields.Float(digits=(8,6))
    latitude = fields.Float(digits=(8,6))
    default_location = fields.Boolean(help="Check this box if this is the default location")
    
    
class project_timereport(http.Controller):
        
    @http.route(['/staffledger'], type='http', auth="user", website=True)
    def timereport_list(self, user=False, clicked=False, **post):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            request.render('website.403')
        sign = post.get('sign', False)
        trans = request.env['hr.staff.ledger.transaction'].search([('employee_id', '=', employee.id )], order='date_in desc', limit=1)
        location = None
        if trans and trans.status == 'checked_in':
            location = trans.location_id
        if sign:
            employee.attendance_manual('hr_attendance.hr_attendance_action_my_attendances')
            if trans and len(trans) == 1:
                if trans.status == 'checked_in':
                    trans.date_out =  fields.Datetime.now()
                    trans.status = 'checked_out'
                else:
                    trans.date_in =  fields.Datetime.now()
                    trans.date = fields.Datetime.now()
                    trans.location_id = post.get('location')
                    trans.date_out =  None
                    trans.status = 'checked_in'
                    trans.longitude = post.get('location_lon')
                    trans.latitude = post.get('location_lat')
                    # ~ trans.device = request.user_agent.device.family()
            elif not trans:
                request.env['hr.staff.ledger.transaction'].create({'date_in': fields.Datetime.now(), 'date': fields.Datetime.now(), 'location_id': post.get('location'), 'employee_id': employee.id, 'status': 'checked_in'})
        
        if not location and post.get('location'):
            location = request.env['hr.staff.ledger.location'].browse(int(post.get('location')))        

        ctx = {
            'employee' : employee,
            'attendance': employee.last_attendance_id,
            'location' : location,
            'default_location': request.env['hr.staff.ledger.location'].search([('default_location', '=', True)], limit=1),
        }
        return request.render('hr_staff_ledger.staffledger', ctx)

    @http.route('/staffledger/closest_pos', type='json', auth="user")
    def closest_position(self, lat=False, long=False, default_location=0, **post):
        locations = request.env['hr.staff.ledger.location'].search([])
        result = None
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if employee:
            for location in locations.with_context(employee = employee).filtered(lambda l: l.id in l._context.get('employee').location_ids.mapped('id')):
                if result:
                    d = (location.longitude - long) ** 2 + (location.latitude - lat) ** 2
                    if d < (result.longitude - long) ** 2 + (result.latitude - lat) ** 2:
                        result = location
                else:
                    result = location
            if result:
                return result.id
            else:
                return default_location
        return 0
    
    @http.route(['/staffledger/staffledgerlist'], type='http', auth="user", website=True)
    def staffledgerlist(self, user=False, clicked=False, **post):
            employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
            location = None
            if post.get('location'):
                location = request.env['hr.staff.ledger.location'].browse(int(post.get('location')))
            else :
                trans = request.env['hr.staff.ledger.transaction'].search([('employee_id', '=', employee.id ), ('date_in', '>=', fields.Date.today()+' 00:00:00'), ('date_in', '<=', fields.Date.today()+' 23:59:59')])
                if trans.status == 'checked_in':
                    location = trans.location_id
                    
            if not location:    
                location = request.env['hr.staff.ledger.location'].search([('default_location', '=', True)], limit=1)
                
                
            ctx = {
                'employee' : employee,
                'attendance': employee.last_attendance_id,
                'location' : location,
                'default_location': request.env['hr.staff.ledger.location'].search([('default_location', '=', True)], limit=1),
            }
            return request.render('hr_staff_ledger.staffledgerlist', ctx)
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
