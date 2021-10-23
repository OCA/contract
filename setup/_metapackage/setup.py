import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-agreement',
        'odoo14-addon-agreement_legal',
        'odoo14-addon-agreement_maintenance',
        'odoo14-addon-agreement_mrp',
        'odoo14-addon-agreement_project',
        'odoo14-addon-agreement_sale',
        'odoo14-addon-agreement_serviceprofile',
        'odoo14-addon-agreement_stock',
        'odoo14-addon-contract',
        'odoo14-addon-contract_mandate',
        'odoo14-addon-contract_payment_mode',
        'odoo14-addon-contract_sale',
        'odoo14-addon-contract_variable_quantity',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
