#!/usr/bin/env python

#######################################
##defination for ctnt_parser.
(RL_NO_DEFINE, RL_AC_CT, RL_SUSP_CT, RL_LOWER_AC_CT, RL_LOWER_SUSP_CT, RL_TOPIC_RELA, \
RL_TOPIC_NO_RELA, RL_PAGE_AID, RL_PAGE_FRAME, RL_PAGE_MAX) = range(10)

########
class CtntParser:
	def __init__(self):
		self.refresh()

########
	def __del__(self):
		self.m_count = 0

########
	def refresh(self):
		self.m_count = 0
		self.list_level = [0] * RL_PAGE_MAX
		self.list_relate = [0] * RL_PAGE_MAX
		self.list_mark = [0] * RL_PAGE_MAX
		self.list_offset = [0] * RL_PAGE_MAX
		self.list_ctntlen = [0] * RL_PAGE_MAX
		self.list_idx = [0] * RL_PAGE_MAX
		self.list_imgOffsetInCtnt = [-1] * RL_PAGE_MAX
		self.list_ctnt_text = [''] * RL_PAGE_MAX
		self.m_pRelateCtnt = ''
		
		'''
		const int MAX_LINE_BUF_LEN = 1048576;
		char m_pRelateCtnt[MAX_LINE_BUF_LEN];
		'''
		return 0
		
########
	def getTextCount(self):
		return self.m_count

########
	def getImgTextRela(self, idx):
		if idx < 0 or idx >= self.m_count:
			return -1
		return self.list_relate[self.list_idx[idx]]

########
	def getContent(self, idx):
		if idx < 0 or idx >= self.m_count:
			return ''
		return self.list_ctnt_text[self.list_idx[idx]]

########
	def getOffset(self, idx):
		if idx < 0 or idx >= self.m_count:
			return 0
		return self.list_offset[self.list_idx[idx]]

########
	def isIncludeImg(self, idx):
		if idx < 0 or idx >= self.m_count:
			return -1
		if self.list_imgOffsetInCtnt[self.list_idx[idx]] >= 0:
			return 1
		else:
			return 0

########
	def print_out(self):
		print "m_count", self.m_count
		print "list_level          ", self.list_level
		print "list_relate         ", self.list_relate
		print "list_mark           ", self.list_mark
		print "list_offset         ", self.list_offset
		print "list_ctntlen        ", self.list_ctntlen
		print "list_idx            ", self.list_idx
		print "list_imgOffsetInCtnt", self.list_imgOffsetInCtnt
		#print "list_ctnt_text      ", self.list_ctnt_text
		print "list_ctnt_text      ", [len(i) for i in self.list_ctnt_text] 
		print "m_pRelateCtnt", self.m_pRelateCtnt
		print '#' * 100
		
		return 0

########
	def parse_item(self, the_str, text_type):
		block_tag = '\2'
		
		words = the_str.split(block_tag, 4)
		if len(words) != 5:
			return -1
			
		try:	
			self.list_level[text_type] = int(words[0])
			self.list_relate[text_type] = int(words[1])
			self.list_mark[text_type] = int(words[2])
			self.list_imgOffsetInCtnt[text_type] = int(words[3])
			self.list_ctnt_text[text_type] = words[4]
			self.list_ctntlen[text_type] = len(words[4])
		except:
			return -2
		
		return 0

