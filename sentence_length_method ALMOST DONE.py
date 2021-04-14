#приведу к виду функции, которая будет применяться к filename, данным пользователем?
#надо еще выкинуть регулярками т.д., ср., 2.2(.3), И.К. как инициалы
#и завершить. записывать новый файл с "конспектом"?

#делаем список списков из файла, данного пользователем. пока только .txt
import re

filename = input('Введите имя файла для обработки: ')
with open(filename, encoding='utf-8') as f:
    text_from = f.read()
text_from = text_from.replace(';', '.')
text_from = re.sub(r'\n', '', text_from)
text_from = text_from.replace('. ', '.')
text_to = text_from.split('.')
text = [[i] for i in text_to] #вот он - наш список списков*, где каждый список* - предложение текста, правда, без точки в конце

#считаем среднюю длину предложений как среднее количество слов в оном

words_total = 0
for i in range(len(text)):
    sent_list = text[i]
    sent = str(sent_list[0])
    words_list = sent.split()
    words_total += len(words_list)
average_len = int(round(words_total / len(text),0))

#начинаем давать очки предложениям. 3 - при разнице не более чем на 5* от average_len
#2 - не более чем на 10, 1 - не более чем на 15, остальное 0 и не учитываем
#* - допустимая разница меняется в зависимости от средней длины предложений. Подумаю, как лучше рассчитывать
#будем хранить в списках индексы предложений, набравших нужное число баллов

score1 = []
score2 = []
score3 = []
for i in range(len(text)):
    sent_list = text[i]
    sent = str(sent_list[0])
    words_list = sent.split()
    if len(words_list) > average_len - 5 and len(words_list) < average_len + 5:
        score3.append(i)
    elif len(words_list) > average_len - 10 and len(words_list) < average_len + 10:
        score2.append(i)
    elif len(words_list) > average_len - 15 and len(words_list) < average_len + 15:
        score1.append(i)
    else:
        pass
#теперь выведем предложения, набравшие 3 балла. в теории это и есть те, что содержат главную информацию
#НА ПОТОМ: если 3-балльных мало, добавляем 2-балльные. мало или нет - в зависимости от длины текста?

print('summary')
for j in range(len(score3)):
    sent_list = text[score3[j]]
    sent = str(sent_list[0])
    print(sent)
