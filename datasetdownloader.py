import wget
from zipfile import ZipFile
import time
rfc_directory = "./RFC-all"
model = 'granite3-dense'
embedmodel = 'nomic-embed-text'

import os
from tqdm import tqdm
import requests
import subprocess

def rfcdownloader():
	url='https://www.rfc-editor.org/in-notes/tar/RFC-all.zip'
	print('Downloading zip')
	filename=wget.download(url)
	print('..Done')
	print('Extracting')
	with ZipFile(filename, 'r') as zObject:
		zObject.extractall(rfc_directory)
	print('Cleaning')
	os.remove(filename)
	directory_to_clean=rfc_directory
	if os.path.exists(directory_to_clean):
		for root, _, files in os.walk(directory_to_clean):
			for file in tqdm(files):
				if not file.lower().endswith('.txt'):
					file_path = os.path.join(root, file)
					try:
						os.remove(file_path)
					except Exception as e:
						print(f"Error deleting {file_path}: {e}")

def init_datadownload():
	if not os.path.exists(rfc_directory):
		rfcdownloader()
	else:
		print('Dataset exists. Skipping download')
		
def download_model():
	os.system(f'ollama pull {model}')
	os.system(f'ollama pull {embedmodel}')
	
def start_ollama():
	subprocess.Popen('ollama serve')
	time.sleep(3)
	
def test_ollama(retry=False):
	try:
		resp=requests.get('http://localhost:11434').text
		if 'Ollama' in resp:
			return True
		else:
			if not retry:
				start_ollama()
				return test_ollama(True)
			raise ValueError('Ollama is not running. Please start Ollama.')
	except:
		if not retry:
			start_ollama()
			return test_ollama(True)
		raise ValueError('Ollama is not running. Please start Ollama.')