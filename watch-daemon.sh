source ~/.virtualenvs/studentenwerk-room-watcher/bin/activate

for OFFER in $(python /Users/agrebenkin/Dev/speechkey/github/studentenwerk-room-watcher/watcher.py /Users/agrebenkin/Dev/speechkey/github/studentenwerk-room-watcher/offers.txt); do
	LINK=$(echo $OFFER | cut -d"|" -f1)

	/usr/local/bin/terminal-notifier -title "=)" -message "New appartment found" -execute "open $LINK"
done
