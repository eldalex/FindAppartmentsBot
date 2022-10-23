FROM python:3.9

RUN apt update && apt -y install nano python3-pip

RUN mkdir /homeproject
RUN mkdir /homeproject/database
RUN mkdir /homeproject/logs
RUN mkdir /homeproject/tmp

ENV APP_HOME=/homeproject

ADD HelperFindAppatrmentsBot.py $APP_HOME
ADD entrypoint.sh $APP_HOME
ADD main.py $APP_HOME
ADD Scrapping.py $APP_HOME
ADD requirements.txt $APP_HOME
ADD chromedriver $APP_HOME
ADD ./tmp/google-chrome-stable_current_amd64.deb $APP_HOME/tmp
RUN pip install -r $APP_HOME/requirements.txt

RUN apt install -y /homeproject/tmp/google-chrome-stable_current_amd64.deb

RUN chmod +x /homeproject/chromedriver
RUN chmod +x /homeproject/entrypoint.sh

CMD ["/homeproject/entrypoint.sh"]
