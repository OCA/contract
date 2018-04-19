import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-agreement_account',
        'odoo10-addon-agreement_sale',
        'odoo10-addon-contract',
        'odoo10-addon-contract_digitized_signature',
        'odoo10-addon-contract_payment_auto',
        'odoo10-addon-contract_payment_mode',
        'odoo10-addon-contract_recurring_analytic_distribution',
        'odoo10-addon-contract_sale',
        'odoo10-addon-contract_sale_generation',
        'odoo10-addon-contract_show_invoice',
        'odoo10-addon-contract_variable_quantity',
        'odoo10-addon-product_contract',
        'odoo10-addon-website_portal_contract',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
