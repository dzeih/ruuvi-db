#!/usr/bin/env zsh
crontab -l > temp_cron
echo "*/5 * * * * $(pwd)/venv/bin/python $(pwd)/read_ruuvi.py >/tmp/cron.log 2>/tmp/cron_stderr.log" >> temp_cron
crontab temp_cron
rm temp_cron
