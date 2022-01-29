#!/bin/sh
#
# Start RTL_433 decoder and announce over MQTT.
#

mqtt="${MQTTHOST:-mqtt}"
pub="/usr/bin/mosquitto_pub -h ${mqtt} -r"
radio="${RADIO:-`hostname`}"

pid=0

# SIGTERM-handler
term_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# Setup SIGTERM handler
trap term_handler SIGTERM
trap '${pub} -t rtl_433/${radio}/status -m offline' EXIT

# Announce service
${pub} -t homeassistant/binary_sensor/rtl_sdr/config -m "{\"stat_t\":\"rtl_433/${radio}/status\",\"dev\":{\"mf\":\"NooElec\",\"mdl\":\"NESDR Nano 2+\",\"ids\":\"RTL2838UHIDIR\",\"name\":\"RTL-SDR ${radio}\",\"via_device\":\"MQTT broker\"},\"dev_cla\":\"connectivity\",\"entity_category\":\"diagnostic\",\"ic\":\"mdi:antenna\",\"name\":\"RTL-SDR Status\",\"uniq_id\":\"${radio}\",\"pl_on\":\"online\",\"pl_off\":\"offline\"}"
${pub} -t "rtl_433/${radio}/status" -m online
/usr/local/bin/rtl_433 -c /rtl_433.conf  -F "mqtt://${mqtt}:1883,events=rtl_433/${radio}[/id]" &
pid="$!"

wait "$pid"
