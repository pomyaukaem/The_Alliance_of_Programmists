#ЧТО БЕРЕТ ЭТОТ КОД? строку (ПОКА ЧТО) text_read, являющуюся текстом нашей статьи
#ЧТО ОН ВОЗВРАЩАЕТ? принтит (ПОКА ЧТО) список индексов важных точек - тех, которые по-настоящему делят на предложения
import re
#создаем список индексов всех точек, чтобы дальше последовательно проверять каждую 
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
for index in list_commas:
    upperwords = ['Р.', 'C.', 'Им.', 'Тов.', 'Пос.', 'Обл.', 'П.г.т.']
    if text_read[index-2:index+1] == ' '+upperwords[0]:
        list_commas.remove(index)
    elif text_read[index-2:index+1] == ' '+upperwords[0].lower():
        list_commas.remove(index)
    elif text_read[index-2:index+1] == ' '+upperwords[1]:
        list_commas.remove(index)
    elif text_read[index-2:index+1] == ' '+upperwords[1].lower():
        list_commas.remove(index)
    elif text_read[index-3:index+1] == ' '+upperwords[2]:
        list_commas.remove(index)
    elif text_read[index-3:index+1] == ' '+upperwords[2].lower():
        list_commas.remove(index)
    elif text_read[index-6:index+1] == ' '+upperwords[6]:
        list_commas.remove(index)
    elif text_read[index-6:index+1] == ' '+upperwords[6].lower():
        list_commas.remove(index)
    for word in upperwords[3:6]:
        if text_read[index-4:index+1] == ' '+word:
            list_commas.remove(index)
        elif text_read[index-4:index+1] == ' '+word.lower():
            list_commas.remove(index)

just_numbers = '123456789'
for index in list_commas[0:-1]:
    if text_read[index+2] in just_numbers:

        #вводим те штуки с точками, после которых предполагается наличие цифры, но на предложения эти точки не делят
        numbers_1 = ['Ч.', 'Г.', 'К.', 'П.', 'Т.', 'С.', 'Д.']
        for word1 in numbers_1:
            if text_read[index-2:index+1] == ' '+word1: 
                list_commas.remove(index)
            elif text_read[index-2:index+1] == ' '+word1.lower(): 
                list_commas.remove(index)
                    
        numbers_2 = ['Ст.', 'Гл.', 'См.', 'Ср.', 'Им.', 'Кв.', ]
        for word2 in numbers_2:
            if text_read[index-3:index+1] == ' '+word2: 
                list_commas.remove(index)
            elif text_read[index-3:index+1] == ' '+word2.lower():
                list_commas.remove(index)
                    
        numbers_3 = ['Тов.', 'Рис.', 'Стр.']
        for word3 in numbers_3:
            if text_read[index-4:index+1] == ' '+word3:
                list_commas.remove(index)
            elif text_read[index-4:index+1] == ' '+word3.lower():
                list_commas.remove(index)
                    
        numbers_4 = ['Подп.', 'Табл.']
        for word4 in numbers_4:
            if text_read[index-5:index+1] == ' '+word4: 
                list_commas.remove(index)
            elif text_read[index-5:index+1] == ' '+word4.lower():
                list_commas.remove(index)       

print(list_commas)



    
