def migrate(cr, version):
    # pre-paid/post-paid becomes significant for monthlylastday too,
    # make sure it has the value that was implied for previous versions.
    cr.execute(
        """\
            UPDATE contract_line
            SET recurring_invoicing_type = 'post-paid'
            WHERE recurring_rule_type = 'monthlylastday'
        """
    )
