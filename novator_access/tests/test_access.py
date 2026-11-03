from odoo import release
from odoo.exceptions import AccessError, UserError
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestAccess(HttpCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Restricted User', 'login': 'nacc_user', 'password': 'nacc_user_123',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('base.group_partner_manager').id,
                                  self.env.ref('base.group_allow_export').id])],
        })
        self.profile = self.env['nacc.profile'].create({'name': 'Test profile', 'user_ids': [(6, 0, self.user.ids)]})
        self.Partner = self.env['res.partner'].with_user(self.user)

    def test_01_read_only(self):
        self.Partner.create({'name': 'Allowed before'})
        self.profile.read_only = True
        with self.assertRaises(AccessError):
            self.Partner.create({'name': 'Blocked'})
        partner = self.env['res.partner'].create({'name': 'Existing'})
        with self.assertRaises(AccessError):
            partner.with_user(self.user).write({'name': 'Changed'})
        self.assertTrue(self.Partner.search([('id', '=', partner.id)]), 'reading still works')
        arch = self.Partner.get_view(view_type='form')['arch']
        self.assertIn('create="0"', arch)
        # administrators are never restricted
        self.profile.user_ids = [(4, self.env.ref('base.user_admin').id)]
        self.env['res.partner'].with_user(self.env.ref('base.user_admin')).create({'name': 'Admin can'})

    def test_02_export_import(self):
        self.assertTrue(self.user.with_user(self.user).has_group('base.group_allow_export'))
        self.profile.write({'hide_export': True, 'hide_import': True})
        self.assertFalse(self.user.with_user(self.user).has_group('base.group_allow_export'))
        with self.assertRaises(UserError):
            self.Partner.search([], limit=1).export_data(['name'])
        with self.assertRaises(UserError):
            self.Partner.load(['name'], [['Imported']])
        arch = self.Partner.get_view(view_type='list')['arch']
        self.assertIn('import="0"', arch)
        # the way the web client asks
        self.authenticate('nacc_user', 'nacc_user_123')
        args = ['base.group_allow_export'] if release.version_info[0] < 18 else [[self.user.id], 'base.group_allow_export']
        res = self.make_jsonrpc_request('/web/dataset/call_kw/res.users/has_group', {
            'model': 'res.users', 'method': 'has_group', 'args': args, 'kwargs': {}})
        self.assertFalse(res)

    def test_03_menus(self):
        contacts = self.env.ref('base.menu_administration')
        menu = self.env['ir.ui.menu'].search([('parent_id', '=', False), ('id', '!=', contacts.id)], limit=1)
        child = self.env['ir.ui.menu'].create({'name': 'Child', 'parent_id': menu.id})
        Menu = self.env['ir.ui.menu'].with_user(self.user)
        self.profile.hide_menu_ids = [(6, 0, menu.ids)]
        visible = Menu._visible_menu_ids()
        self.assertNotIn(menu.id, visible)
        self.assertNotIn(child.id, visible)

    def test_04_company_scope(self):
        other = self.env['res.company'].create({'name': 'Other Co'})
        self.profile.write({'read_only': True, 'company_ids': [(6, 0, other.ids)]})
        self.Partner.create({'name': 'Not restricted here'})

    def _store(self):
        try:
            from odoo.http import root
            return root.session_store
        except ImportError:
            from odoo.http.session import session_store
            return session_store()

    def test_05_debug(self):
        self.profile.disable_debug = True
        session = self.authenticate('nacc_user', 'nacc_user_123')
        self.url_open('/web?debug=1')
        self.assertFalse(self._store().get(session.sid).debug)
        self.profile.disable_debug = False
        self.url_open('/web?debug=1')
        self.assertTrue(self._store().get(session.sid).debug)
