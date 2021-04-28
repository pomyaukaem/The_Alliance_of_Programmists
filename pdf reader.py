import libpdf # эта библиотека должна быть установлена через
# pip.exe для интерпретатора, в котором она запускается
import re
import pprint

filename = "богуславский.pdf" # filename тут просто такой вот пока
file_content = libpdf.load(filename) # читаем pdf

pars = file_content.flattened.paragraphs # достаём из него параграфы
tabs = file_content.flattened.tables
# Разобраться с таблицами!!!
def cell_cleaner(cell):
    to_delete = 'Cell\(.+?\)\s'
    new = re.sub(to_delete, '', str(cell))
    return new


def text_roast(paragraphs):
    # Что бывает: name (название статьи и автор),
    # example (пример), footnote (сноска), header (заголовок главы),
    # text (текст абзаца), page (номер страницы)
    page_pattern = '^\s*[0-9]+\s*$' 
    example_pattern = '^\s*\([0-9]+?[а-я]?\).*?'
    footnote_pattern = '^[0-9]+\s*?[А-Яа-яA-Za-z«].*?'
    header_pattern = ['[0-9]+\.[0-9]*?\s[А-Я].*?$',
                       '[IVX]+?.?\s*[А-Я]?.*?$']
    meta_pattern = '^[А-Я\-\)\(\.\s]+$'

    descent = [] # Список списков [параграф, статус]
    page_edge = False # Переменная, отвечающая за то, был ли разорван текст
    # всякой ерундой на границе страниц
    
    for par in paragraphs:
        # Последнего \n в параграфах нет -> наличие \n
        # = параграф не из одной строки.
        if '\n' not in par:
            # перед нами номер страницы
            if re.match(page_pattern, par.strip('\s')) is not None:
                page_edge = True
                descent.append([par, 'разрыв страницы'])
            # перед нами заголовок 1
            elif re.match(header_pattern[0], par.strip('\s')) is not None:
                page_edge = False
                descent.append([par, 'header'])
            # перед нами заголовок 2
            elif re.match(header_pattern[1], par.strip('\s')) is not None:
                page_edge = False
                descent.append([par, 'header'])
            # перед нами пример
            elif re.match(example_pattern, par.strip('\s')) is not None:
                descent.append([par, 'example'])
            # перед нами сноска
            elif re.match(footnote_pattern, par.strip('\s')) is not None:
                page_edge = True
                descent.append([par, 'footnote'])
            # перед нами метаинфа
            elif re.match(meta_pattern, par.strip('\s')) is not None:
                descent.append([par, 'meta'])
            # перед нами чёрти что -> добавляем к последнему сегменту
            else:
                if len(descent) != 0:
                    descent.append([par, 'lost'])
                else:
                    descent.append([par, 'name'])
        # Если в параграфе 2 строки и больше
        else:
            # Если параграф оборван - присоединяем его к предыдущему.
            if par[0].islower():
                descent.append([par, 'lost'])
            else:
                # перед нами пример
                if re.match(example_pattern, par.strip('\s')) is not None:
                    descent.append([par, 'example'])
                # перед нами сноска
                elif re.match(footnote_pattern, par.strip('\s')) is not None:
                    page_edge = True
                    descent.append([par, 'footnote'])
                else:
                    descent.append([par, 'text'])
    #pprint.pprint(descent)
    return descent


def par_deleter(old):
    # Удалятель из списков
    new = []
    for every in old:
        if every[1] != 'delete':
            new.append(every)
    return new


def break_searcher(abc):
    # Эта функция ищет, где разорван абзац: ему не хватает начала (initial_break),
    # конца (ending_break), и того, и другого (both_break), или с ним всё ок (no_break)
    # Принимает на вход параграф [текст, статус], возвращает параграф
    # [текст, статус, где_разрыв]

    initial_break = 0
    ending_break = 0
    punctuation = '."»?!;'
    
    clean = abc[0].strip('\n ')
    if clean[0].islower():
        initial_break = 1
    if clean[-1] not in punctuation:
        ending_break = 1

    if initial_break == 1 and ending_break == 1:
        abc.append('both_break')
    elif initial_break == 1 and ending_break == 0:
        abc.append('initial break')
    elif initial_break == 0 and ending_break == 1:
        abc.append('ending break')
    else:
        abc.append('no break')

    return abc


