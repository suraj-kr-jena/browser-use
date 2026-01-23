from boto3.session import Session
import json
from typing import Dict, Any


class GetSecret:
    """
    Helper to fetch JSON secrets from AWS Secrets Manager.

    Usage:
        gs = GetSecret(region_name="us-east-1")
        creds = gs.get_secret("my/secret/name")  # -> dict
    """

    def __init__(self, region_name: str = "us-east-1"):
        self._client = Session(profile_name="mlops", region_name=region_name).client("secretsmanager")

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Fetch a secret by name and return it as a dict.
        Expects the stored secret to be a JSON string.

        :param secret_name: The Secrets Manager secret name or ARN.
        :return: Parsed JSON as a dictionary.
        :raises RuntimeError: If the secret retrieval fails.
        :raises ValueError: If the secret isn't a JSON string.
        """
        try:
            resp = self._client.get_secret_value(SecretId=secret_name)
        except Exception as e:
            raise RuntimeError(f"Error fetching secret '{secret_name}': {e}") from e

        if "SecretString" not in resp:
            raise ValueError(f"Secret '{secret_name}' is binary or missing SecretString; JSON expected.")

        try:
            return json.loads(resp["SecretString"])
        except json.JSONDecodeError as e:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON: {e}") from e
