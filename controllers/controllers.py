import json
import math
import logging
import requests
from odoo import http, _, exceptions
from odoo.http import request, Response
import json


class Purchase(http.Controller):

    @http.route('/api/get-po',  auth="none", methods=['GET'])
    def po_details(self):
        headers = {'Content-Type': 'application/json'}
        response = []
        try:
            purchase_details = request.env['hr.employee'].sudo().search([])
        except:
            return ('cant access')

        for rec in purchase_details:
            response.append({'name': rec.name})

        return Response(json.dumps(response), headers=headers)

