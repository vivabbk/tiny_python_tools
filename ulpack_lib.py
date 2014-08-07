#!/usr/bin/env python

###

import sys, struct

########
class UlpackData:
	def __init__(self):
		self.clear_data()

########	
	def __del__(self):
		self.clear_data()

########	
	def clear_data(self):
		self.list_attr_names = []
		self.dict_attr_value = {}
		self.body_attr = ''
		self.list_text_names = []
		self.dict_text_value = {}

########		
	def set_attribute(self, attr_name, attr_value):
		if attr_name not in self.list_attr_names:
			self.list_attr_names.append(attr_name)
		
		self.dict_attr_value[attr_name] = attr_value
		return 0

########	
#	def add_attribute(self, attr_name, new_attr_value):
#		if attr_name in self.list_attr_names:
#			return -1
#		
#		self.list_attr_names.append(attr_name)
#		self.dict_attr_value[attr_name] = new_attr_value
#		return 0

########	
	def get_attribute(self, attr_name):
		if attr_name not in self.list_attr_names:
			return ''
		else:
			return self.dict_attr_value[attr_name]

########	
	def set_text(self, text_name, text_value):
		if text_name not in self.list_text_names:
			self.list_text_names.append(text_name)
		
		self.dict_text_value[text_name] = text_value
		return 0

########	
	def get_text(self, text_name):
		if text_name not in self.list_text_names:
			return ''
		else:
			return self.dict_text_value[text_name]

########		
	def rebuild_body_section(self):
		if self.body_attr == '':
			return -1
		
		body_slices = []
		for text_name in self.list_text_names:
			text_value = self.dict_text_value[text_name]
			text_len = len(text_value)
			body_slice = text_name + str(text_len)
			body_slices.append(body_slice)
		body = '+'.join(body_slices)
		self.body_attr = body
		
		return 0
	
########
	def output_as_ulpack(self):
		ret = self.rebuild_body_section()
		if ret != 0:
			return ''
		
		str_ulpack = ''
		
		attr_block = ''
		for name in self.list_attr_names:
			attr_value = self.dict_attr_value[name]
			attr_block += name + ' : ' + attr_value + '\r\n'
		attr_block += 'Body : ' + self.body_attr + '\r\n\r\n'
		attr_len = len(attr_block)
		###
		text_block = ''
		for name in self.list_text_names:
			text_value = self.dict_text_value[name]
			text_block += text_value
		text_len = len(text_block)
		###
		ulpack_head = '~BUF! ' + str(attr_len) + ' ' + str(text_len) + ' '
		while len(ulpack_head) < 19:
			ulpack_head += '@'
		ulpack_head += '\0'
		ulpack_tail = '~EOF!'
		###
		str_ulpack = ulpack_head + attr_block + text_block + ulpack_tail
		
		return str_ulpack
	
########	
	def build_with_string(self, str_ulpack):				
		if str_ulpack == '':
			return -1
			
		self.clear_data()
		
		###
		ulpack_head = str_ulpack[:20]
		ulpack_head_slices = ulpack_head.split()
		try:
			attr_len = int(ulpack_head_slices[1])
			text_len = int(ulpack_head_slices[2])
		except:
			#print '###',ulpack_head_slices[1],'###'
			return -1
		attr_block = str_ulpack[20: 20 + attr_len]
		text_block = str_ulpack[20 + attr_len : 20 + attr_len + text_len]
		ulpack_tail = str_ulpack[-5:]
		###
		
		lines = attr_block.split('\r\n')
		for line in lines:
			line = line.rstrip()
			words = line.split(' : ')
			if len(words) != 2:
				continue
			
			attr_name = words[0]
			attr_value = words[1]
			
			if attr_name != 'Body':
				self.list_attr_names.append(attr_name)
				self.dict_attr_value[attr_name] = attr_value
			else:
				self.body_attr = attr_value
		###
		if self.body_attr != '':
			body = self.body_attr
		else:
			return -2
		sec_slices = body.split('+')
		idx = 0
		for sec_slice in sec_slices:
			text_name = sec_slice[:4]
			text_len = int(sec_slice[4:])
			
			self.list_text_names.append(text_name)
			self.dict_text_value[text_name] = text_block[idx: idx + text_len]
			
			idx += text_len
		###
		return 0

########
	def print_out(self, file_out):		
		for attr_name in self.list_attr_names:
			file_out.write(attr_name + ' : ' + self.dict_attr_value[attr_name] + '\n')
		file_out.write('Body : ' + self.body_attr + '\n')
		for text_name in self.list_text_names:
			file_out.write(text_name + ' : ' + self.dict_text_value[text_name] + '\n')
		
		return 0

##############################
def read_seqbody_data(file_in):
	#key_len
	readed = file_in.read(4)
	try:
		klen = int(struct.unpack('i', readed)[0])
	except:
		return -1, 0, '', 0, ''
	#key
	key = file_in.read(klen)
	if not key and klen > 0:
		return -1, 0, '', 0, ''
	#value_len
	readed = file_in.read(4)
	if not readed:
		return -1, 0, '', 0, ''
	vlen = int(struct.unpack('i', readed)[0])
	#value
	value = file_in.read(vlen)
	if not value:
		return -1, 0, '', 0, ''
	###
	
	return 0, klen, key, vlen, value

##############################
def write_seqbody_data(file_out, key, value):
	key_len = len(key)
	value_len = len(value)
	file_out.write(struct.pack('i', key_len) )
	file_out.write(key)
	file_out.write(struct.pack('i', value_len) )
	file_out.write(value)
	
	return 0

##############################
if __name__ == "__main__":
	print 'this is ulpack_lib class wrote by lileng.'