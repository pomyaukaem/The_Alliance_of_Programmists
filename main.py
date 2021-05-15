#библиотеки libpdf и nltk должны быть установлены на компьютер через pip install
from nltk.stem.snowball import SnowballStemmer
snowball = SnowballStemmer("russian")
from collections import defaultdict
import libpdf
import re
import math
import pandas as pd

filename = input('Введите путь к вашему pdf-файлу:')
file_content = libpdf.load(filename) # читаем pdf

pars = file_content.flattened.paragraphs # достаём из него параграфы
tabs = file_content.flattened.tables
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

for fp in final_paragraphs:
    fp[0] = re.sub('  ', ' ', fp[0])
    
# ПРЕДЛОЖЕНИЗАТОР

def sentence_border_searcher(text_read):
    # Эта функция принимает на вход абзац и выдаёт список предложений абзаца
    
    if '.' not in text_read and '?' not in text_read and '!' not in text_read and ';' not in text_read:
        return [text_read,]
    
    text_read = text_read + ' '

    list_commas = []
    q = 0
    for symbol in text_read:
        q += 1
        if symbol == ';' or symbol == '?' or symbol == '.' or symbol == '!':
            list_commas.append(q-1) 
    new_list_commas = []
    
    for index in list_commas:
        #если следующий после "точки" символ - не пробел и не перенос строки, то это не конец предложения
        if text_read[index+1] == ' ' or text_read[index+1] == '\n':
            new_list_commas.append(index)
    list_commas = new_list_commas

    for index in list_commas[0:-1]:
        if  type(text_read[index+2]) == str:
            if text_read[index+2].islower() is True:
                list_commas.remove(index)
            else:
                #вводим паттерн для инициалов типа В. В. Виноградов или М. Дж. Николсон
                pattern_1 = '.*[А-Я][а-я]?\.\s?[А-Я]?[а-я]?\.?\s?[А-Я].*'
                if re.match(pattern_1, text_read[index-2:index+8]) is not None:
                    list_commas.remove(index)

    #точка есть в сокращениях типа 'Им.', 'Тов.', 'Пос.', но не делит на предложения
    for index in list_commas:
        upperwords = ['р.', 'с.', 'им.', 'тов.', 'пос.', 'обл.', 'п.г.т.']
        if text_read[index-2:index+1].lower() == ' '+upperwords[0]:
            list_commas.remove(index)
        elif text_read[index-2:index+1].lower() == ' '+upperwords[1]:
            list_commas.remove(index)
        elif text_read[index-3:index+1].lower() == ' '+upperwords[2]:
            list_commas.remove(index)
        elif text_read[index-6:index+1].lower() == ' '+upperwords[6]:
            list_commas.remove(index)
        for word in upperwords[3:6]:
            if text_read[index-4:index+1].lower() == ' '+word:
                list_commas.remove(index)

    just_numbers = '123456789'
    for index in list_commas[0:-1]:
        if text_read[index+2] in just_numbers:
        #вводим те штуки с точками, после которых предполагается наличие цифры, но на предложения эти точки не делят
            numbers_1 = ['ч.', 'г.', 'к.', 'п.', 'т.', 'с.', 'д.']
            for word1 in numbers_1:
                if text_read[index-2:index+1].lower() == ' '+word1: 
                    list_commas.remove(index)
                    
            numbers_2 = ['ст.', 'гл.', 'см.', 'ср.', 'им.', 'кв.', ]
            for word2 in numbers_2:
                if text_read[index-3:index+1].lower() == ' '+word2: 
                    list_commas.remove(index)
                    
            numbers_3 = ['тов.', 'рис.', 'стр.']
            for word3 in numbers_3:
                if text_read[index-4:index+1].lower() == ' '+word3:
                    list_commas.remove(index)
                    
            numbers_4 = ['подп.', 'табл.']
            for word4 in numbers_4:
                if text_read[index-5:index+1].lower() == ' '+word4: 
                    list_commas.remove(index)

    # Если все точки оказались не предложенческими
    if len(list_commas) == 0:
        return [text_read,]
    
    # Составим список предложений на основе индексов конечных знаков препинания
    sentences_list = []
    sentences_list.append(text_read[:list_commas[0]+1]) # Добавим предложение до первой точки
    # Добавим предложения от первой до последней точки
    for c in range(0, len(list_commas)-1):
        sentences_list.append(text_read[list_commas[c]+1:list_commas[c+1]+1])
    # Если после последней точки есть ещё какой-то большой кусок 
    # (длиннее двух символов) -> тоже добавим его
    if len(text_read) - list_commas[-1] > 2:
        sentences_list.append(text_read[list_commas[-1]+1:])

    return sentences_list


