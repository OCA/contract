from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {
            "product_template": [
                ("subscription_template_id", "old_subscription_template_id", None)
            ]
        },
    )
