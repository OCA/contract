def migrate(cr, version):
    cr.execute(
        """\
            UPDATE res_company
            SET create_new_line_at_contract_line_renew = true
        """
    )
