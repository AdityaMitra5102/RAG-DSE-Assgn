from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from tqdm import tqdm

import codecs
import os
from preprocess import *
from datasetdownloader import *

model = 'granite3-dense'
embedmodel = 'nomic-embed-text'  
CHUNK_SIZE = 512
CHUNK_OVERLAP = 20
vstore=None

codecs.register_error("strict", codecs.ignore_errors)
embeddings = OllamaEmbeddings(model=embedmodel)
llm=OllamaLLM(model=model)

def load_rfc_documents(rfclist):
	docs=[]
	for rfc in rfclist:
		filepath=(os.path.join(rfc_directory, f'rfc{str(rfc)}.txt'))
		loader=TextLoader(filepath)
		docs.extend(loader.load())
		
	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=CHUNK_SIZE,
		chunk_overlap=CHUNK_OVERLAP,
		length_function=len,
	)
		
	chunked_docs=text_splitter.split_documents(docs)
		
	return chunked_docs

	    
def create_docs_preprocess(rfcjson):
	docs=[]
	for rfc in rfcjson:
		doc=Document(page_content=rfcjson[rfc], metadata={'RFC':rfc})
		docs.append(doc)
	return docs

def get_similarity(vectorstore, query):
	docs=vectorstore.similarity_search_with_score(query)
	rfclist=[]
	for x in docs:
		rfclist.append(x[0].metadata['RFC'])
	return rfclist
	
def get_material(vectorstore,query):
	docs=vectorstore.similarity_search_with_score(query)
	return docs

def create_vector_store(texts, querydict=None, query=None):
    vector_store = FAISS.from_documents(
        documents=[texts[0]],
        embedding=embeddings,
    )
    curr=1
    ingest=texts

    for text in tqdm(ingest):
        if querydict is not None and query is not None:
            querydict[query]['current']=curr
            querydict[query]['total']=len(ingest)
        vector_store.add_documents([text])
        curr=curr+1
        if curr>len(ingest):
            curr=len(ingest)
    return vector_store

def create_preprocessed_vstore():
	rfcjson=preprocess_rfc_index(os.path.join(rfc_directory, 'rfc-index.txt'))
	docs=create_docs_preprocess(rfcjson)
	vstore=create_vector_store(docs)
	return vstore

def process_query(query):
	print(query)
	similarrfc=get_similarity(vstore, query)
	print('Found similar RFCs', similarrfc)
	loadrfcs=load_rfc_documents(similarrfc)
	localvstore=create_vector_store(loadrfcs)
	print('Loaded them into vector store')
	retriever=localvstore.as_retriever()
	qa=RetrievalQA.from_chain_type(llm=llm, chain_type='refine', retriever=retriever)
	resp=qa.run(query)
	print(resp)
	return resp

def init_rag():
	global vstore
	test_ollama()
	download_model()
	init_datadownload()
	try:
		vstore=FAISS.load_local('faiss_index', embeddings, allow_dangerous_deserialization=True)
		print('Vector database loaded')
	except:
		print('Creating Vector database')
		vstore=create_preprocessed_vstore()
		vstore.save_local('faiss_index')
	return vstore

if __name__ == "__main__":
    while True:
    	query=input('Enter query or quit \n')
    	if query=='quit':
    	    	break	
    	process_query(query)