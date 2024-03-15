from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_to_company_dependent(
        env,
        "product.template",
        "old_subscription_template_id",
        "subscription_template_id",
    )
    openupgrade.drop_columns(
        env.cr, [("product_template", "old_subscription_template_id")]
    )
