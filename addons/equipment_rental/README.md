# Equipment Rental — Módulo Odoo 19

Módulo de gestión de **alquiler de equipos por días** desarrollado desde cero para
Odoo 19. Pensado como pieza de portfolio: cubre de forma realista los patrones
habituales del desarrollo Odoo.

> Autor: Lucas Riveros · Licencia: LGPL-3

---

## ¿Qué hace?

Una empresa alquila equipos (herramientas, maquinaria, electrónica…) a clientes
durante un número de días. El módulo permite:

- Mantener un **catálogo de equipos** con tarifa diaria, foto y estado operativo.
- Crear **órdenes de alquiler** con varias líneas, calculando días e importe total
  automáticamente.
- **Impedir la doble reserva**: un equipo no puede alquilarse en fechas que se
  solapan con otra orden activa.
- Gestionar el ciclo de vida: `Borrador → Confirmado → En curso → Devuelto`
  (o `Cancelado`).
- Registrar la **devolución** mediante un asistente, con **recargo por retraso**.
- Generar el **contrato de alquiler en PDF**.
- **Facturar** la orden (crea una factura de cliente de Contabilidad).
- Recibir un **aviso automático diario** de las devoluciones vencidas (cron).
- Ver la operación en **calendario** y analizarla con **tablas dinámicas y gráficos**.

---

## Conceptos de Odoo demostrados

| Área | Dónde |
|------|-------|
| ORM: modelos, relaciones `One2many`/`Many2one` | `models/` |
| Campos **calculados** con `@api.depends` (almacenados y no) | `rental_order.py`, `rental_order_line.py` |
| **Restricciones** de negocio `@api.constrains` (solapamiento de fechas) | `rental_order.py` |
| Campos **relacionados** y `@api.onchange` | `rental_order_line.py` |
| **Herencia** de modelo existente (`res.partner`) | `models/res_partner.py` |
| **Wizard** (`TransientModel`) | `wizard/rental_return_wizard.py` |
| **Secuencias** para numeración automática | `data/ir_sequence_data.xml` |
| **Acción programada** (`ir.cron`) | `data/ir_cron_data.xml` |
| Vistas: **form, list, kanban, search, calendar, pivot, graph** | `views/` |
| **Statusbar** con botones de flujo | `views/rental_order_views.xml` |
| **Smart buttons** (facturas, nº de alquileres) | `views/`, `res_partner_views.xml` |
| **Reporte QWeb PDF** | `report/` |
| **Seguridad**: grupos (`res.groups.privilege`), ACL y *record rules* | `security/` |
| **Integración** con Contabilidad (`account.move`) | `rental_order.py` |
| **Datos demo** | `demo/rental_demo.xml` |
| Chatter / actividades (`mail.thread`, `mail.activity.mixin`) | modelos + `<chatter/>` |

> Nota técnica: escrito para las novedades de Odoo 19 — etiqueta `<list>` (antes
> `<tree>`), atributos `invisible/readonly` con expresiones Python (sin `attrs`),
> `<chatter/>`, y el nuevo modelo `res.groups.privilege` para categorizar grupos.

---

## Instalación

Requiere una instancia de Odoo 19 con el módulo `account` disponible.

1. Copia la carpeta `equipment_rental` dentro de tu `addons_path`.
2. Reinicia Odoo y actualiza la lista de aplicaciones.
3. Instala **Equipment Rental** desde Aplicaciones.

Con Docker (ver `docker-compose.yml` en la raíz del repositorio):

```bash
docker compose up -d
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf \
    -d rental -i equipment_rental --with-demo --stop-after-init
```

Accede en <http://localhost:8069> (usuario/clave demo: `admin` / `admin`).

---

## Estructura

```
equipment_rental/
├── models/          # rental.equipment, rental.order, rental.order.line, res.partner
├── wizard/          # asistente de devolución
├── views/           # vistas y menús
├── report/          # acción de informe + plantilla QWeb del contrato
├── security/        # grupos, privilegios, ACL y record rules
├── data/            # secuencias y cron
├── demo/            # datos de demostración
└── static/description/
```
