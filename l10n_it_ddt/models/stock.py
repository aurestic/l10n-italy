# -*- coding: utf-8 -*-
# Copyright 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
# @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
# Copyright 2015-2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    ddt_ids = fields.Many2many(
        comodel_name='stock.picking.package.preparation',
        relation='stock_picking_pack_prepare_rel',
        column1='stock_picking_id',
        column2='stock_picking_package_preparation_id',
        string='DdT',
        copy=False, )

    @api.multi
    def write(self, values):
        pack_to_update = None
        if 'move_lines' in values:
            pack_to_update = self.env['stock.picking.package.preparation']
            for picking in self:
                pack_to_update |= picking.ddt_ids
        res = super(StockPicking, self).write(values)
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res

    @api.multi
    def unlink(self):
        pack_to_update = self.env['stock.picking.package.preparation']
        for picking in self:
            pack_to_update |= picking.ddt_ids
        res = super(StockPicking, self).unlink()
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        if picking.ddt_ids:
            picking.ddt_ids._update_line_ids()
        return picking

    def get_ddt_shipping_partner(self):
        # this is mainly used in dropshipping configuration,
        # where self.partner_id is your supplier, but 'move_lines.partner_id'
        # is your customer
        move_partners = self.mapped('move_lines.partner_id')
        if len(move_partners) == 1:
            return move_partners[0]
        else:
            return self.partner_id
