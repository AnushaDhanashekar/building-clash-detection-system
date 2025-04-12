import setuptools

setuptools.setup(
    name="autodesk-cdk",
    version="0.0.1",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        "aws-cdk-lib==2.184.1",
        "aws-cdk.aws-batch-alpha==2.70.0a0",
        "aws-cdk.aws-glue-alpha==2.70.0a0",
        "constructs==10.4.2",
        "boto3==1.35.88",
        "python-dateutil==2.9.0.post0",
        "wb-cicd==0.0.1",
    ],
    python_requires=">=3.6",
)
