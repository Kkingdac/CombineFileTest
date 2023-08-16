import datetime
import sys
from configparser import ConfigParser
import os
import shutil
import chardet
import pandas as pd
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


def release(init_file: str, folder: str) -> None:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    source_excel_file = os.path.join(base_path, init_file)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(os.path.join(folder, init_file)):
        shutil.copy(source_excel_file, folder)


def init() -> None:
    release('config.ini', './')
    release('template.xlsx', './Template/')


def config(key: str) -> str:
    config_file = './config.ini'
    con = ConfigParser()
    if not os.path.exists(config_file):
        init()
    con.read(config_file)
    try:
        con['config'][key]
    except KeyError:
        init()
        con.read(config_file)
    finally:
        return con['config'][key]


def get_files(convert_folder: str, result_folder: str, backup_folder: str) -> list:
    if not os.path.exists(convert_folder):
        os.mkdir(convert_folder)
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
    return os.listdir(convert_folder)


if __name__ == '__main__':
    # initialize variables
    init()
    convert_path = config('convert_path')
    result_path = config('result_path')
    backup_path = config('backup_path')
    csv_to_excel = config('csv_to_excel')
    start_line = int(config('start_line'))
    file_name = config('result_name')
    template = config('template_path')
    content = []
    remove_columns = ['Source Id']
    timestamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    csv_data = []
    template_sheet = config('OSJE_Template_Sheet')
    # combine excel files
    for file in tqdm(get_files(convert_folder=convert_path, result_folder=result_path, backup_folder=backup_path)):
        keys = pd.read_excel(f'{convert_path}{file}', sheet_name=None, engine='openpyxl').keys()
        details, sheet_name = [pd.read_excel(f'{convert_path}{file}', sheet_name=template_sheet,
                                             engine='openpyxl'), template_sheet] \
            if template_sheet in keys \
            else [pd.read_excel(f'{convert_path}{file}', engine='openpyxl'), 0]
        line = 0 \
            if details.head(0).columns[0] == 'ProfileName' \
            else start_line
        content.append(pd.read_excel(f'{convert_path}{file}', header=line, sheet_name=sheet_name, engine='openpyxl'))
        shutil.move(f'{convert_path}{file}', f'{backup_path}{timestamp}-{file}')
        print(file)
        print(content)
    if content:
        print('Combine Start')
        df = pd.concat(content, axis=0)
        filetype = ''
        line = 0
        try:
            df['Entity'] = df['Entity'].fillna('Unknown')
            df = df[~df['Entity'].str.contains('E#')]
            df = df[~df['Entity'].str.contains('Unknown')]
            # df = df.drop(columns=remove_columns)
        except KeyError:
            filetype = 'M_Dim'
            print('Combining Multi-Dim')
            pass
        else:
            filetype = 'OS_JE'
            line = 25
            print('Combining OS JE')
        finally:
            target_file = f'{result_path}{filetype}-{file_name}-{timestamp}.xlsx'
            match filetype:
                case 'OS_JE':
                    shutil.copy(f'{template}template.xlsx', target_file)
                    with pd.ExcelWriter(target_file, mode='a', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, startrow=line, sheet_name='OS Template', index=False, header=False)
                case 'M_Dim':
                    df.to_excel(target_file, index=False)
            print('Combine Complete')
    # convert csv to excel
    for file in tqdm(get_files(convert_folder=csv_to_excel, result_folder=result_path, backup_folder=backup_path)):
        with open(f'{csv_to_excel}{file}', 'rb') as csv_file:
            encode = chardet.detect(csv_file.read())['encoding']
        csv_data.append(pd.read_csv(f'{csv_to_excel}{file}', encoding=encode))
        shutil.move(f'{csv_to_excel}{file}', f'{backup_path}{timestamp}-{file}')
    if csv_data:
        print('Convert Start')
        pd.concat(csv_data, axis=0).to_excel(f'{result_path}M_Dim-{file_name}-{timestamp}.xlsx', index=False)
        print('Convert Complete')
