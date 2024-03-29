import os
#import configparser
import requests
#import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

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

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        
        url = (client.get_secret("ChatgptBasicUrl")) + "/deployments/" + (client.get_secret("ChatgptModelName")) + "/chat/completions/?api-version=" + (client.get_secret("ChatgptApiVersion"))
        headers = { 'Content-Type': 'application/json', 'api-key': (os.environ['CHATGPT_ACCESS_TOKEN']) }
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

