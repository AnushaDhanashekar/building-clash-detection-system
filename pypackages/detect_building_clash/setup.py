import setuptools

setuptools.setup(
    name="detect-building-clash",
    version="0.0.1",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        # Do not allow black to put these on one line. It seems Renovate has
        # trouble updating this if it goes in one line.
        # fmt: off
        "boto3==1.35.88",
        "python-dateutil==2.9.0.post0",
        "typing-extensions==4.12.2",
        "common==0.0.1"
        # fmt: on
    ],
)
