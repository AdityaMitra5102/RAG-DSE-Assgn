from flask import *
from rag import *
import webbrowser
from threading import *
import time
from dotenv import load_dotenv

load_dotenv()

app= Flask(__name__)

querydict={}
noragquerydict={}
rfcjson={}

def process_norag_query(query):
	global noragquerydict
	print(query)
	resp=no_rag_query(query)
	print(resp)
	noragquerydict[query]['result']=resp
	noragquerydict[query]['status']=4	


def open_browser():
	time.sleep(5)
	port = int(os.getenv('PORT', 5000))
	webbrowser.open(f'http://localhost:{port}', new=2)

def process_query(query):
	global querydict, vstore
	print(query)
	similarrfc=get_similarity(vstore, query)
	querydict[query]['rfclist']=similarrfc
	querydict[query]['current']=0
	querydict[query]['total']=9999
	querydict[query]['status']=2
	loadrfcs=load_rfc_documents(similarrfc)
	localvstore=create_vector_store(loadrfcs, querydict, query)
	print('Loaded them into vector store')
	querydict[query]['status']=4
	retriever=localvstore.as_retriever()
	qa=RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
	resp=qa.run(query)
	print(resp)
	querydict[query]['result']=resp
	querydict[query]['status']=4	
	

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/library')
def library():
	return render_template('library.html')

@app.route('/metadata')
def metadata():
	global rfcjson
	return jsonify(rfcjson)
	
@app.route('/rfc')
def getrfc():
	rfcnum=int(request.args.get('num'))
	filepath=os.path.join(rfc_directory, f'rfc{str(rfcnum)}.txt')
	content=''
	with open(filepath, 'r') as f:
		content=f.read()
		
	additional_content=''
	psfilepath=os.path.join(rfc_directory, f'rfc{str(rfcnum)}.ps')
	if os.path.exists(psfilepath):
		additional_content='Supplementary PS file available for this RFC. Reading'
		
	htmltext=f'<html><body style="background-color: rgba(255, 255, 255, 0.7);"><h2>{additional_content}</h2><br><pre>{content}</pre></body></html>'
	return render_template_string(htmltext)

@app.route('/query', methods=["POST"])
def submitquery():
	global querydict
	querystring=request.form.get('query')
	userag=request.form.get('expert').lower()=='true'
	if userag:
		if querystring not in querydict:
			querydict[querystring]={}
			querydict[querystring]['status']=3
			th=Thread(target=process_query, args=(querystring,))
			th.start()
		return jsonify(querydict[querystring])
	else:
		if querystring not in noragquerydict:
			noragquerydict[querystring]={}
			noragquerydict[querystring]['status']=3
			th=Thread(target=process_norag_query, args=(querystring,))
			th.start()
		return jsonify(noragquerydict[querystring])
		
	
def main():
	global vstore, rfcjson
	vstore=init_rag()
	rfcjson=preprocess_rfc_index(rfc_directory, 'rfc-index.txt')
	Thread(target=open_browser).start()
	port = int(os.getenv('PORT', 5000))
	host = os.getenv('HOST', '0.0.0.0')
	app.run(host=host, port=port, debug=False)
	
if __name__=='__main__':

	main()

