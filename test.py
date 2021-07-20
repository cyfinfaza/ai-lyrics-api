from app import getLyricsFromQuery
from time import perf_counter

while True:
	then = perf_counter()
	# scrape("https://genius.com/Avicii-wake-me-up-lyrics")
	# scrape("https://www.lyricsontop.com/avicii-songs/wake-me-up-lyrics.html")
	getLyricsFromQuery('wake me up avicii genius')
	print(perf_counter()-then)
	# break