import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-contract>=15.0dev,<15.1dev',
        'odoo-addon-contract_payment_mode>=15.0dev,<15.1dev',
        'odoo-addon-contract_sale>=15.0dev,<15.1dev',
        'odoo-addon-contract_sale_generation>=15.0dev,<15.1dev',
        'odoo-addon-contract_variable_quantity>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
