FROM python:3.7-stretch

RUN mkdir /opt/docfex
COPY ./requirements.txt /opt/docfex/requirements.txt
WORKDIR /opt/docfex
RUN pip install -r requirements.txt
COPY . .
VOLUME [ "/opt/docfex/src/config" ]

RUN mkdir /mnt/basepath


ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
