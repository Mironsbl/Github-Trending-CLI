#!/bin/bash
# Remove old URL file
rm -f /home/miron/github-trending-web/tunnel_url.txt
rm -f /home/miron/github-trending-web/localtunnel.log

# Start localtunnel in the background
npx -y localtunnel --port 5050 --subdomain git-trends-miron > /home/miron/github-trending-web/localtunnel.log 2>&1 &
LT_PID=$!

# Wait up to 15 seconds for the URL to appear in the log
for i in {1..15}; do
    sleep 1
    if grep -q "your url is:" /home/miron/github-trending-web/localtunnel.log; then
        break
    fi
done

# Extract the URL from the log file
line=$(grep "your url is:" /home/miron/github-trending-web/localtunnel.log)
if [[ "$line" =~ (https://[a-zA-Z0-9.-]+\.loca\.lt) ]]; then
    url="${BASH_REMATCH[1]}"
    echo "$url" > /home/miron/github-trending-web/tunnel_url.txt
    echo "TUNNEL_URL_FOUND: $url"
    
    if [[ "$url" != *"git-trends-miron"* ]]; then
        echo "Error: Did not get requested subdomain ($url). Killing process and exiting..."
        kill $LT_PID
        exit 1
    fi
else
    echo "Error: Could not find URL in log. Exiting..."
    kill $LT_PID 2>/dev/null
    exit 1
fi

# Wait for the background localtunnel process to finish
wait $LT_PID
