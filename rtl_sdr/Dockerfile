FROM hertzg/rtl_433
MAINTAINER James Inge

RUN apk --no-cache --no-progress upgrade
RUN apk --no-cache --no-progress add mosquitto-clients

COPY rtl_433.conf /
COPY rtl_433.sh /

EXPOSE 1883

ENTRYPOINT ["/rtl_433.sh"]
