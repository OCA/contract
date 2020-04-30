# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Convert contract_template_id field of the product_template table
    # to a company dependent field
    model_name = "product.template"
    model_table_name = "product_template"
    origin_field_name = "contract_template_id"
    destination_field_name = "property_contract_template_id"
    # Add ir.model.fields entry
    env.cr.execute(
        "SELECT id FROM ir_model WHERE model = %s", (model_name, ),
    )
    model_id = env.cr.fetchone()[0]
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO ir_model_fields (
            model_id, model, name, field_description, ttype, state, relation
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )""",
        (model_id, model_name, destination_field_name, 'OU', "many2one",
            'base', 'contract.template'),
    )
    openupgrade.convert_to_company_dependent(
        env,
        model_name,
        origin_field_name,
        destination_field_name,
        model_table_name,
    )
