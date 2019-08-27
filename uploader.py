import boto3
import os
import re
import glob
import time
import logging
from configparser import ConfigParser


class Uploader:

    """Delete last submitted model from bucket and upload most recent model to bucket.
    Option to upload specific checkpoint not implemented or tested yet.
    Option to backup last model not implemented or tested yet.
    Option to automatically submit model not implemented or tested yet.
    """

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
                
    def __init__(self):
        
        config = self.load_configuration()

        logging.info('Loading config variables.')

        self.m_path = config['m_path']
        self.s3 = boto3.resource('s3')
        self.s3_bucket_name = config['s3_bucket_name']
        self.s3_bucket = self.s3.Bucket(self.s3_bucket_name)
        self.s3_prefix = config['s3_prefix']
        self.bot = config.getboolean('bot')
        self.bot_sleep = config.getint('bot_sleep')*60
        
        self.checkpoint = None # not implemented or tested yet
        self.backup_last_model = False # not implemented or tested yet
        self.auto_submit = False # not implemented or tested yet

        logging.info('Variables loaded.')

        logging.info(f'Bot is set to {config["bot"]}.')
        
        if self.bot:
            self.bot()
        else:
            self.action()

    def load_configuration(self):
        config = ConfigParser()
        try:
            config.read('config.ini')
            return config['Uploader']
        except FileNotFoundError:
            logging.warning('Please create a config.ini file in the same directory as the uploader.')

    def bot(self):
        while True:
            logging.info(f'Bot next action in {self.bot_sleep/60} minutes.')
            time.sleep(self.bot_sleep)
            self.action()

    def action(self):
        logging.info('Initializing action.')
        self.objects_to_delete = self.get_objects_to_delete()
        self.delete_from_bucket()
        self.files_to_upload = self.get_files_to_upload()
        self.upload_to_bucket()
        logging.info('Action finished.')
        
    def get_objects_to_delete(self):
        try:
            content = self.s3.meta.client.list_objects(Bucket=self.s3_bucket_name, Prefix=self.s3_prefix)['Contents']
            return [{'Key': content[i]['Key']} for i in range(len(content))]     
        except KeyError:
            logging.warning('No files were identified. Please verify config.ini file or check your s3 bucket.')
            return None

    def delete_from_bucket(self):
        if self.objects_to_delete:
            self.s3_bucket.delete_objects(Delete={'Objects': self.objects_to_delete})
            logging.info('The files from the s3 bucket object were deleted.')
        else:
            logging.warning('No files were deleted from s3 bucket, since the object had no files.')
    
    def get_files_to_upload(self):
        if not self.checkpoint:
            with open(os.path.join(self.m_path, 'checkpoint'), 'r') as file:
                self.checkpoint = re.search('(\d+)', file.readline()).group(1)
        
        model_files = glob.glob(f'{self.m_path}/*{self.checkpoint}*')
        custom_files = [f'{self.m_path}/checkpoint', f'{self.m_path}/model_metadata.json']
        return custom_files + model_files
        
    def upload_to_bucket(self):
        count = 0
        for file in self.files_to_upload:
            file_name = file.split('/')[-1]
            self.s3_bucket.upload_file(file, Key=os.path.join(self.s3_prefix, 'model', file_name))
            logging.info(f'{file_name} uploaded to s3 bucket.')
            count += 1
        logging.warning(f'Model checkpoint {self.checkpoint} uploaded to s3 bucket.')
        logging.warning(f'A total of {count} files were uploaded to s3 bucket.')


if __name__ == '__main__':
    Uploader()

    