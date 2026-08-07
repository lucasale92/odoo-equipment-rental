from odoo import http
from odoo.http import request


class RentalDemoLogin(http.Controller):
    """Acceso directo para el portfolio: loguea con un usuario de demo
    de solo lectura/gestión sobre el módulo de alquiler (sin permisos de
    administración de Odoo) y redirige a la app."""

    @http.route('/demo-login', type='http', auth='none', csrf=False)
    def demo_login(self, **kwargs):
        credential = {'login': 'demo', 'password': 'demo', 'type': 'password'}
        request.session.authenticate(request.env, credential)
        return request.redirect('/odoo')
