# ibmTest.py
#
# This file tests all 11 classifiers using the NLClassifier IBM Service
# previously created using ibmTrain.py
#
# TODO: You must fill out all of the functions in this file following
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#		You may also find it helpful to reuse some of your functions from ibmTrain.py.
import os
import requests
import json
import re
import codecs

def get_classifier_ids(username,password):
	# Retrieves a list of classifier ids from a NLClassifier service
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#
	# Returns:
	#	a list of classifier ids as strings
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason
	#
        try:
            url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers'
            r = requests.get(url, auth=(username, password))
            if r.status_code == 200:
                classifiers_as_json = r.json()
            # print 'status_code', r.status_code
            # print 'content-type', r.headers['content-type']
            # print classifiers_as_json['classifiers']
            list_of_classifier_ids = []
            for cls in classifiers_as_json['classifiers']:
                # print cls['classifier_id']
                list_of_classifier_ids.append(cls['classifier_id'])
                # cmd = 'curl -u %s:%s "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers"'%(username, password)
                # os.system(cmd)
        except Exception:
            print "Error sending POST request."
            raise

	return list_of_classifier_ids


def assert_all_classifiers_are_available(username, password, classifier_id_list):
	# Asserts all classifiers in the classifier_id_list are 'Available'
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id_list - a list of classifier ids as strings
	#
	# Returns:
	#	None
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason AND
	#	It should throw an error if any classifier is NOT 'Available'
        try:
            for cid in classifier_id_list:
                url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'+str(cid)
                r = requests.get(url, auth=(username, password))
                if r.status_code != 200:
                    raise Exception('Status code from REQUEST is not 200!!!')
                classifiers_as_json = r.json()
                if classifiers_as_json['status'] != 'Available':
                    raise Exception('Job is not available!')
        except Exception:
            print "Error sending POST request."
            raise

	return

def classify_single_text(username,password,classifier_id,text):
	# Classifies a given text using a single classifier from an NLClassifier
	# service
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id - a classifier id, as a string
	#
	#	text - a string of text to be classified, not UTF-8 encoded
	#		ex. "Oh, look a tweet!"
	#
	# Returns:
	#	A "classification". Aka:
	#	a dictionary containing the top_class and the confidences of all the possible classes
	#	Format example:
	#		{'top_class': 'class_name',
	#		 'classes': [
	#					  {'class_name': 'myclass', 'confidence': 0.999} ,
	#					  {'class_name': 'myclass2', 'confidence': 0.001}
	#					]
	#		}
	#
	# Error Handling:
	#	This function should throw an exception if the classify call fails for any reason
        result = dict()
        try:
            payload = {'text': text}
            url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'+str(classifier_id)+'/classify'
            r = requests.get(url, auth=(username, password), params=payload)
            if r.status_code != 200:
                raise Exception('Status code from REQUEST is not 200!!!')
            classifiers_as_json = r.json()
            result['classes'] = classifiers_as_json['classes']
            result['top_class'] = classifiers_as_json['top_class']
            print classifiers_as_json['classes']
        except Exception:
            print "Error sending POST request."
            raise

	return result

def classify_all_texts(username,password,input_csv_name):
	# Classifies all texts in an input csv file using all classifiers for a given NLClassifier
	# service.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	A list of "classifications". Aka:
	#	A list of dictionaries, one for each text, in order of lines in the
	#	input file. Each element is a dictionary containing the top_class
	#	and the confidences of all the possible classes (ie the same
	#	format as returned by classify_single_text)
	#	Format example:
        #       [
	#		[
	#			{'top_class': 'class_name',
	#		 	 'classes': [
	#					  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#					  	{'class_name': 'myclass2', 'confidence': 0.001}
	#						]
	#			},
	#			{'top_class': 'class_name',
	#			...
	#			}
	#		]
	#       ]
	# Error Handling:
	#	This function should throw an exception if the classify call fails for any reason
	#	or if the input csv file is of an improper format.
	#
        classifier_id_list = get_classifier_ids(username, password)
        print classifier_id_list
        TWEET_REGEX = '^\"(\d)\",\"(\d+)\",\"([^\"]+)\",\"(.+)\",\"([^\"]+)\",\"(.+)\"$'

        result = dict()
        for cls_id in classifier_id_list:
            classifier_result = []
            with codecs.open(input_csv_name, "r", 'latin-1') as f:
                for line in f:
                    tweet_match = re.match(TWEET_REGEX, line)
                    try:
                        tclass, tid, date, query, user, text = tweet_match.groups()
                    except Exception as e:
                        print "Unable to parse tweet " + line
                        continue
                    text = text.replace('"', '')
                    text = text.replace('\t', '')
                    classifier_result.append(classify_single_text(username, password, cls_id, text))
            result[cls_id] = classifier_result

	return result


