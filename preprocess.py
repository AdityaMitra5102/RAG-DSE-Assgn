import json
filename='rfc-index.txt'

def format_line(line):
	line=line.replace('\n',' ')
	formatted= ' '.join(line.split())
	return formatted

def preprocess_rfc_index(filename):
	with open(filename, encoding='utf-8', errors='ignore') as f:
		lines=f.readlines()
	for x in lines:
		if not x.startswith('0'):
			lines.remove(x)
		else:
			break
	
	currline=''
	rfclines=[]	
	for x in lines:
		if x.startswith(' '):
			currline=currline+' '+x
		else:
			rfclines.append(currline)
			currline=x
	rfclines.append(currline)
	for x in rfclines:
		if x=='' or x=='\n':
			rfclines.remove(x)

	rfcformattedlines=[]
	for line in rfclines:
		rfcformattedlines.append(format_line(line))
			
	lines=[]
			
	for x in rfcformattedlines:
		try:
			line=x[:x.index('(Format:')]
			lines.append(line.strip())
		except:
			if 'Not Issued.' not in x:			
				print(x)
			
	rfcdict={}
	for x in lines:
		rfcnum=int(x[:x.index(' ')])
		rfcdict[rfcnum]=f'RFC-{str(rfcnum)}, RFC{str(rfcnum)}, {x}'
		
	print(json.dumps(rfcdict, indent=2))
	return rfcdict
	