def main_sentencizer(parag_list):
  # Эта функция из списка параграфов делает пандас с предложениями и их статусом
    sentences = []
    status = []
    example_template = '^\s*\([0-9]+?[а-я]?\).*?' # для проверки на затесавшиеся в текст примеры
    for parag in parag_list:
        if parag[1] == 'text':
            parag[0] = sentence_border_searcher(parag[0])
            redline = True
            for p in parag[0]:
                sentences.append(p)
                if re.match(example_template, p) != None:
                    status.append('example')
                else:
                    if redline is True:
                        status.append('redline')
                        redline = False
                    else:
                        status.append('text')
        else:
            sentences.append(parag[0])
            status.append(parag[1])
    
    pd_sentences = pd.Series(sentences, dtype=pd.StringDtype())
    pd_status = pd.Series(status, dtype=pd.StringDtype())
    panda = pd.DataFrame({'sentences':pd_sentences, 'status':pd_status})
    return panda

main_results = main_sentencizer(final_paragraphs)



# POSITION METNOD
#dic - прототипический датафрейм на вход с двумя столбцами: предложениями и их статусом,
#ufo - список из очков, которые набрали предложения
def position_method(panda_main_res):
#ищем индексы первого, второго и последнего заголовков статьи
    headcount = 0
    h1 = 0
    h2 = 0
    hlast = 0
    for i in range(len(panda_main_res.index)):
      if panda_main_res.loc[i]['status'] == 'header':
        if h1 == 0:
          h1 = i
        headcount += 1
        if headcount == 2:
            h2 = i
        hlast = i 
    ufo = []
    for i in range(len(panda_main_res.index)):
        points = 0
        sent = panda_main_res.loc[i]['sentences']
        words_list = sent.split() #чтобы не давать очков предложениям с менее, чем 4 словами
        st = panda_main_res.loc[i]['status']
        if st == 'name' or st == 'example':
            ufo.append(points)
        elif len(words_list) < 4:
            ufo.append(points)
        else:
            if (i > h1 and i < h2) or (i > hlast): #предложения вступления и заключения
                points += 1
            if i < len(panda_main_res.index)-1:
                if i != 0:
                    if panda_main_res.loc[i-1]['status'] == 'header' or panda_main_res.loc[i+1]['status'] == 'header': #предложения-начала и концы разделов
                        points += 1
                if st == 'redline' or panda_main_res.loc[i+1]['status'] == 'redline': #предложения-начала и концы абзацев
                    points += 1
                ufo.append(points)
            else:
                points += 1
                ufo.append(points)
    panda_main_res['position_method'] = ufo 
    return panda_main_res

#SENTENCE LENGTH METHOD
def sentence_length_method(st_data):
    words_total = 0
    for i in range(len(st_data.index)):
      sent = st_data.loc[i]['sentences']
      words_list = sent.split()
      words_total += len(words_list)
    average_len = int(round(words_total / len(st_data.index),0)) #средняя длина предложений
