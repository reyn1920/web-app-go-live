-- Speechelo AppleScript Helper
-- Copies a text file into clipboard and pastes into Speechelo's main textarea
-- Usage: osascript tools/speechelo_fill.applescript outputs/audio/script.txt

on run argv
	if (count of argv) is 0 then
		return
	end if
	
	set p to POSIX file (item 1 of argv) as alias
	set theText to read p
	set the clipboard to theText
	
	tell application "System Events"
		tell process "Speechelo"
			set frontmost to true
			delay 0.5
			keystroke "a" using command down
			delay 0.2
			keystroke "v" using command down
		end tell
	end tell
end run

