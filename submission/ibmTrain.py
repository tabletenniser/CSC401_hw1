# ibmTrain.py
# 
# This file produces 11 classifiers using the NLClassifier IBM Service
# 
# TODO: You must fill out all of the functions in this file following 
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#

###IMPORTS###################################
import re
import os
import codecs
import requests

###HELPER FUNCTIONS##########################

def convert_training_csv_to_watson_csv_format(input_csv_name, group_id, output_csv_name): 
	# Converts an existing training csv file. The output file should
	# contain only the 11,000 lines of your group's specific training set.
	#
	# Inputs:
	#	input_csv - a string containing the name of the original csv file
	#		ex. "my_file.csv"
	#
	#	output_csv - a string containing the name of the output csv file
	#		ex. "my_output_file.csv"
	#
	# Returns:
	#	None
	
        TWEET_REGEX = '^\"(\d)\",\"(\d+)\",\"([^\"]+)\",\"(.+)\",\"([^\"]+)\",\"(.+)\"$'

        class_0_lb = group_id * 5500
        class_0_ub = (group_id + 1) * 5500 - 1
        class_4_lb = class_0_lb + 800000
        class_4_ub = class_0_ub + 800000

        line_count = 0
        out = codecs.open(output_csv_name, 'w', 'utf-8')
        with codecs.open(input_csv_name, "r", 'latin-1') as f:
            for line in f:
                line_count += 1
                if ((line_count >= class_0_lb and line_count <= class_0_ub) or
                    (line_count >= class_4_lb and line_count <= class_4_ub)):
                    tweet_match = re.match(TWEET_REGEX, line)
                    try:
                        tclass, tid, date, query, user, text = tweet_match.groups()
                    except Exception as e:
                        print "Unable to parse tweet " + line
                        continue
                    text = text.replace('"', '')
                    text = text.replace('\t', '')
                    out.write('"%s","%s"\n'%(text,tclass))
        out.close()
	return
	
def extract_subset_from_csv_file(input_csv_file, n_lines_to_extract, output_file_prefix='ibmTrain'):
	# Extracts n_lines_to_extract lines from a given csv file and writes them to 
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs: 
	#	input_csv - a string containing the name of the original csv file from which
	#		a subset of lines will be extracted
	#		ex. "my_file.csv"
	#	
	#	n_lines_to_extract - the number of lines to extract from the csv_file, as an integer
	#		ex. 500
	#
	#	output_file_prefix - a prefix for the output csv file. If unspecified, output files 
	#		are named 'ibmTrain#.csv', where # is the input parameter n_lines_to_extract.
	#		The csv must be in the "watson" 2-column format.
	#		
	# Returns:
	#	None
        out = codecs.open(output_file_prefix+str(n_lines_to_extract)+'.csv', 'w', 'utf-8')
        class_0_count = 0
        class_4_count = 0
        with codecs.open(input_csv_file, "r", 'utf-8') as f:
            for ori_line in f:
                line = ori_line.strip()
                text, tclass = line.split('","')
                tclass = tclass.replace('"', '')

                if tclass == '0':
                    if class_0_count < n_lines_to_extract:
                        class_0_count += 1
                    else:
                        continue
                elif tclass == '4':
                    if class_4_count < n_lines_to_extract:
                        class_4_count += 1
                    else:
                        break
                else:
                    raise Exception('Unrecognized class '+tclass)
                out.write(ori_line)
        out.close()
	return
	
def create_classifier(username, password, n, input_file_prefix='ibmTrain'):
	# Creates a classifier using the NLClassifier service specified with username and password.
	# Training_data for the classifier provided using an existing csv file named
	# ibmTrain#.csv, where # is the input parameter n.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	n - identification number for the input_file, as an integer
	#		ex. 500
	#
	#	input_file_prefix - a prefix for the input csv file, as a string.
	#		If unspecified data will be collected from an existing csv file 
	#		named 'ibmTrain#.csv', where # is the input parameter n.
	#		The csv must be in the "watson" 2-column format.
	#
	# Returns:
	# 	A dictionary containing the response code of the classifier call, will all the fields 
	#	specified at
	#	http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/natural-language-classifier/api/v1/?curl#create_classifier
	#   
	#
	# Error Handling:
	#	This function should throw an exception if the create classifier call fails for any reason
	#	or if the input csv file does not exist or cannot be read.
        input_file = input_file_prefix+str(n)+'.csv'
        if not os.path.exists(input_file):
            raise Exception("File "+input_file+" does not exist!")

        try:
            url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers'
            payload = {'training_data': open(input_file, 'rb'), 'training_metadata': '{"language":"en", "name":"Classifier %d"}'%(n)}
            r = requests.post(url, auth=(username, password), files=payload)
            print r.content
            if r.status_code != 200:
                raise Exception('ERROR: Response code is NOT 200')

        except Exception as e:
            raise Exception('Unable to POST to Watson with error: %s'%(e))
	
	return r.content
	
if __name__ == "__main__":
	
	### STEP 1: Convert csv file into two-field watson format
	input_csv_name = 'training.1600000.processed.noemoticon.csv'
	
	#DO NOT CHANGE THE NAME OF THIS FILE
	output_csv_name = 'training_11000_watson_style.csv'
	
	convert_training_csv_to_watson_csv_format(input_csv_name, 55, output_csv_name)
	
	### STEP 2: Save 3 subsets in the new format into ibmTrain#.csv files
	# you should make use of the following function call:
	n_lines_to_extract = 500
	extract_subset_from_csv_file(output_csv_name,n_lines_to_extract)
	n_lines_to_extract = 2500
	extract_subset_from_csv_file(output_csv_name,n_lines_to_extract)
	n_lines_to_extract = 5000
	extract_subset_from_csv_file(output_csv_name,n_lines_to_extract)
	
	### STEP 3: Create the classifiers using Watson
	username = '2c26f0a8-b83b-448c-8b44-daa6e799f8a3'
	password = 'WKW85r9ZVwuf'
	n = 500
	create_classifier(username, password, n, input_file_prefix='ibmTrain')
	n = 2500
	create_classifier(username, password, n, input_file_prefix='ibmTrain')
	n = 5000
	create_classifier(username, password, n, input_file_prefix='ibmTrain')
