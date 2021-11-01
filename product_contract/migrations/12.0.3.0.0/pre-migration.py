from odoo.tools import parse_version


def migrate(cr, version):
    if parse_version(version) == parse_version('12.0.2.0.0'):
        # pre-paid/post-paid becomes significant for monthlylastday too,
        # make sure it has the value that was implied for previous versions.
        cr.execute(
            """\
                UPDATE product_template
                SET recurring_invoicing_type = 'post-paid'
                WHERE recurring_rule_type = 'monthlylastday'
            """
        )
