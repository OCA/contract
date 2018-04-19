import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-contract_account_banking_mandate',
        'odoo8-addon-contract_discount',
        'odoo8-addon-contract_invoice_merge_by_partner',
        'odoo8-addon-contract_journal',
        'odoo8-addon-contract_payment_mode',
        'odoo8-addon-contract_recurring_invoicing_marker',
        'odoo8-addon-contract_recurring_invoicing_monthly_last_day',
        'odoo8-addon-contract_recurring_plans',
        'odoo8-addon-contract_show_invoice',
        'odoo8-addon-contract_show_recurring_invoice',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
