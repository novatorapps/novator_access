from odoo import _, api, fields, models, release, tools

PRO_URL = 'https://apps.odoo.com/apps/modules/%s.0/novator_access_pro'


class AccessProfile(models.Model):
    """A set of restrictions for some users. A user can have several profiles: restrictions add up."""
    _name = 'nacc.profile'
    _description = 'Access Profile'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    user_ids = fields.Many2many('res.users', 'nacc_profile_user_rel', 'profile_id', 'user_id', string='Users',
                                domain=[('share', '=', False)])
    company_ids = fields.Many2many('res.company', string='Only in Companies',
                                   help='Leave empty to apply in every company.')
    note = fields.Text()
    hide_menu_ids = fields.Many2many('ir.ui.menu', 'nacc_profile_menu_rel', 'profile_id', 'menu_id',
                                     string='Hidden Menus', help='Sub-menus of a hidden menu are hidden too.')
    read_only = fields.Boolean('Read-Only User', help='Users can look at everything they may see, but cannot '
                                                      'create, change or delete anything.')
    disable_debug = fields.Boolean('No Developer Mode')
    hide_import = fields.Boolean('No Import')
    hide_export = fields.Boolean('No Export')
    user_count = fields.Integer(compute='_compute_user_count', string='Users ')
    pro_installed = fields.Boolean(compute='_compute_pro_installed')

    def _compute_user_count(self):
        for profile in self:
            profile.user_count = len(profile.user_ids)

    def _compute_pro_installed(self):
        installed = bool(self.env['ir.module.module'].sudo().search(
            [('name', '=', 'novator_access_pro'), ('state', '=', 'installed')], limit=1))
        for profile in self:
            profile.pro_installed = installed

    # ------------------------------------------------------------------ cache
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._nacc_clear()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._nacc_clear()
        return res

    def unlink(self):
        res = super().unlink()
        self._nacc_clear()
        return res

    @api.model
    def _nacc_clear(self):
        self.env.registry.clear_cache()
        self.env.registry.clear_cache('templates')

    @api.model
    @tools.ormcache('uid', 'company_id')
    def _nacc_profile_ids(self, uid, company_id):
        """Active profiles of a user in a company, as a tuple of (id, write_date) for cache keys."""
        user = self.env['res.users'].sudo().browse(uid)
        if not user.exists() or uid == 1 or user._is_superuser() or user.has_group('base.group_system'):
            return ()
        profiles = self.sudo().search([('user_ids', 'in', uid), ('active', '=', True)])
        profiles = profiles.filtered(lambda p: not p.company_ids or company_id in p.company_ids.ids)
        return tuple((p.id, str(p.write_date)) for p in profiles)

    @api.model
    def _nacc_current(self):
        """Profiles of the current user (sudo recordset). Administrators and superuser: none."""
        if self.env.su:
            return self.sudo().browse()
        ids = self._nacc_profile_ids(self.env.uid, self.env.company.id)
        return self.sudo().browse([i for i, _w in ids])

    @api.model
    def _nacc_signature(self):
        if self.env.su:
            return ()
        return self._nacc_profile_ids(self.env.uid, self.env.company.id)

    # ------------------------------------------------------------------ ui
    def action_pro(self):
        return {'type': 'ir.actions.act_url', 'target': 'new', 'url': PRO_URL % release.version_info[0]}
