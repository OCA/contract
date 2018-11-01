import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-agreement',
        'odoo11-addon-agreement_maintenance',
        'odoo11-addon-contract',
        'odoo11-addon-contract_payment_mode',
        'odoo11-addon-contract_sale',
        'odoo11-addon-contract_sale_invoicing',
        'odoo11-addon-contract_section',
        'odoo11-addon-contract_variable_qty_timesheet',
        'odoo11-addon-contract_variable_quantity',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