########
	def parse_ctnt(self, the_str):
		if len(the_str) == 0:
			return 0
		
		self.refresh()
		text_tag = '\1'
		obj_tag = '\3'
		
		words = the_str.split(text_tag)
		
		new_words = []
		need_data_type = 1
		
		for i in range(len(words) ):
			if need_data_type == 1:
				if words[i] != '' and words[i] != obj_tag:
					if i == 0:
						return -1
					else:
						new_words[-1] = new_words[-1] + text_tag + words[i]
				else:
					if words[i] == obj_tag:
						new_words.append(words[i])
					need_data_type = 2
			elif need_data_type == 2:
				new_words.append(words[i])
				need_data_type = 1
			else:
				return -2
		
		#
		imgOffset = -1
		offset = 0
		buf_idx = RL_PAGE_MAX - 1
		idx = 0
		
		for item in new_words:
			if item == obj_tag:
				imgOffset = offset
			else:
				ret = self.parse_item(item, buf_idx)
				if ret != 0:
					return -3
				
				if self.list_imgOffsetInCtnt[buf_idx] > 0:
					imgOffset = offset + self.list_imgOffsetInCtnt[buf_idx]
				
				self.list_offset[buf_idx] = offset
				offset += self.list_ctntlen[buf_idx]
				
				#check app/search/image/img-build/extractor2v/strategy/strategy/textparser.cpp for details.
				idx = self.list_relate[buf_idx] - 1
				if idx < 0 or idx >= buf_idx:
					continue
				
				###
				###
				###
				if self.list_relate[buf_idx] == RL_TOPIC_RELA:
					self.m_pRelateCtnt += self.list_ctnt_text[buf_idx]
					
					if self.list_imgOffsetInCtnt[buf_idx] != -1:
						self.list_imgOffsetInCtnt[idx] = self.list_ctntlen[idx] + self.list_imgOffsetInCtnt[buf_idx]
						self.list_offset[idx] = imgOffset - (self.list_offset[idx] + self.list_imgOffsetInCtnt[buf_idx] )
					self.list_ctntlen[idx] += self.list_ctntlen[buf_idx]
					
					self.list_level[idx] = self.list_level[buf_idx]
					self.list_relate[idx] = self.list_relate[buf_idx]
					self.list_mark[idx] = self.list_mark[buf_idx]
					self.list_ctnt_text[idx] = self.m_pRelateCtnt
				elif self.list_ctntlen[idx] < self.list_ctntlen[buf_idx] or self.list_imgOffsetInCtnt[buf_idx] > 0:
					if self.list_imgOffsetInCtnt[idx] == -1:
						self.list_level[idx] = self.list_level[buf_idx]
						self.list_imgOffsetInCtnt[idx] = self.list_imgOffsetInCtnt[buf_idx]
						self.list_relate[idx] = self.list_relate[buf_idx]
						self.list_mark[idx] = self.list_mark[buf_idx]
						self.list_ctnt_text[idx] = self.list_ctnt_text[buf_idx]
						self.list_ctntlen[idx] = self.list_ctntlen[buf_idx]
						self.list_offset[idx] = self.list_offset[buf_idx]
				
				self.m_count += 1
		
		self.m_count = 0
		for i in range(RL_PAGE_MAX - 2, -1, -1):
			if self.list_ctntlen[i] > 0:
				self.list_idx[self.m_count] = i
				#
				if imgOffset != -1:
					self.list_offset[i] -= imgOffset
				else:
					self.list_offset[i] = 0
				self.m_count += 1
		
		return 0

########
	def build_ct(self, str_ctnt):
		ct0_text = ''
		ct1_text = ''
		ct2_text = ''
		
		ret = self.parse_ctnt(str_ctnt)
		if ret != 0:
			return -1, '', '', ''
		
		for i in range(self.m_count):
			rela = self.getImgTextRela(i)
			the_str = self.getContent(i).strip()
			if rela == RL_AC_CT:
				ct0_text = ct0_text + the_str
			elif rela == RL_SUSP_CT:
				ct1_text = ct1_text + the_str
			elif rela == RL_TOPIC_RELA:
				ct2_text = ct2_text + the_str
		
		return 0, ct0_text, ct1_text, ct2_text

########
##############################
def unzip_ctnt_texts(str_ctnt_in, is_from_ulpack = False):
	ret = 0
	
	the_parser = CtntParser()
	str_ctnt = str_ctnt_in
	
	if is_from_ulpack:
		str_ctnt = str_ctnt_in.rstrip('\0')
		if str_ctnt == '(null)':
			str_ctnt = ''
	
	ret, str_ct0, str_ct1, str_ct2 = the_parser.build_ct(str_ctnt)
	
	ret_list = []
	
	if ret == 0:
		ret_list.append(str_ct0)
		ret_list.append(str_ct1)
		ret_list.append(str_ct2)
	
	return ret_list

##############################
def get_ct0_from_ctnt(str_ctnt_in, is_from_ulpack = False):
	
	ctnt_list = unzip_ctnt_texts(str_ctnt_in, is_from_ulpack)
	
	if len(ctnt_list) == 3:
		return ctnt_list[0]
	else:
		return ''

##############################
def get_ct1_from_ctnt(str_ctnt_in, is_from_ulpack = False):
	
	ctnt_list = unzip_ctnt_texts(str_ctnt_in, is_from_ulpack)
	
	if len(ctnt_list) == 3:
		return ctnt_list[1]
	else:
		return ''
	
##############################
def get_ct2_from_ctnt(str_ctnt_in, is_from_ulpack = False):
	ctnt_list = unzip_ctnt_texts(str_ctnt_in, is_from_ulpack)
	
	if len(ctnt_list) == 3:
		return ctnt_list[2]
	else:
		return ''

##############################
if __name__ == "__main__":
	print 'this is ctnt_parser class wrote by lileng.'