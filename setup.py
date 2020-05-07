import setuptools


with open("readme.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="singo",
    version="0.0.1",

    description="the API for a community web server",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Bernard Paques",

    package_dir={"": "singo"},
    packages=setuptools.find_packages(where="singo"),

    install_requires=[
        "bcrypt",
        "boto3",
        "Flask",
        "flask-classful",
        "flask-cors",
        "pyjwt",
        "pyyaml",
        "shortuuid",
    ],

    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",

        "Topic :: Utilities",

    ],
)
