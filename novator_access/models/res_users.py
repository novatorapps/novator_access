from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    nacc_profile_ids = fields.Many2many('nacc.profile', 'nacc_profile_user_rel', 'user_id', 'profile_id',
                                        string='Access Profiles')

    def write(self, vals):
        res = super().write(vals)
        if 'nacc_profile_ids' in vals or 'groups_id' in vals or 'company_ids' in vals:
            self.env['nacc.profile']._nacc_clear()
        return res

    @api.model
    def has_group(self, group_ext_id):
        # the web client asks this before showing Export
        if group_ext_id == 'base.group_allow_export' and (not self or self.id == self.env.uid):
            if any(self.env['nacc.profile']._nacc_current().mapped('hide_export')):
                return False
        return super().has_group(group_ext_id)
