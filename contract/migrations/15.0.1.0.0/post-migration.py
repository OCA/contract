from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "contract", "migrations/15.0.1.0.0/noupdate_changes.xml"
    )
    xml_ids = [
        "email_contract_template",
        "mail_template_contract_modification",
        "mail_notification_contract",
    ]
    for xml_id in xml_ids:
        if env.ref(f"contract.{xml_id}", raise_if_not_found=False):
            xml_ids.remove("xml_id")
    if xml_ids:
        openupgrade.delete_record_translations(
            env.cr,
            "contract",
            xml_ids,
        )
