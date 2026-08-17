CAPIF_SDK_CONFIG_PATH = "app/capif/capif_sdk_config.json"

# CAPIF apiName each provider publishes its service APIs under. The name is
# extracted by the SDK's api_schema_translator from the published base url
# (<apiRoot>/<apiName>/v<version>), so it cannot be chosen freely:
#   NEF emulator     -> https://<host>:<port>/nef/api/v1        -> "api"
#   GSMA Open Gateway-> <gateway_public_url>/gsma-open-gateway/v1 -> "gsma-open-gateway"
NEF_CAPIF_API_NAME = "api"
CAMARA_CAPIF_API_NAME = "gsma-open-gateway"
