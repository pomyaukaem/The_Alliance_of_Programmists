from collections import defaultdict
import re
import math




# TERM METHOD

# Проверено (по Зализняку), что есть окончания для:
# СУЩЕСТВИТЕЛЬНЫХ "стол", "лампа", "пекло", "тюлень", "цапля", "море",
# "сапог", "коряга", "солнышко", "калач", "галоша", "чудовище",
# "конец", "девица", "деревце", "бой", "шея", "здоровье",
# "полоний", "сложение", "мания", "боль";
# ПРИЛАГАТЕЛЬНЫХ "тусклый", "весенний", "мягкий", "вещий", "куцый";
# ГЛАГОЛОВ 1 и 2 спряжения
endings = ['а', 'у', 'ом', 'е', 'ы', 'ов', 'ам', 'ами', 'ах', 'ы', 'ой', 'о',
           'ь', 'я', 'ю', 'ем', 'и', 'ей', 'ями', 'ях', 'й', 'ёв', 'ью',
           'ый', 'ого', 'ому', 'ым', 'ом', 'ая', 'ой', 'ое', 'ий', 'его', 'ему',
           'им', 'ем', 'яя', 'ее', 'ые', 'ых', 'ым', 'ыми', 'ие', 'их', 'ую', 'юю',
           'еть', 'ить', 'ять', 'ать', 'ите', 'ешь', 'ишь', 'ете', 'ет', 'ит',
           'ют', 'ят', 'ут', 'ат', 'л', 'ла']
endings = sorted(endings, key = lambda x: (len(x), x), reverse = True)
# Эта схема не помогает с чередованиями гласных (замок - замка)
# и чередованиями согласных хотеть - хочу, ведут - вела 
# (есть ли правила для чередований?)


def term_method_lemmatizer(word, flex, stops):
    word = word.lower()
    # Проверяем, что перед нами русское слово
    rus_let = '[а-я]+'
    if re.match(rus_let, word) is None:
        return word # Не уверена в этом решении
    # Проверяем, что перед нами не стоп-слово (отсюда: https://snipp.ru/seo/stop-ru-words)
    # Возможно, есть источники получше? (потому что этот мне не нравится)
    # Вообще замечание к стоп-словам: они там в основном в начальных формах,
    # их тоже где-то надо лемматизировать (набор словоформ как вриант, но 
    # это сложно и долго делать...)
    if len(word) == 1:
        if word in stops[word]['']:
            return 'стоп-слово!!!'
    else:
        if word in stops[word[0]][word[1]]:
            return 'стоп-слово!!!'
    # Отсекаем постфиксы
    vowels = 'уеоэаыяию'
    if word.endswith('ся'):
        word = word[0:-2]
        # этот алгоритм см. ниже
        for f in flex:
            if word.endswith(f):
                return(word[:-len(f)]+'_'+'ся')
    if word.endswith('сь') and word[-3] in vowels:
        word = word[0:-2]
        # этот алгоритм см. ниже
        for f in flex:
            if word.endswith(f):
                return(word[:-len(f)]+'_'+'ся')
    # Начинаем поиск окончаний с самых длинных паттернов
    for f in flex:
        if word.endswith(f):
            return(word[:-len(f)])
    # Если окончание ненашлось
    return word
    # Подумать про весы вероятности верного определения формы!!!


def main_term_method(sents, ends):
    # Создаём словарь вида (слово, ч.р.):кол-во_употреблений
    # Если у слова находится окончание, то в словаре оно хранится
    # без окончания, иначе возвращается как было.
    freq_dict = defaultdict(int)
    lenth_of_the_text= 0
    # Словарь вида "первая буква:словарь вторых букв:список слов с такими двумя
    # первыми буквами" ('' как вторая буква для однобуквенных слов)
    stopwords = defaultdict(list)
    alphabet = 'ёйцукенгшщзхъэждлорпавыфячсмитьбю'
    with open('stopwords.txt', 'r', encoding = 'utf-8') as stopwords_file:
        # сначала словарь буква:[слова]
        for stopword in stopwords_file.readlines():
            stopword = stopword.strip('\n')
            stopwords[stopword[0]].append(stopword)
        # досоздаём словари с пустыми списками для невстретившихся букв
        met_let_1 = list(stopwords) # встретившиеся буквы
        for alpha in alphabet:
            if alpha not in met_let_1:
                stopwords[alpha] = []
        # теперь из каждого списка слов делаем словарь вторых букв
        for letter in list(stopwords):
            letter_dict = defaultdict(list)
            for badword in stopwords[letter]:
                if len(badword) == 1:
                    letter_dict[''].append(badword)
                else:
                    letter_dict[badword[1]].append(badword)
            met_let_2 = list(letter_dict)
            for beta in alphabet:
                if beta not in met_let_2:
                    letter_dict[beta] = []
            stopwords[letter] = letter_dict
    # НУЖНО ПРИДУМАТЬ КАК НЕ АНАЛИЗИРОВАТЬ ПРИМЕРЫ (отличать от нумерации пунктов)
    # Вычленяем из текста слова, очищаем от пунктуации, отправляем
    # на лемматизацию
    for sent in sents:
        dirty_words = sent[0].split(' ')
        for dw in dirty_words:
            lenth_of_the_text += 1
            cw = dw.strip('—«»\n!?,.;:/\\()\*][{}|%^\"\'')
            freq_dict[term_method_lemmatizer(cw, ends, stopwords)] += 1
    # САМОЕ ГЛАВНОЕ: отбор слов, которые мы считаем ключевыми
    log_freq_dict = {}
    for lemma in list(freq_dict):
        # 1/60 выведена глупым экспериментом
        if freq_dict[lemma]/lenth_of_the_text >= 1/60 and lemma != 'стоп-слово!!!':
            log_freq_dict[lemma] = math.log(freq_dict[lemma], 2) # С основанием тоже поработать!!!
    # Ещё раз идём по словам предложения и начисляем логарифмические очки за слова
    list_of_scores = []
    for sent in sents:
        list_of_scores.append(0)
        dirty_words = sent[0].split(' ')
        for dw in dirty_words:
            lenth_of_the_text += 1
            cw = dw.strip('—«»\n!?,.;:/\\()\*][{}|%^\"\'')
            for freq_w in log_freq_dict:
                if term_method_lemmatizer(cw, ends, stopwords) == freq_w:
                    # В тестовом случае прошли 12/20 предложений
                    list_of_scores[-1] += log_freq_dict[freq_w]
    return list_of_scores


main_term_method(text, endings)
