from Process.S3Processor import S3Processor
import config

if __name__ == '__main__':
    s = S3Processor()
    s.delete_all_obj(config.script_bucket)
    s.delete_all_obj(config.source_data_bucket)
    s.delete_all_obj(config.output_data_bucket)