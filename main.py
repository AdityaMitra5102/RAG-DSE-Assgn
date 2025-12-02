from flask import *
from rag import *

from threading import *


app= Flask(__name__)

querydict={}


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
	qa=RetrievalQA.from_chain_type(llm=llm, chain_type='refine', retriever=retriever)
	resp=qa.run(query)
	print(resp)
	querydict[query]['result']=resp
	querydict[query]['status']=4	
	

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/rfc')
def getrfc():
	rfcnum=int(request.args.get('num'))
	filepath=os.path.join(rfc_directory, f'rfc{str(rfcnum)}.txt')
	content=''
	with open(filepath, 'r') as f:
		content=f.read()
	htmltext=f'<html><body style="background-color: rgba(255, 255, 255, 0.7);"><pre>{content}</pre></body></html>'
	return render_template_string(htmltext)

@app.route('/query', methods=["POST"])
def submitquery():
	global querydict
	querystring=request.form.get('query')
	if querystring not in querydict:
		querydict[querystring]={}
		querydict[querystring]['status']=3
		
		th=Thread(target=process_query, args=(querystring,))
		th.start()
		
	return jsonify(querydict[querystring])
	
def main():
	global vstore
	vstore=init_rag()
	app.run(host='0.0.0.0', debug=True)
	
if __name__=='__main__':
	main()