#предложение получает 3 очка при отличии не более чем на 15% от average_len
#2 - не более чем на 30%, 1 - не более чем на 50%, остальные - 0
    ufo_too = []
    for i in range(len(st_data.index)):
      sent = st_data.loc[i]['sentences']
      words_list = sent.split()
      if len(words_list) < 4:
          ufo_too.append(0)
      else:
          if st_data.loc[i]['status'] == 'header' or st_data.loc[i]['status'] == 'example':
              ufo_too.append(0) 
          else:
              if len(words_list) > int(round(average_len*0.85,0)) and len(words_list) < int(round(average_len*1.15,0)):
                  ufo_too.append(3)
              elif len(words_list) > int(round(average_len*0.7,0)) and len(words_list) < int(round(average_len*1.3,0)):
                  ufo_too.append(2)
              elif len(words_list) > int(round(average_len*0.5,0)) and len(words_list) < int(round(average_len*1.5,0)):
                  ufo_too.append(1)
              else:
                  ufo_too.append(0)
    st_data['sentence_length_method'] = ufo_too
    return st_data


# TERM BASED METHOD
def term_method_lemmatizer(word, stops):
    word = word.lower()
    # Проверяем, что перед нами русское слово
    rus_let = '[а-я]+'
    if re.match(rus_let, word) is None:
        return word 
    # Проверяем, что перед нами не стоп-слово
    if word in stops:
            return 'стоп-слово!!!'
    return snowball.stem(word)

