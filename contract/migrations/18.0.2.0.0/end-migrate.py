# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        SELECT name
        FROM ir_module_module
        WHERE state='uninstalled' AND name IN (
            'contract_line_successor', 'contract_termination');"""
    )
    uninstalled_modules = [x[0] for x in env.cr.fetchall()]
    no_update_xml_ids = {
        "contract_line_successor": [
            "contract_line_cron_for_renew",
        ],
        "contract_termination": [],
    }
    xmlids_spec = []
    for new_module, moved_xml_ids in no_update_xml_ids.items():
        if new_module in uninstalled_modules:
            xmlids_spec.extend([f"{new_module}.{xml_id}" for xml_id in moved_xml_ids])
    if xmlids_spec:
        openupgrade.delete_records_safely_by_xml_id(env, xmlids_spec)
