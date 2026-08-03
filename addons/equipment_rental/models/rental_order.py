from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RentalOrder(models.Model):
    _name = 'rental.order'
    _description = 'Orden de Alquiler'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: ('Nuevo'),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
    )
    date_start = fields.Date(
        string='Fecha inicio',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    date_end = fields.Date(
        string='Fecha fin (prevista)',
        required=True,
        tracking=True,
    )
    return_date = fields.Date(
        string='Fecha devolución real', readonly=True, copy=False)
    duration_days = fields.Integer(
        string='Días', compute='_compute_duration_days', store=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('ongoing', 'En curso'),
            ('returned', 'Devuelto'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )
    rental_line_ids = fields.One2many(
        'rental.order.line', 'order_id', string='Líneas', copy=True)
    note = fields.Text(string='Notas')

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Compañía',
        default=lambda self: self.env.company, required=True)
    amount_total = fields.Monetary(
        string='Total',
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True,
        tracking=True,
    )

    invoice_id = fields.Many2one(
        'account.move', string='Factura', readonly=True, copy=False)
    invoice_count = fields.Integer(
        string='Nº facturas', compute='_compute_invoice_count')

    # ------------------------------------------------------------------
    # Cálculos
    # ------------------------------------------------------------------
    @api.depends('date_start', 'date_end')
    def _compute_duration_days(self):
        for order in self:
            if order.date_start and order.date_end:
                delta = (order.date_end - order.date_start).days
                # Alquiler mínimo de 1 día (mismo día = 1 día).
                order.duration_days = max(delta, 1)
            else:
                order.duration_days = 0

    @api.depends('rental_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.rental_line_ids.mapped('price_subtotal'))

    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = 1 if order.invoice_id else 0

    # ------------------------------------------------------------------
    # Restricciones de negocio
    # ------------------------------------------------------------------
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for order in self:
            if order.date_start and order.date_end and order.date_end < order.date_start:
                raise ValidationError(
                    "La fecha de fin no puede ser anterior a la fecha de inicio.")

    @api.constrains('date_start', 'date_end', 'rental_line_ids', 'state')
    def _check_equipment_availability(self):
        """Impide que un mismo equipo se alquile en fechas solapadas."""
        for order in self:
            if order.state in ('draft', 'cancelled', 'returned'):
                continue
            for line in order.rental_line_ids:
                equipment = line.equipment_id
                if equipment.status == 'maintenance':
                    raise ValidationError(
                        "El equipo '%s' está en mantenimiento y no puede alquilarse."
                        % equipment.display_name)
                # Buscar otras órdenes activas con el mismo equipo y fechas solapadas.
                overlapping = self.env['rental.order.line'].search([
                    ('equipment_id', '=', equipment.id),
                    ('order_id', '!=', order.id),
                    ('order_id.state', 'in', ('confirmed', 'ongoing')),
                    ('order_id.date_start', '<=', order.date_end),
                    ('order_id.date_end', '>=', order.date_start),
                ], limit=1)
                if overlapping:
                    raise ValidationError(
                        "El equipo '%s' ya está reservado entre %s y %s "
                        "(orden %s)." % (
                            equipment.display_name,
                            overlapping.order_id.date_start,
                            overlapping.order_id.date_end,
                            overlapping.order_id.name,
                        ))

    # ------------------------------------------------------------------
    # Creación / secuencia
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'rental.order') or 'Nuevo'
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Acciones de flujo
    # ------------------------------------------------------------------
    def action_confirm(self):
        for order in self:
            if not order.rental_line_ids:
                raise UserError(
                    "No puedes confirmar una orden sin líneas de alquiler.")
            order.state = 'confirmed'

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_open_return_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar devolución',
            'res_model': 'rental.return.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise UserError("Esta orden ya tiene una factura asociada.")
        if not self.rental_line_ids:
            raise UserError("No hay líneas para facturar.")
        invoice_lines = []
        for line in self.rental_line_ids:
            invoice_lines.append((0, 0, {
                'name': "Alquiler %s (%s días)" % (
                    line.equipment_id.display_name, self.duration_days),
                'quantity': line.quantity * self.duration_days,
                'price_unit': line.unit_price,
            }))
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        })
        self.invoice_id = invoice.id
        return self.action_view_invoice()

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factura',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }

    # ------------------------------------------------------------------
    # Acción programada (cron)
    # ------------------------------------------------------------------
    @api.model
    def _cron_check_overdue_rentals(self):
        """Marca actividad en las órdenes en curso cuya fecha de fin ya pasó."""
        today = fields.Date.context_today(self)
        overdue = self.search([
            ('state', '=', 'ongoing'),
            ('date_end', '<', today),
            ('return_date', '=', False),
        ])
        for order in overdue:
            order.activity_schedule(
                'mail.mail_activity_data_todo',
                summary="Alquiler vencido sin devolver",
                note="La orden %s debía devolverse el %s y sigue en curso." % (
                    order.name, order.date_end),
                user_id=order.create_uid.id,
            )
        return True
