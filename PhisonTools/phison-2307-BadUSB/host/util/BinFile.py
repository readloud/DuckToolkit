def save(name, data):
	hf = open(name, "wb")
	hf.write(data)
	hf.close()

def load(name):
	hf = open(name, "rb")
	data = hf.read()
	hf.close()
	return data
