from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _handle_debug(cls):
        super()._handle_debug()
        if request.session.debug and request.session.uid and request.env:
            try:
                env = request.env(user=request.session.uid)
                if any(env['nacc.profile']._nacc_current().mapped('disable_debug')):
                    request.session.debug = ''
            except Exception:  # noqa: BLE001 - never break a page because of this check
                pass

    def session_info(self):
        info = super().session_info()
        profiles = self.env['nacc.profile']._nacc_current()
        if any(profiles.mapped('disable_debug')):
            info['debug'] = ''
        return info
