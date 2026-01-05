============================================================
GALANI ENTERPRISE EDITION - DEPLOYMENT KIT
============================================================

Thank you for purchasing the Enterprise License (k/yr).

INSTRUCTIONS:
1. We have provided you with a Secure Docker Image: 
   Registry: 209483893123.dkr.ecr.ap-south-1.amazonaws.com/galani-enterprise-secure

2. Your License Key is: LICENSE_HEDGE_FUND_X

3. TO DEPLOY (Run this in your Kubernetes/AWS):

   docker run -d      -e LICENSE_KEY="LICENSE_HEDGE_FUND_X"      -e LICENSE_SERVER="https://license.galani.io/verify"      -p 8080:8080      galani-enterprise-secure

NOTE: This node requires internet access to validate your license on startup.
If payment is not received, the node will fail to boot.

============================================================
Support: emperor@galani.io
============================================================
