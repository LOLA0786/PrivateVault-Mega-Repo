"""
Example: Retrieve secrets from Vault (no OpenAI SDK dependency)
"""

from security.secrets.secrets_manager import SecretsManager


def main():
    secrets = SecretsManager()

    openai_secret = secrets.get_secret("openai/api_key")
    if not openai_secret:
        print("❌ Secret not found: openai/api_key")
        return

    api_key = openai_secret["data"]["data"].get("api_key")
    if not api_key:
        print("❌ api_key field missing")
        return

    print("✅ Retrieved OpenAI key from Vault:", api_key[:6] + "...")


if __name__ == "__main__":
    main()
