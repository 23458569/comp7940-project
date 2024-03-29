FROM python
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

ENV KEY_VAULT_NAME=comp7940KeyVault

CMD python chatbot.py
