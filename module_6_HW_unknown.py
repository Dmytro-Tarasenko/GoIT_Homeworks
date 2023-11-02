import os
import shutil
import re
from sys import argv, exit
#import pathlib не дозволяє показати отримані навички роботи зі строками та т.ін)))

folder_to_sort = ''

IGNORE = ['images', 'documents', 'audio', 'video', 'archives', 'unknown']

extensions_dict = {
    'video' : ['AVI', 'MP4', 'MOV', 'MKV'],
    'audio' : ['MP3', 'OGG', 'WAV', 'AMR'],
    'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'XLS', 'ODT'],
    'images' : ['JPEG', 'PNG', 'JPG', 'SVG', 'BMP'],
    'archives' : []
}

stat_dict = {
    'video' : {'AVI' : {'quant' : 0,
                        'list' : [] },
                'MP4' : {'quant' : 0,
                         'list' : [] },
                'MOV' : {'quant' : 0,
                         'list' : [] },
                'MKV' : {'quant' : 0,
                         'list' : [] }
                },
    'audio' : {'MP3' : {'quant' : 0,
                        'list' : [] },
                'OGG' : {'quant' : 0,
                         'list' : [] },
                'WAV' : {'quant' : 0,
                         'list' : [] },
                'AMR' : {'quant' : 0,
                         'list' : [] },
                },
    'documents': {'DOC' : {'quant' : 0,
                           'list' : [] },
                 'DOCX' : {'quant' : 0,
                           'list' : [] },
                 'TXT' : {'quant' : 0,
                           'list' : [] },
                 'PDF' : {'quant' : 0,
                           'list' : [] },
                 'XLSX' : {'quant' : 0,
                           'list' : [] },
                 'PPTX' : {'quant' : 0,
                           'list' : [] },
                 'XLS' : {'quant' : 0,
                          'list' : [] },
                 'ODT' : {'quant' : 0,
                          'list' : [] },
                },
    'images' : {'JPEG' : {'quant' : 0,
                         'list' : [] },
                'PNG' : {'quant' : 0,
                         'list' : [] },
                'JPG' : {'quant' : 0,
                         'list' : [] },
                'SVG' : {'quant' : 0,
                         'list' : [] },
                'BMP' : {'quant' : 0,
                         'list' : [] },
                },
    'archives' : {},
    'unknown' : {}
}

#Великі літери Ш, Ч та ін. передаються двома великими SH, CH etc.
TRANS_FULL = {1072: 'a', 1040: 'A', 1073: 'b', 1041: 'B', 1074: 'v', 1042: 'V', 
              1075: 'g', 1043: 'G', 1076: 'd', 1044: 'D', 1077: 'e', 1045: 'E', 
              1105: 'e', 1025: 'E', 1078: 'j', 1046: 'J', 1079: 'z', 1047: 'Z', 
              1080: 'i', 1048: 'I', 1081: 'j', 1049: 'J', 1082: 'k', 1050: 'K', 
              1083: 'l', 1051: 'L', 1084: 'm', 1052: 'M', 1085: 'n', 1053: 'N', 
              1086: 'o', 1054: 'O', 1087: 'p', 1055: 'P', 1088: 'r', 1056: 'R', 
              1089: 's', 1057: 'S', 1090: 't', 1058: 'T', 1091: 'u', 1059: 'U', 
              1092: 'f', 1060: 'F', 1093: 'h', 1061: 'H', 1094: 'ts', 1062: 'TS', 
              1095: 'ch', 1063: 'CH', 1096: 'sh', 1064: 'SH', 1097: 'sch', 1065: 'SCH', 
              1098: '', 1066: '', 1099: 'y', 1067: 'Y', 1100: '', 1068: '', 1101: 'e', 
              1069: 'E', 1102: 'yu', 1070: 'YU', 1103: 'ya', 1071: 'YA', 1108: 'je', 
              1028: 'JE', 1110: 'i', 1030: 'I', 1111: 'ji', 1031: 'JI', 1169: 'g', 1168: 'G'}

