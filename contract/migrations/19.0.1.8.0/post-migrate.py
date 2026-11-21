# Copyright 2026 OCA - bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # note went from Text to Html: wrap the existing plain text so its line
    # breaks survive.
    openupgrade.convert_field_to_html(env.cr, "contract_contract", "note", "note")
