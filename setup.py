from setuptools import find_packages, setup

setup(
    name="GeekChat",
    description="GeekChat",
    version="0.0.2",
    install_requires=["click>=7.0,<8.0",
                      "PyQt5>=5.0,<6.0",
                      "SQLAlchemy>=1.2,<2.0",
                      "bcrypt>=3.0,<4.0",
                      "pycryptodome>=3.0,<4.0",
                      "structlog>=20.0,<22.0"
                      ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "start_client=GeekChat.chat_client:start",
            "start_server=GeekChat.chat_server:start",
        ]
    },
)
