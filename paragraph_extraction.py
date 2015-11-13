import glob
from alchemyapi import AlchemyAPI
import json
import csv

scanned_files = glob.glob("haad_docs/txt_tesseract/*txt")

alchemyapi = AlchemyAPI()
output_file = open("NameFiles.csv","wb")
output_writer = csv.writer(output_file)
output_writer.writerow(["Filename","Grantor","Grantee","Unknown Names"])

valid_counter = 0
invalid_counter = 0
valid_file_names = []

for each_file in scanned_files:
	flag = False
	open_file = open(each_file,"r")
	for each_line in open_file:
		if "THIS IN" in each_line:
			valid_file_names.append(each_file)
			valid_counter+=1
			flag=True
			break
	if flag==False:
		invalid_counter+=1

result = []
all_data = []
for each_file_name in valid_file_names:
	temp_data = []
	for each_line in open(each_file_name,"r"):
		temp_data.append(each_line.strip("\n"))
	all_data.append(temp_data)

change = 0
for i in range(0,len(all_data)):
	for j in range(len(all_data[i])):
		if "THIS IN" in all_data[i][j]:
			doc = " ".join(all_data[i][j:j+60]).lower()
			break
	response = alchemyapi.entities('text', doc, {'sentiment': 1})
	name_list = []
	
	if response['status'] == 'OK':
		for entity in response['entities']:
			if (entity['type'] == "Person"):
				name = entity['text'].encode('utf-8')
				name_list.append(name)
				print valid_file_names[i]+"\t"+name
	#if change>6:
	#	break
	change = change+1
		

	doc_dict = dict()
	doc_list = doc.split()
		
	num =1
	for each_word in doc_list:
		if each_file_name.lower() not in doc_dict.keys():
			doc_dict[each_word.lower()] = num
		num = num + 1	

	grantee = []
	grantor = []
	unknown = [] 

	for each_name in name_list:
		first_name = each_name.split()
		try :
			grantee_distance = doc_dict["grantee"] - doc_dict[first_name[0]]
			grantor_distance = doc_dict["grantor"] - doc_dict[first_name[0]]
			if grantor_distance > grantee_distance:
				grantee.append(each_name)
				print "grantee: ",each_name
			else :
				grantor.append(each_name)
				print "grantor: ",each_name
			
		except:
			unknown.append(each_name)

	output_writer.writerow([valid_file_names[i],grantor,grantee,unknown])

output_file.close()