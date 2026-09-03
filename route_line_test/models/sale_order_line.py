##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    route_company_id = fields.Many2one(
        "res.company",
        string="Compania de la ruta",
        compute="_compute_route_company_id",
        store=True,
        help="Compania de la ruta de la linea, cacheada en la linea.",
    )

    @api.depends("route_id")
    def _compute_route_company_id(self):
        for line in self:
            line.route_company_id = line.route_id.company_id
