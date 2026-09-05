# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Split the legacy ``invoicing_mode`` selection into orthogonal fields.

    Old ``invoicing_mode`` values map to the new fields as follows:

    ===================  =================  ==============  ==============
    invoicing_mode       create_sale_order  invoice_state   send_invoice
    ===================  =================  ==============  ==============
    draft                False              draft           False
    invoice              False              posted          False
    invoice_send         False              posted          True
    sale_and_invoice     True               posted          False
    ===================  =================  ==============  ==============
    """
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'sale_subscription_template' "
        "AND column_name = 'invoicing_mode'"
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE sale_subscription_template
        SET create_sale_order = (invoicing_mode = 'sale_and_invoice'),
            invoice_state = CASE
                WHEN invoicing_mode IN ('invoice', 'invoice_send', 'sale_and_invoice')
                THEN 'posted' ELSE 'draft' END,
            send_invoice = (invoicing_mode = 'invoice_send')
        """
    )
    cr.execute(
        "ALTER TABLE sale_subscription_template DROP COLUMN IF EXISTS invoicing_mode"
    )
