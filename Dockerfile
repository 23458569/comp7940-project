FROM python
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

#RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

ENV KEY_VAULT_NAME=comp7940KeyVault
ENV AZURE_TENANT_ID=f8971b7d-548e-4a09-b619-e94079137094
ENV AZURE_CLIENT_ID=abb40e96-add0-4e90-b08f-b85e448936f9
ENV AZURE_CLIENT_SECRET=$(cat /run/secrets/AZURE_CLIENT_SECRET)

ENTRYPOINT python chatbot.py
