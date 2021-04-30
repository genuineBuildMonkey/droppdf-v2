from celery import shared_task
import subprocess
import os

from hashlib import md5

from django.conf import settings

from pdfrw import PdfReader, PdfWriter

from apps.utils.api_aws import S3 
from apps.utils.files import save_temp_file, cleanup_temp_file, check_ocr_file_exists, randword

from apps.models import OCRUpload

class MaxProcessesExceededError(Exception):
    pass


class FileInProcessError(Exception):
    '''raised when file with identical hash is already being processed'''
    pass


@shared_task
def ocr_pdf(filename, parent_id, md5_hash, force_flag):

    if not os.path.exists('/tmp/ocr_clients'):
        os.makedirs('/tmp/ocr_clients')

    lockfile = os.path.join('/tmp/ocr_clients', md5_hash)

    try:
        #prevent too many heavy ocr processes from running at once
        current_process_count = len(os.listdir('/tmp/ocr_clients'))

        print('--', current_process_count, int(settings.MAX_SIM_OCR_PROCESSES), '---')

        if current_process_count >= int(settings.MAX_SIM_OCR_PROCESSES):
            raise MaxProcessesExceededError()

        #add to current process count with file
        try:
            f = open(lockfile, 'x')
            f.close()
        except FileExistsError:
            raise FileInProcessError()

        input_path = os.path.join('/tmp', filename)

        #download file and save 
        s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

        file_obj = s3.download_fileobj_from_bucket(filename)
        #file_obj.save(input_path)
        with open (input_path, 'wb') as tmpfile:
            tmpfile.write(file_obj.getbuffer())
            
       
        basename = '.'.join(filename.split('.')[:-1])
        if force_flag:
            processed_filename = basename + '_ocr_force.pdf'
            force_flag = True
        else:
            processed_filename = basename + '_ocr.pdf'
            force_flag = False

        output_path = os.path.join('/tmp', processed_filename)

        if force_flag:
            f = '--force-ocr'

        else:
            f = ''

        cmd = '/usr/bin/ocrmypdf {} {} {}'.format(f, input_path, output_path)

        rslt = subprocess.check_output(cmd, shell=True)

        #save to s3 
        with open(output_path, 'rb') as file_:
            s3.save_to_bucket(processed_filename, file_)

            file_.seek(0)

            hash_ = md5(file_.read()).hexdigest()

        #record to db
        ref = OCRUpload(filename=processed_filename, md5_hash=hash_,
                is_original=False, is_forced=force_flag, parent_id=parent_id)

        ref.save()

        #remove from process count 
        os.remove(lockfile)

        cleanup_temp_file(filename)
        cleanup_temp_file(processed_filename)

    except Exception as e:
        print(e)

        try:
            os.remove(os.path.join('/tmp/ocr_clients', md5_hash))
            cleanup_temp_file(filename)
            cleanup_temp_file(processed_filename)
        except:
            pass

        raise e


@shared_task
def refingerprint_pdf(filename, copy_count, suffix):

    #content = PdfReader(io.BytesIO(file_content))
    content = PdfReader('/tmp' + filename)

    #make save directory 
    rand_path = randword(9)
    fingerprint_dir = os.path.join('/tmp/', rand_path)
    os.makedirs(fingerprint_dir)

    if content.ID is None:
        file_id = 'No ID'
    else:
        file_id = str(content.ID[0]).replace('<', '').replace('>', '')\
                .replace('(', '').replace(')', '')


    #bad file_ids can contain strange characters
    try:
        file_id.encode('utf-8').strip()
    except UnicodeDecodeError:
        file_id = 'Unreadable'

    print(file_info, copy_count)

    for copy_index in range(copy_count):
        try:
            print(copy_index)

            if suffix and suffix != '':
                save_filename = filename + '-' + suffix + '-' + str(copy_index + 1) + extension
            else:
                save_filename = filename + '-' + str(copy_index + 1) + extension

            file_path = os.path.join(fingerprint_dir, save_filename)

            print(file_path)

            #static_link = os.path.join('/pdf', save_filename)
            download_link = os.path.join('/fingerprinter/download/', save_filename)

            #print('x', download_link)

            #try:
            content = PdfReader(io.BytesIO(file_content))
            #except Exception as e:
                #print(e)


            #add some random meta data
            content.Info.randomMetaData = binascii.b2a_hex(os.urandom(20)).upper()

            print('AAA', filename)
            filename = filename.strip().encode('utf-8')

            #change id to random id
            md = hashlib.md5()

            #md = hashlib.md5(filename)
            #md = _randomword(5)

            print('d')
            md.update(str(time.time()))
            md.update(os.urandom(10))
            print('xx')

            new_id = _randomword(10)

            print(new_id)

            print(md.upper)

            new_id = md.hexdigest().upper()

            #keep length 32
            new_id = new_id[0:32]

            while len(new_id) < 32:
                new_id += random.choice('0123456789ABCDEF')

            print('c')

            content.ID = [new_id, new_id]

            print('e', file_path)

            PdfWriter(file_path, trailer=content).write()

            print('aaasd')

            shutil.copy(file_path, annotation_path)

            print('f')

            download_link = '/fingerprinter/download/' + save_filename 

            copy_info = {'filename': save_filename,
                    'download_link': download_link, 'id': content.ID[0]}

        except Exception as e:
            #exc_type, exc_value, exc_tb = sys.exc_info()
            #tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
            #print(''.join(tb.format_exception_only()))
            print(e)

        #print(copy_info)

        #processed_files.append(copy_info)
        print('ok')

