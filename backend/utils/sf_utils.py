import json
from datetime import datetime
from functools import partial
from utils.multithread_utils import multi_thread
from utils.s3_utils import upload_file_to_s3, download_from_s3

s3_params_bucket = "step-functions-params"


def upload_params(params, bucket_name="step-functions-params", directory_name="", directory_prefix=True):
    """
    Upload Parameters to an S3 bucket and return the list of files uploaded.
    It is used for step functions states machines to process large payloads
    Args:
        params (list): List of parameters, each item will be uploaded in a file
        directory_name (str): Name of the directory where the files will be uploaded in the S3 bucket (optional)
        bucket_name (str): The name of the bucket where the files will be uploaded

    Returns:
        s3_params (list): List of the filename uploaded along with the directory and the bucket

    """
    now_date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    directory_name = directory_name + now_date if directory_prefix else directory_name

    params_filename = [(f"params{i}.json", heaters_info) for i, heaters_info in enumerate(params)]
    partial_upload_single_params_file = partial(upload_single_params_file, bucket_name=bucket_name,
                                                directory=directory_name)
    s3_params = multi_thread(partial_upload_single_params_file, params_filename, 20)
    return s3_params


def upload_single_params_file(params_filename, bucket_name, directory):
    filename, heaters_info = params_filename
    upload_file_to_s3(json.dumps(heaters_info), filename, bucket_name, directory)
    return {"filename": filename, "bucket": bucket_name, "directory": directory}


def upload_divided_params(params, divider, bucket_name="step-functions-params", directory_name=""):
    """
    Upload the list of the params but with dividing it so sublist before.
    Examples:
        params = [ 1, 2, ... 100]
        divider = 10
        params_divided = [ [1, 2, .. 10], [11, 12, .. 20], ... [91, 92.. 100]]
    """
    return upload_params(divide_list(params, divider), bucket_name, directory_name)


def divide_list(list_to_divide, divider):
    """
    Divide list_to_divider containing x item into another list containing multiple lists with divider items
    Args:
        list_to_divide (list): The list to divide
        divider (int): Max number of item in a list

    Returns :
        divided_lists (list): The global list containing "mini-lists"
    Examples:
        list_to_divide = [0,1,2,...,10]
        divider = 3
        divided_lists = [ [0,1,2], [3,4,5], [6,7,8], [9,10] ]
    """
    return [list_to_divide[x:x + divider] for x in
            range(0, len(list_to_divide), divider)]


def download_parameters_from_s3(file_params):
    filename_params = file_params['filename']
    bucket_params = file_params['bucket']
    directory_params = file_params.get('directory')
    return json.loads(download_from_s3(filename_params, bucket_params, directory_params))
