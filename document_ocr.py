import os
import yaml
from pathlib import Path
import pandas as pd
from google.cloud import documentai
from google.api_core.client_options import ClientOptions

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_ocr.json'
def trim_text(text: str):
    """
    Remove extra space characters from text (blank, newline, tab, etc.)
    """
    return text.strip().replace("\n", " ")

def get_text_from_pdf_ocr(file_path):
    with open('keys.yml', 'r') as file:
                documentAi = yaml.safe_load(file)
    
    print ('<=== read file configuration ===>')
    endpoint = documentAi['google_api']['endpoint']
    location = documentAi['google_api']['location']
    project_id = documentAi['google_api']['project_id']
    processador_id = documentAi['google_api']['processador_id']
    try:   
        _mime_type = 'application/pdf'
        client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{location}-{endpoint}")
        )

        #Process and Project Information in GCP
        _name = client.processor_path(project_id, location, processador_id)

        #Read document 
        with open(file_path, "rb") as image:
            image_content = image.read()

        #Create document instance to GCP Services Document AI
        _raw_document = documentai.RawDocument(
            content = image_content,
            mime_type = _mime_type
        )

        #Call google cloud service in Document AI
        _request = documentai.ProcessRequest(
            name = _name,
            raw_document = _raw_document
        )

        #Process response
        response = client.process_document(request = _request)

        #Get document response from GCP
        document = response.document
        return document.text

    except Exception as e:
        print (e)
        return None
    
def get_text_from_pdf_formParser(file_path):
      endpoint = 'documentai.googleapis.com'
      location = 'us'
      project_id = 'ocrdocumentprocess'
      processador_id = '9c784433e4145c9e'

      try:   
          _mime_type = 'application/pdf'
          client = documentai.DocumentProcessorServiceClient(
              client_options=ClientOptions(api_endpoint=f"{location}-{endpoint}")
          )

          #Process and Project Information in GCP
          _name = client.processor_path(project_id, location, processador_id)

          #Read document 
          with open(file_path, "rb") as image:
              image_content = image.read()

          #Create document instance to GCP Services Document AI
          _raw_document = documentai.RawDocument(
              content = image_content,
              mime_type = _mime_type
          )

          #Call google cloud service in Document AI
          _request = documentai.ProcessRequest(
              name = _name,
              raw_document = _raw_document
          )

          #Process response
          response = client.process_document(request = _request)

          #Get document response from GCP
          document = response.document
          entities = document.entities
          for entity in entities:
                print(f'Detect key: {entity.type_} = value {entity.mention_text} with con confidence {round(entity.confidence,4)}')
          return document

      except Exception as e:
           print (e)
      return None



if __name__ == '__main__':
    file_path = [
        '.\documents\Scan.pdf',
        '.\documents\\form-cms1500.pdf'
        ]
    for path in file_path:
        infoFile = Path(path)
        if infoFile.is_file:
            document = get_text_from_pdf_formParser(path)
            print(f"**************File Name {infoFile.name}**************************")
            print('****************************************')
            if document != None:
                names = []
                name_confidence = []
                values = []
                value_confidence = []

                for page in document.pages:
                    for field in page.form_fields:
                        # Get the extracted field names
                        names.append(trim_text(field.field_name.text_anchor.content))
                        # Confidence - How "sure" the Model is that the text is correct
                        name_confidence.append(field.field_name.confidence)

                        values.append(trim_text(field.field_value.text_anchor.content))
                        value_confidence.append(field.field_value.confidence)

                # Create a Pandas Dataframe to print the values in tabular format.
                df = pd.DataFrame(
                    {
                        "Field Name": names,
                        "Field Name Confidence": name_confidence,
                        "Field Value": values,
                        "Field Value Confidence": value_confidence,
                    }
                )

                print(df)

            #print(document.text)
            print('****************************************')


    
