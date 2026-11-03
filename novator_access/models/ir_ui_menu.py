from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _visible_menu_ids(self, debug=False):
        visible = super()._visible_menu_ids(debug)
        profiles = self.env['nacc.profile']._nacc_current()
        hidden = profiles.mapped('hide_menu_ids')
        if not hidden:
            return visible
        hidden_ids = set(self.sudo().search([('id', 'child_of', hidden.ids)]).ids)
        return frozenset(visible) - hidden_ids
