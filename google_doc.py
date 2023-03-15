from google.oauth2 import service_account
import googleapiclient.discovery


def main():
    SCOPES = ['https://www.googleapis.com/auth/documents']
    SERVICE_ACCOUNT_FILE = 'smm-planer-2ff621f473e2.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    doc_id = '1Pxy42B0-k8lsnqPLL3UXJj8JpA6jlVzsTBiXOHHZYwU'
    doc_admin = googleapiclient.discovery.build('docs', 'v1', credentials=credentials)
    doc = doc_admin.documents().get(documentId=doc_id).execute()
    print(doc)


if __name__ == '__main__':
    main()