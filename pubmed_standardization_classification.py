import sys
import os
import argparse
import gzip
import xml.etree.ElementTree as ET
import ConfigParser
import codecs

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser=argparse.ArgumentParser()
parser.add_argument('-o', help='Output Directory')
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import pubmed_standardization_classification
    parameters = pubmed_standardization_classification.ReadParameters(args)     
    pubmed_standardization_classification.Main(parameters)

def Main(parameters):
    standardization_output=parameters['output']
    standardization_input = parameters['input']
    if not os.path.exists(standardization_output):
        os.makedirs(standardization_output)
    unzip(standardization_input)
    standardization(standardization_input,standardization_output)

def ReadParameters(args):
    parameters_error=False
    parameters_obligation=False
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['output']=Config.get('MAIN', 'output')
        parameters['input']=Config.get('MAIN', 'input')
    else:
        parameters_obligation=True
    if(args.o!=None):
        parameters['output_directory']=args.o
    elif (parameters_obligation):
        print ("No output directory provided")
        parameters_error=False
    if(parameters_error):
        print("Please send the correct parameters.  You can type for --help ")
        sys.exit(1)
    return parameters

def unzip(standardization_input):
    logging.info("Unzip Input Directory " + standardization_input)
    ids_list=[]
    if(os.path.isfile(standardization_input+"/list_files_unziped.txt")):
        with open(standardization_input+"/list_files_unziped.txt",'r') as ids:
            for line in ids:
                ids_list.append(line.replace("\n",""))
        ids.close()
    
    pubMedRetrievals=[]
    if os.path.exists(standardization_input):
        subs = [os.path.join(standardization_input, f) for f in os.listdir(standardization_input) if os.path.isdir(os.path.join(standardization_input, f))]
        for sub in subs:
            onlyfiles = [os.path.join(os.path.join(sub, f)) for f in os.listdir(sub) if (os.path.isfile(os.path.join(sub, f)) & f.endswith('.xml.gz') & (os.path.basename(f) not in ids_list))]
            pubMedRetrievals = pubMedRetrievals + onlyfiles   
    with open(standardization_input+"/list_files_unziped.txt",'a') as list_files_unziped:
        for pubMedRetrieval in pubMedRetrievals:
            file=pubMedRetrieval
            xml_file_path = file + ".xml"
            if os.path.isfile(file):
                with open(xml_file_path,'w') as xml_file:
                    with gzip.open(file, 'rb') as f:    
                        file_content = f.read()
                        xml_file.write(file_content)
                        xml_file.flush()
                        xml_file.close()
                        logging.info("unziped   : " + file)
                        list_files_unziped.write(os.path.basename(file)+"\n")
                        list_files_unziped.flush()
            else:
                print ("The file " + file + " not exist, please review and download again ") 
    list_files_unziped.close()    
    logging.info("Unzip End ")      
                       
def standardization(standardization_input, standardization_output):
    logging.info("Standardization Input Directory " + standardization_input)
    ids_list=[]
    if(os.path.isfile(standardization_output+"/list_files_standardized.txt")):
        with open(standardization_output+"/list_files_standardized.txt",'r') as ids:
            for line in ids:
                ids_list.append(line.replace("\n",""))
        ids.close()
    pubMedRetrievals=[]
    if os.path.exists(standardization_input):
        subs = [os.path.join(standardization_input, f) for f in os.listdir(standardization_input) if os.path.isdir(os.path.join(standardization_input, f))]
        for sub in subs:
            onlyfiles = [os.path.join(sub, f) for f in os.listdir(sub) if (os.path.isfile(os.path.join(sub, f)) & f.endswith('.xml') & (os.path.basename(f) not in ids_list))]
            pubMedRetrievals = pubMedRetrievals + onlyfiles
    with open(standardization_output+"/list_files_standardized.txt",'a') as list_files_standardized:
        for pubMedRetrieval in pubMedRetrievals:
            if not os.path.exists(standardization_output):
                os.makedirs(standardization_output)
            xml_file_path=pubMedRetrieval
            if os.path.isfile(xml_file_path):
                file_name = os.path.basename(xml_file_path)
                with open(xml_file_path,'r') as xml_file:    
                    txt_file_path=  standardization_output + "/" + file_name + ".txt"
                    with codecs.open(txt_file_path,'w',encoding='utf8') as txt_file:
                        logging.info("Parsing: " + xml_file_path)
                        docXml = ET.parse(xml_file)
                        for article in docXml.findall("PubmedArticle"):
                            try:
                                pmid = article.find("MedlineCitation").find("PMID").text
                                art_txt = pmid + "\t"    
                                article_xml = article.find("MedlineCitation").find("Article")
                                abstract_xml = article_xml.find("Abstract")
                                if(abstract_xml!=None):
                                    title_xml=article_xml.find("ArticleTitle")
                                    if(title_xml!=None):
                                        title = title_xml.text
                                        if(title!=None):
                                            art_txt = art_txt + title.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\t" 
                                        else:
                                            art_txt = art_txt + " " + "\t"     
                                        abstract_xml = article_xml.find("Abstract")
                                        if(abstract_xml!=None):
                                            abstract_text = abstract_xml.find("AbstractText")
                                            if(abstract_text!=None):
                                                abstract=abstract_text.text
                                                if(abstract!=None):
                                                    art_txt = art_txt + abstract.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\n" 
                                                    txt_file.write(art_txt)
                                                    txt_file.flush()
                            except Exception as inst:
                                logging.error("Error generation data set for classification " + pmid)
                        txt_file.flush()                     
                        txt_file.close()    
                    xml_file.close()
                logging.info("Standardization: " + os.path.basename(xml_file_path))
                list_files_standardized.write(os.path.basename(xml_file_path)+"\n")
                list_files_standardized.flush()
    list_files_standardized.close()   
    logging.info("Standardization End")
                        
                                