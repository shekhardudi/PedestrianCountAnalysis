import boto3
import config

class Crawler:

    def __init__(self):
        self.client = boto3.client('glue')
        self.db = None

    def add_db(self):
        self.db = self.client.create_database(DatabaseInput={'Name':config.crawler_db})

    def add_crawler(self):
        self.client.create_crawler(Name=config.crawler_name,
                                Role='AccessRoleForGlue',
                                DatabaseName=config.crawler_db,
                                Targets={
                                            'S3Targets': [
                                                {
                                                    'Path': 's3://{}'.format(config.bucket_source),
                                                },
                                            ]})
    
    def start_crawler(self):
        response = self.client.start_crawler(Name=config.crawler_name)


if __name__ == '__main__':

    c = Crawler()
    c.add_db()
    c.add_crawler()
    c.start_crawler()

