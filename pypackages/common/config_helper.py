import os
from typing import Optional, Dict

import boto3

SSM_PREFIX = "ssm://"
SM_PREFIX = "sm://"
DEFAULT_AWS_REGION = "eu-west-1"


def resolve_value(value: str) -> str:
    """
    Values beginning with `ssm://` will be looked up in Parameter Store.
    Values beginning with `sm://` will be looked up in Secrets Manager.

    Examples:
      - `ssm://my-ssm-parameter`
      - `ssm:///my/ssm/parameter` (notice the third slash)

    To be compatibile with https://github.com/telia-oss/aws-env
    """

    if value.startswith(SSM_PREFIX):
        return _get_from_ssm(value[len(SSM_PREFIX) :])

    if value.startswith(SM_PREFIX):
        return _get_from_sm(value[len(SM_PREFIX) :])

    return value

def _get_ssm_client():
    global _ssm_client
    if _ssm_client is None:
        _ssm_client = boto3.client("ssm", region_name=DEFAULT_AWS_REGION)
    return _ssm_client


def _get_sm_client():
    global _sm_client
    if _sm_client is None:
        _sm_client = boto3.client("secretsmanager")
    return _sm_client


def _get_from_ssm(ssm_path: str):
    return _get_ssm_client().get_parameter(Name=ssm_path, WithDecryption=True)[
        "Parameter"
    ]["Value"]


def _get_from_sm(sm_path: str):
    return _get_sm_client().get_secret_value(SecretId=sm_path)["SecretString"]


def resolve_env(name: str, default: str = None, fallback_empty: bool = False) -> str:
    """
    Read the named environment variable and resolve special values. See
    resolve_value for details.
    """

    value = os.environ.get(name)
    if value is None:
        if default is None:
            if fallback_empty:
                return ""
            raise LookupError(f"Env variable {name} missing")
        value = default

    return resolve_value(value)