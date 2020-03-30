from openupgradelib import openupgrade

def migrate(cr, version):
    # pre-paid/post-paid becomes significant for monthlylastday too,
    # make sure it has the value that was implied for previous versions.
    if openupgrade.column_exists(cr, 'product_template', 'recurring_invoicing_type'):
        cr.execute(
            """\
                UPDATE product_template
                SET recurring_invoicing_type = 'post-paid'
                WHERE recurring_rule_type = 'monthlylastday'
            """
        )
