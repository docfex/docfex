from elasticsearch_dsl.field import Text, Object
from .base import EsBase, BaseDoc
from elasticsearch.client.ingest import IngestClient
from elasticsearch_dsl import InnerDoc


attachment_fields = ['encoded_obj', 'stored_attachment']

class AttachmentEncDoc(InnerDoc):
    '''
    Provide attachment as base64 decoded ascii string at enc_attachment property
    '''
    enc_attachment = Text(index=False)

class AttachmentDoc():
    '''
    Document class to store a file as attachment

    :param enc_attachment: file as base64 encoded ASCII-string
    :type enc_attachment: Field.Text
    :param stored_attachment: field where the decoded file will be written to as JSON-object
    :type stored_attachment: Field.Object
    '''
    encoded_obj = Object(AttachmentEncDoc, enabled=False)
    stored_attachment = Object(index_options='offsets')


def ingest_attachment(client, pipe_id='esattachment'):
    '''
    Prepares a pipeline for the attachment to be saved.
    Pipeline id = 'esattachment'
    '''
    p = IngestClient(client)
    p.put_pipeline(id=pipe_id, body={
        'description': "Extract attachment information",
        'processors': [
            {
                "attachment": {
                    "field": "encoded_obj.enc_attachment",
                    "target_field": "stored_attachment",
                    "indexed_chars": "-1",
                    "properties": ["content", "title"]
                }
            }
        ]
    })


