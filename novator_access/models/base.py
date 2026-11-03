from odoo import _, api, models
from odoo.exceptions import AccessError, UserError
from odoo.orm.domains import Domain

# models a read-only user may still write to: their own settings, chat, notifications, wizards
READ_ONLY_ALLOWED_PREFIXES = ('bus.', 'mail.', 'discuss.', 'web_tour.', 'res.users.settings', 'res.users.log',
                              'spreadsheet.', 'digest.', 'auth_totp.', 'base.language', 'ir.attachment')


def _read_only_allows(model):
    return model._transient or model._name.startswith(READ_ONLY_ALLOWED_PREFIXES)


class Base(models.AbstractModel):
    _inherit = 'base'

    def _nacc_profiles(self):
        return self.env['nacc.profile']._nacc_current()

    # ------------------------------------------------------------------ rights
    def _nacc_denied(self, operation):
        """Message if the current user's profiles forbid ``operation`` on this model, else False."""
        if operation == 'read' or self.env.su or _read_only_allows(self):
            return False
        profiles = self._nacc_profiles()
        if profiles and any(profiles.mapped('read_only')):
            return _('Your user is read-only: you cannot create, change or delete %s.', self._description)
        return False

    def _access_domain(self, operation):
        if self._nacc_denied(operation):
            return Domain.FALSE
        return super()._access_domain(operation)

    # ------------------------------------------------------------------ import / export
    def export_data(self, fields_to_export):
        if not self.env.su and any(self._nacc_profiles().mapped('hide_export')):
            raise UserError(_('Exporting data is turned off for your user.'))
        return super().export_data(fields_to_export)

    @api.model
    def load(self, fields, data):
        if not self.env.su and any(self._nacc_profiles().mapped('hide_import')):
            raise UserError(_('Importing data is turned off for your user.'))
        return super().load(fields, data)

    # ------------------------------------------------------------------ views
    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (('nacc',) + self.env['nacc.profile']._nacc_signature(),)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        profiles = self._nacc_profiles()
        if profiles:
            self._nacc_postprocess_arch(arch, view_type, profiles)
        return arch, view

    @api.model
    def _nacc_postprocess_arch(self, arch, view_type, profiles):
        """Hook: change the view for the current user's profiles (Pro adds field, button and tab rules)."""
        if view_type in ('tree', 'list', 'kanban') and any(profiles.mapped('hide_import')):
            arch.set('import', '0')
        if any(profiles.mapped('read_only')) and not _read_only_allows(self):
            for attr in ('create', 'edit', 'delete', 'duplicate'):
                arch.set(attr, '0')
        return arch