#Великі літери Ш, Ч та ін. передаються великою та маленькою Sh, Ch etc.
TRANS_CAPT = {1072: 'a', 1040: 'A', 1073: 'b', 1041: 'B', 1074: 'v', 1042: 'V', 
              1075: 'g', 1043: 'G', 1076: 'd', 1044: 'D', 1077: 'e', 1045: 'E', 
              1105: 'e', 1025: 'E', 1078: 'j', 1046: 'J', 1079: 'z', 1047: 'Z', 
              1080: 'i', 1048: 'I', 1081: 'j', 1049: 'J', 1082: 'k', 1050: 'K', 
              1083: 'l', 1051: 'L', 1084: 'm', 1052: 'M', 1085: 'n', 1053: 'N', 
              1086: 'o', 1054: 'O', 1087: 'p', 1055: 'P', 1088: 'r', 1056: 'R', 
              1089: 's', 1057: 'S', 1090: 't', 1058: 'T', 1091: 'u', 1059: 'U', 
              1092: 'f', 1060: 'F', 1093: 'h', 1061: 'H', 1094: 'ts', 1062: 'Ts', 
              1095: 'ch', 1063: 'Ch', 1096: 'sh', 1064: 'Sh', 1097: 'sch', 1065: 'Sch',
              1098: '', 1066: '', 1099: 'y', 1067: 'Y', 1100: '', 1068: '', 1101: 'e', 
              1069: 'E', 1102: 'yu', 1070: 'Yu', 1103: 'ya', 1071: 'Ya', 1108: 'je', 
              1028: 'Je', 1110: 'i', 1030: 'I', 1111: 'ji', 1031: 'Ji', 1169: 'g', 1168: 'G'}

RE_VERB_PATTERN = r'[avdizu\*]'

verbose_pattern = set('avdizu')

def usage(bad_param=''):
    """Prints usage info"""
    print(f'\n{"Super Sorter v0.0.0.1-pre-a":=^80}\n')
    if bad_param:
        print(f'"{bad_param}" is not a valid path to a folder or such folder does not exist\n')
    print(f'Usage: python {argv[0]} <folder_to_sort> [-v [avdizu|*]]\n')
    print(f'{"<folder_to_sort>":<18} full path to the folder which content needs to be sorted')
    print(f'{"-v":<10} with this optional parameter outputs file names in respective folders:')
    print(f'\t{"a":<10} for audio files')
    print(f'\t{"v":<10} for video files')
    print(f'\t{"d":<10} for documents')
    print(f'\t{"i":<10} for image files')
    print(f'\t{"z":<10} for archive files')
    print(f'\t{"u":<10} for unknown files')
    print(f'\t{"*":<10} for all files, default value fo -v')
    print(f'\texample: "-v adu" means display filenames for audio files, documents and unknown files')
    

def get_archives_types():
    """Returns a list of registered archive extensions for shutil archive methods and fills extension_dict['archives']"""
    __lst = []
    __lst_stat = []
    for record in shutil.get_archive_formats():
        __lst.append(record[0].upper())
        __lst_stat.append((record[0].upper(), {'quant' : 0, 'list' : []}))
    return __lst, dict(__lst_stat)


def extend_unknown(ext):
    __lst = stat_dict['unknown']
    ext = ext if ext else 'no_ext'
    if ext not in __lst:
        __dict = {ext: {'quant' : 0, 'list' : [] }}
        stat_dict['unknown'].update(__dict)


def find_category(ext):
    """Returns type of file by provided extension and extends 'unknown' types"""
    if ext in extensions_dict['archives']:
        return 'archives'
    elif ext in extensions_dict['audio']:
        return 'audio'
    elif ext in extensions_dict['documents']:
        return 'documents'
    elif ext in extensions_dict['images']:
        return 'images'
    elif ext in extensions_dict['video']:
        return 'video'
    else: 
        extend_unknown(ext)
    return 'unknown'

def normalize(name):
    
    def replace_fn(match):
        return '_'*len(match.group(0))
    
    name = name.translate(TRANS_CAPT)
    name = re.sub(r'[^a-zA-Z_\d]+', replace_fn, name)
    
    return name

def add_stat(category, path, ext):
    ext = ext if ext else 'no_ext'
    stat_dict[category][ext]['list'].append(path)
    stat_dict[category][ext]['quant'] += 1


def process_file(path):
    """Does main sorting stuff"""
    file_name = path.rsplit(os.path.sep, maxsplit=1)[1]
    file_dir = path.rsplit(os.path.sep, maxsplit=1)[0]
    
    good_file = True # non zero length archive flag
    
    if len(file_name.split('.')) == 1:
        extension = ''
        pure_name = file_name
    else:
        extension = file_name.split('.')[-1]
        pure_name = file_name.rsplit('.', maxsplit = 1)[0]#кількість точок у назві файлу не обмежена
    category = find_category(extension.upper())
    norm_name = normalize(pure_name)
    if pure_name != norm_name:
            new_path = os.path.join(file_dir,f'{norm_name}.{extension}') if extension else os.path.join(file_dir,norm_name)
            os.rename(path, new_path)
            path = new_path
            file_name = new_path.rsplit(os.path.sep, maxsplit=1)[1]
    # if category != 'unknown':
    dest_path = os.path.join(folder_to_sort,f'{category}{os.path.sep}{file_name}')
    if category == 'archives':
        dest_path = dest_path.rsplit(".", maxsplit=1)[0]
        try:
            shutil.unpack_archive(path, dest_path)
        except:
            print(f'Warning: {path} is a wrong archive file and will be removed.')
            good_file = False # bad archive is deleted and does not go to statistic
        os.remove(path)
    else:
        shutil.move(path, dest_path)
    # else:
    #     file_name = path
    if good_file: # bad archive is deleted and does not go to statistic
        add_stat(category, file_name, extension.upper())
   

