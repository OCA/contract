from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "contract", "migrations/15.0.1.0.0/noupdate_changes.xml"
    )
    openupgrade.delete_record_translations(
        env.cr,
        "contract",
        [
            "email_contract_template",
            "mail_template_contract_modification",
            "mail_notification_contract",
        ],
    )
