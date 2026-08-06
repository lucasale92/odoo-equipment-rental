# Odoo 19 · Equipment Rental

Módulo personalizado de **gestión de alquiler de equipos por días** para Odoo 19,
desarrollado desde cero como pieza de portfolio.

Una empresa alquila equipos (herramientas, maquinaria, electrónica…) a clientes por
un número de días. El módulo cubre el ciclo completo: catálogo, reserva con control
de disponibilidad, contrato PDF y facturación.

## Demo en vivo

**https://163-176-66-200.sslip.io**

- Usuario: `admin`
- Contraseña: `admin`

(Instancia de demostración con datos ficticios, sin garantía de disponibilidad continua.)

## Funcionalidades

- Catálogo de equipos con tarifa diaria, foto y estado (vista **kanban**).
- Órdenes de alquiler con líneas y cálculo automático de días e importe.
- **Control de disponibilidad**: impide la doble reserva en fechas solapadas.
- Flujo de estados: `Borrador → Confirmado → En curso → Devuelto`.
- Vista **calendario** de reservas y análisis con **pivot/graph**.
- **Asistente de devolución** con recargo por retraso.
- **Contrato de alquiler en PDF** (QWeb) — ver [ejemplo](docs/contrato_demo.pdf).
- **Aviso automático** de devoluciones vencidas (`ir.cron`).
- **Facturación** integrada (crea la factura de cliente).
- Grupos de seguridad Usuario / Responsable.

## Conceptos de Odoo demostrados

Modelos y ORM · campos *computed*/*related* · `@api.constrains` (solapamiento) ·
herencia de `res.partner` · wizard (`TransientModel`) · secuencias · `ir.cron` ·
7 tipos de vista (form, list, kanban, search, calendar, pivot, graph) · statusbar ·
smart buttons · reporte QWeb PDF · seguridad (grupos + record rules) · datos demo.

Escrito con la sintaxis de **Odoo 19** (`<list>`, `res.groups.privilege`,
`<chatter/>`, expresiones `invisible/readonly`).

## Cómo ejecutarlo (Docker)

Requiere Docker. Levanta Odoo 19 (imagen oficial) + PostgreSQL:

```bash
docker compose up -d
```

Luego abrí <http://localhost:8069>, creá una base de datos e instalá la app
**Equipment Rental** desde el menú Aplicaciones (actualizá la lista de apps si no
aparece). El módulo vive en `addons/equipment_rental`.

Para instalarlo con datos de demostración desde la línea de comandos:

```bash
docker compose exec odoo odoo -d rental -i equipment_rental --with-demo -c /etc/odoo/odoo.conf --stop-after-init
docker compose restart odoo
```

## Estructura

```
addons/equipment_rental/
├── models/      # equipos, órdenes, líneas, res.partner
├── wizard/      # asistente de devolución
├── views/       # vistas y menús
├── report/      # contrato QWeb
├── security/    # grupos, ACL, record rules
├── data/        # secuencias y cron
└── demo/        # datos demo
```

## Licencia

LGPL-3.
