import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-agreement',
        'odoo12-addon-agreement_legal',
        'odoo12-addon-agreement_legal_sale',
        'odoo12-addon-agreement_maintenance',
        'odoo12-addon-agreement_mrp',
        'odoo12-addon-agreement_project',
        'odoo12-addon-agreement_repair',
        'odoo12-addon-agreement_sale',
        'odoo12-addon-agreement_serviceprofile',
        'odoo12-addon-agreement_stock',
        'odoo12-addon-contract',
        'odoo12-addon-contract_mandate',
        'odoo12-addon-contract_payment_mode',
        'odoo12-addon-contract_sale',
        'odoo12-addon-contract_sale_invoicing',
        'odoo12-addon-contract_sale_mandate',
        'odoo12-addon-contract_sale_payment_mode',
        'odoo12-addon-contract_variable_quantity',
        'odoo12-addon-product_contract',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
