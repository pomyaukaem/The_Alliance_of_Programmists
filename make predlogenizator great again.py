#ЧТО БЕРЕТ ЭТОТ КОД? строку, являющуюся текстом нашей статьи
#ЧТО ОН ВОЗВРАЩАЕТ? список предложений этого текста
import re
#создаем список индексов всех точек, чтобы дальше проверять каждую 
list_commas = []

q = 0
for symbol in text_read:
    q += 1
    if symbol == ';' or symbol == '?' or symbol == '.' or symbol == '!':
        list_commas.append(q-1) 
print(list_commas)
new_list_commas = []
for index in list_commas:
    #если следующий после "точки" символ - не пробел и не перенос строки, то это не конец предложения
    if text_read[index+1] == ' ' or text_read[index+1] == '\n':
        new_list_commas.append(index)
print(new_list_commas)
list_commas = new_list_commas

for index in list_commas[0:-1]:
    if  type(text_read[index+2]) == str:
        if text_read[index+2].islower() is True:
            list_commas.remove(index)
            print(list_commas)
        else:
            #вводим паттерн для инициалов типа В. В. Виноградов или М. Дж. Николсон
            pattern_1 = '.*[А-Я][а-я]?\.\s?[А-Я]?[а-я]?\.?\s?[А-Я].*'
            if re.match(pattern_1, text_read[index-2:index+8]) is not None:
                list_commas.remove(index)

                #точка есть в сокращениях типа 'Им.', 'Тов.', 'Пос.', но не делит на предложения
                    upperwords = ['Р.', 'C.', 'Им.', 'Тов.', 'Пос.', 'Обл.', 'П.г.т.', 'П. г. т.']
            if text_read[text_read.index(symbol)-2:text_read.index(symbol)+1] == ' '+upperwords[0]:
                list_commas.remove(index)
            elif text_read[text_read.index(symbol)-2:text_read.index(symbol)+1] == ' '+upperwords[0].lower():
                list_commas.remove(index)
            elif text_read[index-3:index+1] == ' '+upperwords[1]:
                list_commas.remove(index)
            elif text_read[index-3:index+1] == ' '+upperwords[1].lower():
                list_commas.remove(index)
            elif text_read[index-4:index+1] == ' '+upperwords[2]:
                list_commas.remove(index)
            elif text_read[index-4:index+1] == ' '+upperwords[2].lower():
                list_commas.remove(index)
            elif text_read[index-8:index+1] == ' '+upperwords[5]:
                list_commas.remove(index)
            elif text_read[index-8:index+1] == ' '+upperwords[5].lower():
                list_commas.remove(index)

            for word in upperwords[3:6]:
                if text_read[index-5:index+1] == ' '+word:
                    list_commas.remove(index)
                elif text_read[index-5:index+1] == ' '+word.lower():
                    list_commas.remove(index)
        
        elif type(text_read[index+2]) == int:
            #вводим те штуки с точками, после которых предполагается наличие цифры, но на предложения эти точки не делят
            numbers_1 = ['Ч.', 'Г.', 'К.', 'П.', 'Т.', 'С.', 'Д.']

            for word in numbers_1:
                        if text_read[text_read.index(symbol)-2]:symbol = word: 
                            list_commas.remove(index)
                        elif text_read[text_read.index(symbol)-1]+symbol = word.lower():
                            list_commas.remove(index)
                    
                    numbers_2 = ['Ст.', 'Гл.', 'См.', 'Ср.', 'Им.', 'Кв.', ]
                    for word in numbers_1:
                        if text_read[text_read.index(symbol)-2:text_read.index(symbol)+1] = word:
                            list_commas.remove(index)
                        elif  text_read[text_read.index(symbol)-2:text_read.index(symbol)+1] = word.lower():
                            list_commas.remove(index)
                    
                    numbers_3 = ['Тов.', 'Рис.', 'Стр.']
                    for word in numbers_1:
                        if text_read[text_read.index(symbol)-3:text_read.index(symbol)+1] = word: 
                            list_commas.remove(index)
                        elif text_read[text_read.index(symbol)-3:text_read.index(symbol)+1] = word.lower():
                            list_commas.remove(index)
                    
                    numbers_4 = ['Подп.', 'Табл.']
                    for word in numbers_1:
                        if text_read[text_read.index(symbol)-4:text_read.index(symbol)+1] = word: 
                            list_commas.remove(index)
                        elif text_read[text_read.index(symbol)-4:text_read.index(symbol)+1] = word.lower():
                            list_commas.remove(index)       


list_sentences = []        
double_list_commas = list_commas
for index in double_list_commas[0, -1, 2]:
    list_sentences.append(text_read[index:index+2])



    
