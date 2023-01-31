from flask import Flask, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from transformers import pipeline
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import urllib
from fpdf import FPDF

app = Flask(__name__)

@app.get('/summary')
def summary_api():
    url = request.args.get('url','')
    if "file:///C:" in url:
        pdf_id = url.split("file:///C:")[1]
        raw_text = extract_text(pdf_id)
        summary = get_summary(raw_text)
    elif "youtube" in url:
        video_id = url.split('=')[1]
        summary = get_summary(get_transcript(video_id))
    else:
        web_id = url
        html = urllib.request.urlopen(web_id).read()
        soup = BeautifulSoup(html, 'html.parser')
        web_text = soup.get_text()
        summary = get_summary(web_text)
    
    return summary, 200

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    return transcript

def get_summary(transcript):
    summariser = pipeline('summarization', model="facebook/bart-large-cnn")
    summary = ''
    for i in range(0, (len(transcript)//1000)+1):
        summary_text = summariser(transcript[i*1000:(i+1)*1000])[0]['summary_text']
        summary = summary + summary_text + ' '
    return summary
    

if __name__ == '__main__':
    app.run()