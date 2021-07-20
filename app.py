from tensorflow import keras
import numpy as np
import asyncio
from pyppeteer import launch
from flask import Flask, request
from flask_cors import CORS
import googlesearch
from time import perf_counter

app = Flask(__name__)
cors = CORS(app)
model = keras.models.load_model('model-multi')
browser = None

loop = asyncio.get_event_loop()

# docReqs = 0
def scrape(link):
	# loop = asyncio.new_event_loop()
	# asyncio.set_event_loop(loop)
	async def handleReq(req):
		# global docReqs
		# print(req.resourceType)
		# if req.resourceType == 'document':
		# 	if docReqs==0:
		# 		await req.continue_()
		# 	else:
		# 		await req.abort()
		# 		docReqs = docReqs + 1
		# 	return
		if req.resourceType in ['image', 'stylesheet', 'font', 'media']:
			# print("stopped")
			await req.abort()
		else:
			await req.continue_()
	async def main():
		global browser
		if not browser:
			browser = await launch(
				headless=True,
				handleSIGINT=False,
				handleSIGTERM=False,
				handleSIGHUP=False
			)
		page = await browser.newPage()
		await page.setRequestInterception(True)
		page.on('request', lambda req: asyncio.ensure_future(handleReq(req)))
		await page.goto(link)
		await page.screenshot({'path': 'example.png'})
		text = await page.evaluate("document.body.innerText")
		# input()
		await page.close()
		# await browser.close()
		return text
	return loop.run_until_complete(main())

def makeDataset(lineset):
	lasts = []
	currents = []
	nexts = []
	for i in range(len(lineset)):
		lasts.append(lineset[i-1] if i>0 else "")
		currents.append(lineset[i])
		nexts.append(lineset[i+1] if i<len(lineset)-1 else "")
	return [np.array(lasts), np.array(currents), np.array(nexts)]

def getLyricsFromQuery(query):
	link = next(googlesearch.search(query+" lyrics -video -youtube"))
	lines = scrape(link).split('\n')
	# print(lines)
	predictions = model.predict(makeDataset(lines))
	goodlines = [lines[i] for i, prediction in enumerate(predictions) if prediction>0]
	return goodlines


@app.route("/")
def index():
	return "enter a query"

@app.route("/lyrics")
def doQuery():
	query = request.args['q']
	return str(getLyricsFromQuery(query))

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)