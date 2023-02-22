import json
import math
import logging
import requests
import functools
import werkzeug.wrappers
from odoo import http
from odoo.http import request, Response
import json


class ReceiveClient(http.Controller):

    @http.route('/api/client/create', auth="none", type="json")
    def client_details(self):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        data = payload.get("data")
        if request.jsonrequest:
            try:
                if data:
                    client = {
                        'name': data['client_name'],
                        'email': data['email'],
                        'phone': data['tel'],
                        'company_type': data['company_type'],
                    }
            except:
                return 'No data or Invalid data'
            try:
                if client:
                    new_client = request.env['res.partner'].sudo().create(client)
                    args = {'Success': True, 'Message': 'Client successfully created', 'Client ID': new_client.id}
                return client, args
            except:
                return 'ERROR'