def term_method(sents, stats):
    # Создаём словарь вида (слово, ч.р.):кол-во_употреблений
    # Если у слова находится окончание, то в словаре оно хранится
    # без окончания, иначе возвращается как было.
    freq_dict = defaultdict(int)
    lenth_of_the_text= 0
    # Стоп-слова были взяты из библиотеки nltk и дополнены нами на наш вкус
    stop_words = ['без', 'иногда', 'эти', 'нас', 'нами', 'еще', 'к', 'какого', 'было', 'впрочем', 'этим', 'этого', 'а', 'может', 'такого', 
                  'нее', 'два', 'некоторых', 'им', 'разве', 'такая', 'некоторыми', ' какой', 'намного', 'перед', 'словно', 'нет', 'вы', 
                  'под', 'него', 'чем', 'кому', 'не', 'который', 'своих', 'пусть', 'я', 'от', 'была', 'нашем', 'раз', 'чём', 'чтоб', 
                  'своим', 'которые', 'во', 'никогда', 'якобы', 'либо', 'зачем', 'ровно', 'нельзя', 'для', 'себе', 'таком', 'своей', 
                  'каких', 'о', 'этом', 'никто', 'только', 'ещё', 'причем', 'даже', 'теперь', 'том', 'другой', 'некоторый', 'вам', 'этот', 
                  ' пускай', 'что', 'после', 'можно', 'ими', 'наконец', 'из', 'вас', 'эту', 'которых', 'всю', 'между', 'через', 'собой',
                  'нашим', 'будет', 'меня', 'своём', 'были', 'которое', 'ж', 'каждая', 'которая', 'ее', 'над', 'своего', 'наш', 'об', 
                  'всегда', 'ними', 'неких', 'этому', 'таких', 'едва', 'кем', 'несмотря', 'эта', 'таким', 'надо', 'три', 'некими', 'из-за',
                  'если', 'нашего', 'такими', 'они', 'нам', 'всем', 'которым', 'с', 'вот', 'же', 'чего', 'какому', 'такое', 'такие', 
                  'каждой', 'при', 'уже', 'бы', 'которой', 'некий', 'себя', 'много', 'некоторые', 'мы', 'был', 'ним', 'ком', 'почти', 
                  'итак', 'всеми', 'свои', 'каким', 'чуть', 'да', 'нескольких', 'тот', 'каждого', 'тем', 'хорошо', 'затем', 'лишь', 'в', 
                  'по', 'их', 'которого', 'до', 'почему', 'ну', 'ней', 'них', 'своими', 'нему', 'которыми', 'ему', 'это', 'откуда', 'своем', 
                  'её', ' кто', 'другие', 'мне', 'ни', 'он', 'свой', 'тогда', 'зато', 'такой', 'хоть', 'того', 'ко', ' как', 'или', 
                  'вами', 'тоже', 'оно', 'быть', 'ли', 'нём', 'притом', 'сейчас', 'этих', 'никого', 'которому', 'у', 'за', 'все', 'неё',
                  'теми', 'вроде', 'поскольку', 'тому', 'ничего', 'всё', 'вдруг', 'то', 'будто', 'ей', 'на', 'и', 'хотя', 'ничто', 'со', 
                  'конечно', 'про', 'лучше', 'какие', 'так', 'но', 'один', 'своему', 'этими', 'есть', 'этой', 'некие', 'всех', 'чему', 
                  'она', 'свою', 'чтобы', 'кого', 'пока', 'также', 'несколько', 'его', 'как', 'каждому', 'каждый', 'когда', 'точно',
                  'какая', 'своя', 'имеет']
    # Вычленяем из текста слова, очищаем от пунктуации, отправляем
    # на лемматизацию
    sent_index = 0
    for sent in sents:
        if stats[sent_index] == 'text':
            dirty_words = sent.split(' ')
            for dw in dirty_words:
                lenth_of_the_text += 1
                cw = dw.strip('—«»\n!?,.;:/\\()\*][{}|%^\"\'’')
                freq_dict[term_method_lemmatizer(cw, stop_words)] += 1
        sent_index += 1
      
    # САМОЕ ГЛАВНОЕ: отбор слов, которые мы считаем ключевыми
    log_freq_dict = {}
    for lemma in list(freq_dict):
        # Оптимальная минимальная частотность выводилась экспериментльно
        if freq_dict[lemma]/lenth_of_the_text >= 10/lenth_of_the_text and lemma != 'стоп-слово!!!' and len(lemma) > 1:
            eng_or_num = False
            engnum = '1234567890qwertyuioplkjhgfdsazxcvbnm'
            log_base = lenth_of_the_text // 100 # Это основание логорифма тоже выводилось экспериментально
            for letter in lemma:
                if letter in engnum:
                    eng_or_num = True
            if eng_or_num is False:
                # Мы используем логорифм, чтобы слова с очень высокой частотностью не давали 
                # непропорционально много очков.
                log_freq_dict[lemma] = math.log(freq_dict[lemma], log_base)
    # Ещё раз идём по словам предложения и начисляем логарифмические очки за слова, предварительно округляя
    # их и оставляя в диапазоне [1:3], чтобы метод не мог давать более 3-х очков.
    list_of_scores = []
    sent_index = 0
    for sent in sents:
        score = 0
        if stats[sent_index] == 'text':
            dirty_words = sent.split(' ')
            for dw in dirty_words:
                cw = dw.strip('—«»\n!?,.;:/\\()\*][{}|%^\"\' ')
                for freq_w in log_freq_dict:
                    if snowball.stem(cw) == freq_w:
                        score += log_freq_dict[freq_w]
        if score < 1 and score != 0:
            score = 1
        elif score > 3:
            score = 3
        else:
            score = round(score)
        list_of_scores.append(score)
        sent_index += 1
    return list_of_scores

def main_term_method(pandas_table):
    # Эта функция взаимодействует с пандасом и правильно применяет term_method
    list_of_sentences = pandas_table.loc[:,'sentences']
    list_of_statuses = pandas_table.loc[:,'status']
    tm_scores = term_method(list(list_of_sentences), list(list_of_statuses))
    pandas_table['term_method'] = tm_scores
    return pandas_table



