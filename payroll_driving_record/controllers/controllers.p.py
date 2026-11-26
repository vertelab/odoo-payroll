# -*- coding: utf-8 -*-
# from odoo import http


# class PayrollDrivingRecord(http.Controller):
#     @http.route('/payroll_driving_record/payroll_driving_record/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_driving_record/payroll_driving_record/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_driving_record.listing', {
#             'root': '/payroll_driving_record/payroll_driving_record',
#             'objects': http.request.env['payroll_driving_record.payroll_driving_record'].search([]),
#         })

#     @http.route('/payroll_driving_record/payroll_driving_record/objects/<model("payroll_driving_record.payroll_driving_record"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_driving_record.object', {
#             'object': obj
#         })
