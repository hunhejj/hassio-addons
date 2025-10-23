#!/usr/bin/env bashio

bashio::log.info "getting configuration..."
CONFIG_PATH=/data/options.json

#grab this first since we'll use it below
DEBUG="$(bashio::config 'debug')"
if [[ -n $DEBUG ]] && [[ $DEBUG != "null" ]]; then
    if [[ $DEBUG = "true" ]]; then
        bashio::log.info "exporting [DEBUG=${DEBUG}]"
    fi
    export DEBUG
fi

#grab the rest in a loop
for var in \
    smtp_auth_required \
    smtp_relay_host smtp_relay_port smtp_relay_user smtp_relay_pass smtp_relay_starttls smtp_relay_timeout_secs \
;
do
    v="$(bashio::config ${var})"
    if [[ -n $v ]] && [[ $v != "null" ]]; then
        if [[ $DEBUG = "true" ]]; then
            bashio::log.info "exporting [${var^^}=${v}]"
        fi
        export ${var^^}=${v}
    fi
done

bashio::log.info "starting application..."
python3 /app/smtp-relay.py