# CUE WORDS METHOD
def main_cue_words_method(panda_main_res):
    list_ofcuewords = {('следовательно', 'примечательно', 'отметим', 'отсюда вытекает',
'разумеется', 'дело в том', 'наиболее', 'видно из примеров', 'в то же время',
'при этом', 'можно заметить','однако', 'интересно', 'так,', 'в ряде случаев', 'связано с'): 1, ('итак', 'подытожим', 'в заключение', 
'важно', 'подводя итоги', 'таким образом', 'подводя итоги', 'подведем итоги', 'в результате'): 2}
    list_of_scores = []
    for i in range(len(panda_main_res.index)):
        list_of_scores.append(0)
        for cue_word_set in list_ofcuewords:
            for cue_word in cue_word_set:
                if cue_word in panda_main_res['sentences'][i].lower(): 
                    list_of_scores[-1] += list_ofcuewords[cue_word_set] #начисляю индекс пр-нию при встрече с cue word в нем
                        
    panda_main_res['cue_words_method'] = list_of_scores
    return panda_main_res

main_results = main_term_method(main_results)
main_results = position_method(main_results)
main_results = sentence_length_method(main_results)
main_results = main_cue_words_method(main_results)

#считаем сумму очков по каждому методу, добавляя в новую колонку total_score в общем датафрейме
total = []
for i in range(len(main_results.index)):
  tm = main_results.loc[i]['term_method']
  pm = main_results.loc[i]['position_method']
  sm = main_results.loc[i]['sentence_length_method']
  cm = main_results.loc[i]['cue_words_method']
  if main_results.loc[i]['status'] == 'header' or main_results.loc[i]['status'] == 'example':
      total.append(0)
  else:
      if cm != 0: #если cue words method дал баллы, в итоге получим сумму баллов за все методы
          total.append(tm + pm + sm + cm)
      else: #sorry not sorry предложения набравшие 0 по cue words и 0 по 2+ остальным методам тоже получат 0 в итоге
          if ((tm == pm or tm == sm) and tm == 0) or ((pm == tm or pm == sm) and pm == 0) or ((sm == pm or sm == tm) and sm == 0): #выглядит не оч лаконично но должно работать!
              total.append(0)
          else:
              total.append(tm + pm + sm + cm)
main_results['total_score'] = total
main_results

#создаем тхт-файл для латеха

output_file_name = input('Введите имя файла, который вы хотите получить:')

with open(output_file_name+'.txt', "w", encoding="utf-8") as output_file:
    output_file.write('\\documentclass{article}\n\\usepackage[russian]{babel}')
    output_file.write('\n\\usepackage[dvipsnames]{xcolor}\n\\usepackage[utf8]{inputenc}')
    output_file.write('\n\\begin{document}')
    output_file.write('\n\\definecolor{medium}{RGB}{150, 150, 150}')
    output_file.write('\n\\definecolor{light}{RGB}{205, 205, 205}')
    for i in range(len(main_results.index)):
        if main_results['status'][i] == 'redline':
            output_file.write('\n\n')
        if main_results['total_score'][i] != 0:    
            if main_results['cue_words_method'][i] == 0:
                if main_results['term_method'][i] != 0 and main_results['position_method'][i] != 0 and main_results['sentence_length_method'][i] != 0:
                    output_file.write(main_results['sentences'][i])
                elif main_results['term_method'][i] == 0 and main_results['position_method'][i] != 0 and main_results['sentence_length_method'][i] != 0:
                    output_file.write(' {\\textcolor{medium}{'+main_results['sentences'][i]+'}}')
                elif main_results['term_method'][i] != 0 and main_results['position_method'][i] == 0 and main_results['sentence_length_method'][i] != 0:
                    output_file.write(' {\\textcolor{medium}{'+main_results['sentences'][i]+'}}')
                elif main_results['term_method'][i] != 0 and main_results['position_method'][i] != 0 and main_results['sentence_length_method'][i] == 0:
                    output_file.write(' {\\textcolor{medium}{'+main_results['sentences'][i]+'}}')
            else:
                output_file.write(main_results['sentences'][i])  
        else:
            output_file.write(' {\\textcolor{light}{'+main_results['sentences'][i]+'}}')
    for note in final_footnotes:
      output_file.write(note)
    output_file.write('\\end{document}')
