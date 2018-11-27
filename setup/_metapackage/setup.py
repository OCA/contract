import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-contract",
    description="Meta package for oca-contract Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-contract',
        'odoo12-addon-contract_sale',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
