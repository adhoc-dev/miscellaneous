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

    @api.depends("route_ids")
    def _compute_route_company_id(self):
        for line in self:
            # En 19 la linea puede tener varias rutas: route_id paso a ser
            # route_ids (Many2many, odoo/odoo@b7a9196366eb). El campo cacheado
            # sigue guardando una sola compania, asi que se queda con la de la
            # primera ruta.
            line.route_company_id = line.route_ids[:1].company_id
