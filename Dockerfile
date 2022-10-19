FROM python:3.9
ARG USERNAME=pythonssh
ARG USERPASS=sshpass
ADD google-chrome-stable_current_amd64.deb .
RUN mkdir ./helperbot
RUN apt update && apt -y install openssh-server whois nano && apt install -y ./google-chrome-stable_current_amd64.deb
RUN useradd -ms /bin/bash $USERNAME
RUN usermod --password $(echo "$USERPASS" | mkpasswd -s) $USERNAME
RUN chown -R $USERNAME:$USERNAME /helperbot
RUN apt purge -y whois && apt -y autoremove && apt -y autoclean && apt -y clean
COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh
USER $USERNAME
RUN mkdir /home/$USERNAME/.ssh && touch /home/$USERNAME/.ssh/authorized_keys
RUN pip install pyTelegramBotAPI
RUN pip install selenium
ADD chromedriver1 ./helperbot
ADD chromedriver2 ./helperbot
ADD HelperFindAppatrmentsBot.py ./helperbot
ADD Scrapping.py ./helperbot
ADD test.py ./helperbot
USER root
VOLUME /home/$USERNAME/.ssh
VOLUME /etc/ssh
CMD ["/entrypoint.sh"]
#CMD python3 ./helperbot/HelperFindAppatrmentsBot.py