def paragraph_glue(par_list):
    # Эта функция склеивает разорванные параграфы вместе
    new_par_list = []
    for i in range(1, len(par_list)):
        if par_list[i][2] != 'no break' and par_list[i][2] != 'ending break' and par_list[i-1][2] != 'no break' and par_list[i-1][2] != 'initial break':
            if par_list[i][1] == par_list[i-1][1] or par_list[i][1] == 'lost' or par_list[i-1][1] == 'lost':
                new_par_list[-1][0] += par_list[i][0]
                if new_par_list[-1][1] == 'lost':
                    new_par_list[-1][1] = par_list[i][1]
            else:
                new_par_list.append(par_list[i])
        else:
            new_par_list.append(par_list[i])
    return new_par_list



def text_fixer(undone_pars):
    # Эта функция разбирается со всеми lost и прочими недоразумениями
    done_pars = []

    # Отнесём всё, что до первого header или text к name, удалим оставшиеся
    # meta и удалим пустые абзацы
    beginning = True
    for each in undone_pars:
        if each[0] == '' or each[0] == '\n':
            each[1] = 'delete'
        if each[1] == 'meta':
            if beginning is True:
                each[1] = 'name'
            else:
                each[1] = 'delete'
        if each[1] == 'text' or each[1] == 'header':
            beginning = False
        done_pars.append(each)
    
    undone_pars = par_deleter(done_pars)

    # Вынесем все сноски в один список, а весь текст - в другой.
    text_list = []
    footnote_list = []

    for i in range(0, len(undone_pars)):
        now = undone_pars[i]
        if now[1] == 'footnote':
            footnote_list.append(now[0])
        elif now[1] != 'footnote' and now[1] != 'lost' and now[1] != 'разрыв страницы':
            text_list.append(now)
        elif now[1] == 'lost':
            n = i - 1
            while n >= 0:
                if undone_pars[n][1] != 'lost' and undone_pars[n][1] != 'footnote' and undone_pars[n][1] != 'разрыв страницы': 
                    text_list.append(now)
                    break
                elif undone_pars[n][1] == 'разрыв страницы':
                    text_list.append(now)
                    break
                elif undone_pars[n][1] == 'footnote':
                    footnote_list.append(now[0])
                    break
                else:
                    n = n - 1

    # Определяем, с какого конца неполноценны потеряшки, чтобы прикрепить их к
    # следующему или предыдущему неполноценному сегменту
    # + очищаем текст от переносов строки.
    linebreak_clean = []
    for txt in text_list:
        txt[0] = re.sub('\-\n', '', txt[0])
        txt[0] = re.sub('\n', ' ', txt[0])
        txt = break_searcher(txt)
        linebreak_clean.append(txt)
    text_list = paragraph_glue(linebreak_clean)

    # Ещё иногда из-за оформления статьи в примеры или заголовки попадают большие куски текста.
    # Мы хотим, чтобы звголовки и примеры занимали не больше 2-х строк, иначе считаем их текстом.
    # Будем считать, что в двух строках примерно 140 символов.
    # К тому же самое время приписать всем потеряшкам тег текст, как просто наиболее вероятный.
    for tt in text_list:
        if tt[1] == 'lost':
            tt[1] = 'text'
        if tt[1] == 'example' or tt[1] == 'header':
            if len(tt[0]) > 140:
                tt[1] = 'text'
    
    return text_list, footnote_list
  

good_pars = []
for each in pars:
    good_pars.append(str(each.text))
roasted_text = text_roast(good_pars)
final_paragraphs, final_footnotes = text_fixer(roasted_text)
