##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    route_company_ids = fields.Many2many(
        "res.company",
        string="Companias de las rutas",
        compute="_compute_route_company_ids",
        store=True,
        help="Companias de las rutas de la linea, cacheadas en la linea.",
    )

    @api.depends("route_ids")
    def _compute_route_company_ids(self):
        for line in self:
            line.route_company_ids = line.route_ids.company_id
