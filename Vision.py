#########################################################################
#########################################################################


#########################################################################
#########################################################################

import glob
from alchemyapi import AlchemyAPI
import json
import csv
import string
import re

class Vision(object):
	ocr_dir_name = ""
	scanned_files = []
	valid_file_names = []
	valid_file_count = 0
	invalid_file_count = 0
	valid_file_criterion = ""
	doc_list = []
	name_list = []
	end_result = []

	def __init__(self):
		#initializating alchemy object and some patterns for string processing
		self.alchemyapi = AlchemyAPI()
		self.space_pattern = re.compile(r"\s+")
		self.punctuation_remover = lambda x:x not in string.punctuation

	def data_reader(self):
		#this function returns all the files in the directory
		self.scanned_files = glob.glob(self.ocr_dir_name)
	
	def set_ocr_dir_location(self,ocr_dir_location):
		#a setter function to specify directory
		self.ocr_dir_name = ocr_dir_location

	def set_valid_file_criterion(self,valid_file_criterion_string):
		#for future reuse when we dont want to just look at documents starting with "THIS IN"
		self.valid_file_criterion = valid_file_criterion_string

	def get_ocr_dir_location(self):
		return self.ocr_dir_name

	def find_valid_files(self):
		#These counters update the class attributes to maintain stats about the number of files that are being filtered 
		valid_counter = 0
		invalid_counter = 0
		valid_file_names = []

		#We look for the documents containing string specified in valid file criterion
		for each_file in self.scanned_files:
			flag = False
			open_file = open(each_file,"r")
			for each_line in open_file:
				if self.valid_file_criterion in each_line:
					self.valid_file_names.append(each_file)
					valid_counter+=1
					flag=True
					break
				if flag==False:
					invalid_counter+=1

		#Maintaining Stats
		self.valid_file_count = valid_counter
		self.invalid_file_count = invalid_counter

	def doc_extractor (self):
		#This function looks at only the valid files and 
		result = []
		all_data = []
		for each_file_name in self.valid_file_names:
			temp_data = []
			for each_line in open(each_file_name,"r"):
				temp_data.append(each_line.strip("\n"))
			all_data.append(temp_data)

		for i in range(0,len(all_data)):
			for j in range(len(all_data[i])):
				if self.valid_file_criterion in all_data[i][j]:
					doc = " ".join(all_data[i][j:j+60]).lower()
					#print doc
					self.doc_list.append(doc)
					break


	def name_extractor(self):
		new_doc_list = []
		i = 0
		for each_doc in self.doc_list:
			response = self.alchemyapi.entities('text', each_doc, {'sentiment': 1})
			name_list = []
			if response['status'] == 'OK':
				for entity in response['entities']:
					if (entity['type'] == "Person"):
						name = entity['text'].encode('utf-8')
						first_name = name.split()
						name_list.append(first_name[len(first_name)-1])
						new_doc_list.append(each_doc)
			self.doc_list = new_doc_list

			doc_dict = dict()
			doc_list = (filter(self.punctuation_remover, word).lower() for word in each_doc.split())
			num =1
			for each_word in doc_list:
				if each_word == "grantees":
					each_word = "grantee"
				elif each_word == "grantors":
					each_word = "grantor"
				if not doc_dict.has_key(each_word):
					doc_dict[each_word] = num
					num = num + 1	
			grantee = []
			grantor = []
			unknown = []

			for each_name in name_list:
				
				first_name = each_name
				try :
					grantee_distance = doc_dict["grantee"] - doc_dict[first_name]
					grantor_distance = doc_dict["grantor"] - doc_dict[first_name]
					if grantee_distance < grantor_distance or grantor_distance<0:
						grantee.append(each_name)
					elif grantee_distance > grantor_distance:
						grantor.append(each_name)
				except :
					unknown.append(each_name)
			self.end_result.append([self.valid_file_names[i],grantee,grantor,unknown])
			i = i +1
		return self.end_result
			

def main():
	petroleum_data_extractor = Vision()
	petroleum_data_extractor.set_ocr_dir_location("haad_docs/txt_tesseract/*txt")
	petroleum_data_extractor.data_reader()
	petroleum_data_extractor.set_valid_file_criterion("THIS IN")
	petroleum_data_extractor.find_valid_files()
	petroleum_data_extractor.doc_extractor()
	end_result = petroleum_data_extractor.name_extractor()
	result_file = open("NameFiles.csv","wb")
	result_writer = csv.writer(result_file)
	for each_row in end_result:
		result_writer.writerow([result_file[0],result_file[1],result_file[2],result_file[3]])
	result_file.close()

if __name__ == "__main__":
	main()
