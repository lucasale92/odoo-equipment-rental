{
    'name': 'Equipment Rental',
    'version': '19.0.1.0.0',
    'category': 'Operations/Rental',
    'summary': 'Gestión de alquiler de equipos por días: reservas, disponibilidad, '
               'contratos y facturación.',
    'description': """
Equipment Rental
================
Módulo de demostración que gestiona el alquiler de equipos por días.

Funcionalidades:
    * Catálogo de equipos con tarifa diaria y estado.
    * Órdenes de alquiler con líneas, cálculo automático de días e importe.
    * Control de disponibilidad (impide doble reserva en fechas solapadas).
    * Flujo de estados: Borrador -> Confirmado -> En curso -> Devuelto.
    * Vista calendario y cuadros de mando (pivot/graph).
    * Asistente de devolución con cargo por retraso.
    * Contrato de alquiler imprimible (PDF QWeb).
    * Recordatorio automático de devoluciones vencidas (cron).
    * Creación de factura de cliente desde la orden.
    * Grupos de seguridad Usuario / Responsable.
""",
    'author': 'Lucas Riveros',
    'website': 'https://github.com/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/rental_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'wizard/rental_return_wizard_views.xml',
        'views/rental_equipment_views.xml',
        'views/rental_order_views.xml',
        'views/res_partner_views.xml',
        'report/rental_report.xml',
        'report/rental_contract_templates.xml',
        'views/rental_menus.xml',
    ],
    'demo': [
        'demo/rental_demo.xml',
        'demo/rental_demo_user.xml',
    ],
    'application': True,
    'installable': True,
}
