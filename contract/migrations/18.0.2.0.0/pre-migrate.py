# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
    DELETE FROM ir_model
    WHERE model IN
        ('contract.abstract.contract',
        'contract.abstract.contract.line',
        'contract.recurrency.mixin',
        'contract.recurrency.basic.mixin'
    );
    """
    )
    views_to_delete = ["contract.contract_template_line_form_view"]
    openupgrade.delete_records_safely_by_xml_id(env, views_to_delete, True)
    all_moved_fields = {
        "contract_line_successor": {
            "contract.line": [
                "termination_notice_date",
                "successor_contract_line_id",
                "predecessor_contract_line_id",
                "manual_renew_needed",
                "is_plan_successor_allowed",
                "is_stop_plan_successor_allowed",
                "is_stop_allowed",
                "is_cancel_allowed",
                "is_un_cancel_allowed",
                "state",
                "is_auto_renew",
                "auto_renew_interval",
                "auto_renew_rule_type",
                "termination_notice_interval",
                "termination_notice_rule_type",
            ],
            "contract.template.line": [
                "is_auto_renew",
                "auto_renew_interval",
                "auto_renew_rule_type",
                "termination_notice_interval",
                "termination_notice_rule_type",
            ],
        },
        "contract_termination": {
            "contract.contract": [
                "is_terminated",
                "terminate_reason_id",
                "terminate_comment",
                "terminate_date",
            ]
        },
    }
    for module_name, moved_fields_by_model in all_moved_fields.items():
        for model_name, moved_fields in moved_fields_by_model.items():
            openupgrade.update_module_moved_fields(
                env.cr, model_name, moved_fields, "contract", module_name
            )
    all_moved_models = {
        "contract_line_successor": ["contract.line.wizard"],
        "contract_termination": [
            "contract.terminate.reason",
            "contract.contract.terminate",
        ],
    }
    for new_module, moved_models in all_moved_models.items():
        for moved_model in moved_models:
            openupgrade.update_module_moved_models(
                env.cr, moved_model, "contract", new_module
            )
    all_moved_xml_ids = {
        "contract_line_successor": [
            "contract_line_wizard",
            "contract_line_cron_for_renew",
        ],
        "contract_termination": [
            "contract_terminate_reason_access_manager",
            "contract_terminate_reason_access_user",
            "can_terminate_contract",
            "contract_contract_terminate_wizard",
        ],
    }
    xmlids_spec = []
    for new_module, moved_xml_ids in all_moved_xml_ids.items():
        xmlids_spec.extend(
            [
                (f"contract.{xml_id}", f"{new_module}.{xml_id}")
                for xml_id in moved_xml_ids
            ]
        )
    openupgrade.rename_xmlids(env.cr, xmlids_spec=xmlids_spec)
