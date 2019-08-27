# deepracer-automation
Personal repository for scripts that automate deepracer common tasks for when deepracer is ran locally. For more information, refer to https://github.com/crr0004/deepracer.

## Uploader
This script uploads the last submitted model from your s3 bucket object and uploads most recent model to bucket.

## Configuration

The config.ini file is loaded into the scripts.
The config.ini should be filled as follows.

```
[Uploader]
s3_bucket_name = # s3 bucket into which are saved the model files
s3_prefix = # s3 prefix that references to the model
m_path = # absolute path to your bucket model
bot = # ON or OFF
bot_sleep = # True of False
backup_last_model = # True or False (set to False, not implemented yet)
```
