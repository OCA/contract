from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "contract", "migrations/15.0.1.0.0/noupdate_changes.xml"
    )
    xml_ids = ["email_contract_template", "mail_template_contract_modification"]
    if env.ref("mail.mail_notification_paynow", raise_if_not_found=False):
        xml_ids.append("mail_notification_contract")
    openupgrade.delete_record_translations(
        env.cr,
        "contract",
        xml_ids,
    )
