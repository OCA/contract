import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-agreement_rebate_partner_company_group>=16.0dev,<16.1dev',
        'odoo-addon-contract>=16.0dev,<16.1dev',
        'odoo-addon-contract_invoice_start_end_dates>=16.0dev,<16.1dev',
        'odoo-addon-contract_payment_mode>=16.0dev,<16.1dev',
        'odoo-addon-contract_sale>=16.0dev,<16.1dev',
        'odoo-addon-contract_sale_generation>=16.0dev,<16.1dev',
        'odoo-addon-contract_variable_quantity>=16.0dev,<16.1dev',
        'odoo-addon-subscription_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
