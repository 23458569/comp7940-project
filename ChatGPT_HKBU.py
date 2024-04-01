import os
#import configparser
import requests
#import logging
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class HKBU_ChatGPT():
#    def __init__(self,config_='./config.ini'):
#        if type(config_) == str:
#            self.config = configparser.ConfigParser()
#            self.config.read(config_)
#        elif type(config_) == configparser.ConfigParser:
#            self.config = config_

    def submit(self,message):
        conversation = [{"role": "user", "content": message}]

        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"

        credential = ClientSecretCredential(
	tenant_id= os.environ["AZURE_TENANT_ID"],
	client_id= os.environ["AZURE_CLIENT_ID"],
	client_secret= os.environ["AZURE_CLIENT_SECRET"]
	)
        client = SecretClient(vault_url=KVUri, credential=credential)
        
        url = (client.get_secret("ChatgptBasicUrl").value) + "/deployments/" + (client.get_secret("ChatgptModelName").value) + "/chat/completions/?api-version=" + (client.get_secret("ChatgptApiVersion").value)
        headers = { 'Content-Type': 'application/json', 'api-key': (client.get_secret("ChatgptAccessToken").value)  }
        payload = { 'messages': conversation }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response


if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()

    while True:
        
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)