def walk_tree(root_path):
    """Name says everything"""
    cd_list = os.listdir(root_path)

    # if len(cd_list) == 0:
    #     os.rmdir(root_path)
    for item_ in cd_list:
        full_path = os.path.join(root_path, item_)
        if os.path.isfile(full_path):
            process_file(full_path)
        else:
            if item_ not in IGNORE:
                walk_tree(full_path)
   
    cd_list = os.listdir(root_path)
    if len(cd_list) == 0:
        os.rmdir(root_path)


def show_stat():
    all_n = 0
    for record in list(stat_dict):
        typestr = f'{record}' if record.endswith('s') else f'{record} files' 
        cat_num = 0
        buff = '\n'
        for extension in list(stat_dict[record]):
            additive = stat_dict[record][extension]['quant']
            file_s = 'file' if additive == 1 else 'files' #plural 's'
            if additive == 0: 
                    continue
            cat_num += additive
            buff += f'\n{additive} {extension} {file_s}: '
            numerator = 1
            for file_name in stat_dict[record][extension]['list']:
                gap = len(f'{additive} {extension} {file_s}: ') + 1
                buff = (buff + f'{numerator}. {file_name}\n') if numerator == 1 else (buff + f'{numerator:>{gap}}. {file_name}\n') 
                numerator += 1
        
        #no files no moves      
        if cat_num == 0:
            continue
        #what kind of files we want to be displayed
        match record:
            case 'audio':
                if 'a' not in verbose_pattern:
                    continue            
            case 'video':
                if 'v' not in verbose_pattern:
                    continue
            case 'images':
                if 'i' not in verbose_pattern:
                    continue
            case 'documents':
                if 'd' not in verbose_pattern:
                    continue
            case 'archives':
                if 'z' not in verbose_pattern:
                    continue
            case 'unknown':
                if 'u' not in verbose_pattern:
                    continue

        is_are = 'is' if cat_num == 1 else 'are'
        typestr = typestr if cat_num != 1 else typestr.removesuffix('s') #not plural no 's'
        title_str = f'There {is_are} {cat_num} {typestr} in {os.path.join(folder_to_sort,record)}:' if record != 'unknown' else f'There {is_are} {cat_num} {typestr}:'
        print(title_str, buff)
        all_n += cat_num
    print(f'Total: {all_n} files`ve been processed.')  

def main():
    global verbose_pattern
    global folder_to_sort
    
    #Have we got a proper argument
    if len(argv) == 1:
        usage()
        exit(1)
    
    args_lst = argv[1].split(' ')
    folder_to_sort = args_lst[0]
    
    if not os.path.exists(folder_to_sort) or os.path.isfile(folder_to_sort):
        usage(folder_to_sort)
        exit(1)
    
    #Retrieve archive types registered in shutil
    extensions_dict['archives'], stat_dict['archives'] = get_archives_types()

    #Making verbose pattern
    if len(args_lst) > 1:
        if args_lst[1] == '-v':
            if len(args_lst) == 2:
                print('Warning: wrong parameters are passed to -v argument. Verbose output is set to full.')
            else:
                verbose_pattern = set(re.findall(RE_VERB_PATTERN, args_lst[2]))
                if len(verbose_pattern) == 0:
                    print('Warning: wrong parameters are passed to -v argument. Verbose output is set to full.')
                    verbose_pattern = set('avdizu')
                if args_lst[2] == '*':
                    verbose_pattern = set('avdizu')
                if len(verbose_pattern) >= 2 and '*' in verbose_pattern:
                    print('Warning: "*" overrides other passed parameters  to -v argument. Verbose output is set to full.')
                    verbose_pattern = set('avdizu')
        if '-v' not in args_lst:
            verbose_pattern = set('_')
        
    #Creating initial folder structure
    for folder in IGNORE:
        full_path = os.path.join(folder_to_sort, folder)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        elif os.path.isfile(full_path):
             os.remove(full_path)
             os.mkdir(full_path)
    
    #Do your job!
    walk_tree(folder_to_sort)

    #Perform final clean of empty IGNORED folders
    for item in IGNORE:
        path = os.path.join(folder_to_sort, item)
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
    
    if verbose_pattern != set('_'):
        show_stat()
    
    exit(0)
    

if __name__ == '__main__':
    main()