def compute_accuracy_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the accuracy of this
	# classifier according to the input csv file
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text)
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The accuracy of the classifier, as a fraction between [0.0-1.0] (ie percentage/100). \
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the
	#	inputs.
	#
        TWEET_REGEX = '^\"(\d)\",\"(\d+)\",\"([^\"]+)\",\"(.+)\",\"([^\"]+)\",\"(.+)\"$'

        total_count = 0
        correct_label = 0
        with codecs.open(input_csv_file_name, "r", 'latin-1') as f:
            for line in f:
                tweet_match = re.match(TWEET_REGEX, line)
                try:
                    tclass, tid, date, query, user, text = tweet_match.groups()
                except Exception as e:
                    print "Unable to parse tweet " + line
                    continue
                # print 'total_count', total_count
                # print 'size of classifier_dict', len(classifier_dict)
                # print 'classifier_dict[total_count]["top_class"]', classifier_dict[total_count]['top_class']
                # print 'tclass', tclass
                if classifier_dict[total_count]['top_class'] == tclass:
                    correct_label +=1
                total_count += 1

	return correct_label*1.0/total_count

def compute_average_confidence_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the average
	# confidence of this classifier wrt the selected class, according to the input
	# csv file.
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text)
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The average confidence of the classifier, as a number between [0.0-1.0]
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the
	#	inputs.
	#
        TWEET_REGEX = '^\"(\d)\",\"(\d+)\",\"([^\"]+)\",\"(.+)\",\"([^\"]+)\",\"(.+)\"$'

        correct_label_confidences = []
        incorrect_label_confidences = []
        total_count = 0
        with codecs.open(input_csv_file_name, "r", 'latin-1') as f:
            for line in f:
                tweet_match = re.match(TWEET_REGEX, line)
                try:
                    tclass, tid, date, query, user, text = tweet_match.groups()
                except Exception as e:
                    print "Unable to parse tweet " + line
                    continue
                # Case for correct labeling
                if classifier_dict[total_count]['top_class'] == tclass:
                    correct_label_confidences.append(classifier_dict[total_count]['classes'][0]['confidence'])
                else:
                    incorrect_label_confidences.append(classifier_dict[total_count]['classes'][0]['confidence'])
                total_count += 1

        correct_label_conf_average = 1.0*sum(correct_label_confidences)/len(correct_label_confidences)
        incorrect_label_conf_average = 1.0*sum(incorrect_label_confidences)/len(incorrect_label_confidences)
	return correct_label_conf_average, incorrect_label_conf_average

if __name__ == "__main__":
	input_test_data = 'testdata.manualSUBSET.2009.06.14.csv'
	#STEP 1: Ensure all 11 classifiers are ready for testing
	username = '2c26f0a8-b83b-448c-8b44-daa6e799f8a3'
	password = 'WKW85r9ZVwuf'
        # classifier_ids = get_classifier_ids(username, password)
        # print "classifier_ids", classifier_ids
        # assert_all_classifiers_are_available(username, password, classifier_ids)

	#STEP 2: Test the test data on all classifiers
        # classifier_predictions = classify_all_texts(username, password, input_test_data)

        import pickle
        # with open('filename.pickle', 'wb') as handle:
        #     pickle.dump(classifier_predictions, handle)
        with open('filename.pickle', 'rb') as handle:
            classifier_predictions = pickle.load(handle)
        print classifier_predictions.keys()
        print 'len(classifier_predictions)', len(classifier_predictions)
        print 'len(classifier_predictions[0])', len(classifier_predictions['c7fa4ax22-nlc-337'])
        print 'len(classifier_predictions[1])', len(classifier_predictions['c7fa49x23-nlc-323'])
        print 'len(classifier_predictions[2])', len(classifier_predictions['c7e487x21-nlc-384'])

	#STEP 3: Compute the accuracy for each classifier
        for cls_name in classifier_predictions:
            print cls_name
            print compute_accuracy_of_single_classifier(classifier_predictions[cls_name], input_test_data)

	#STEP 4: Compute the confidence of each class for each classifier
        for cls_name in classifier_predictions:
            print cls_name
            print compute_average_confidence_of_single_classifier(classifier_predictions[cls_name], input_test_data)

