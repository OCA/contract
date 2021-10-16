import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-contract',
        'odoo9-addon-contract_digitized_signature',
        'odoo9-addon-contract_invoice_merge_by_partner',
        'odoo9-addon-contract_mandate',
        'odoo9-addon-contract_payment_mode',
        'odoo9-addon-contract_recurring_analytic_distribution',
        'odoo9-addon-contract_show_invoice',
        'odoo9-addon-contract_variable_quantity',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
