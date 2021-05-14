# The_Alliance_of_Programmists
Это наш итоговый проект по программированию!

## Описание проекта
Наша консольная программа делает из pdf-файла с научной статьей текстовый файл, в котором текст статьи оформлен языком LaTeX. В дальнейшем пользователь может загрузить этот текст на https://www.overleaf.com/ и получить статью, где чёрным цветом выделены самые важные по мнению программы предложения, серым - обычные, бледно-серым - маловажные.
- Используются разные методы автоматического реферирования, начисляющие предложениям "индексы значимости":
1. Term based method: очки начисляются предложениям с частотными словами статьи
2. Cue words based method: очки начисляются предложениям с важными словами типа "итак", "вывод" и др.
3. Sentence lenth based method: очки начисляются предложением со средней длинной, так как считается, что в таких предложениях с большей вероятностью содержится важная информация.
4. Position based method: очки начисляются первому и последнему предложению абзацев.
- Эти методы мы брали отсюда: https://tconspectus.pythonanywhere.com/about#algorithm
- Программа использует модули re, math, pandas, libpdf (из одноименной библиотеки), collections и nltk.stem.snowball (из библиотеки nltk) - о необходимости установки библиотек указано в начале программы

## Критерий завершенного проекта
##### Предусмотренные недостатки нашей программы:
Некоторые pdf-файлы не распознаются использованной нами библиотекой, или текст иногда распознаётся как таблица. В таких случаях теряется структура документа, распознавание которой важно для работы нашей программы. Поэтому на некоторых pdf-файлах программа может работать некорректно.

В остальном программа должна выполнять все указанное в описании!

## Команда проекта
##### Мы все из БКЛ-203:
- Алина Лобанова
- Светлана Майорова
- Анна Кученина

## Задачи и таймлайны
##### 31 марта - 6 апреля: 
- утверждение темы проекта
- разработка плана действий
##### 7 апреля - 14 апреля:
- разработка term_based_method
- разработка cue_words_based_method
- разработка sentence_lenth_method
##### 15 апреля - 21 апреля:
- чтение файлов pdf
- наприсание функции, разделяющей текст на предложения
- разработка position_based_method
##### 22 апреля - 4 мая:
- соединение всех частей программы в один код
- приведение предложений и их очков к формату pandas + подстраивание методов под pandas
- подбор весов и экспериментирование с совместной работой всех методов
- вывод программой текста, размеченного в LaTeX согласно полученным очкам
- реализация общения с пользователем
##### 5 мая - 14 мая:
- корректировка координации методов
- финальные дизайнерские штрихи над выдачей
- моральная подготовка к защите
## Распределение обязанностей
##### Алина
- чтение pdf-файла (в том числе корректировка деления программой текста на абзацы)
- term_based_method
- состыковка "предложенизатора" и считывателя pdf
- адаптация своего метода к pandas
##### Аня
- "предложенизатор"
- cue_words_based_method
- адаптация своего метода к pandas
- общение с пользователем
- выделение текста с помощью LaTeX
##### Света
- sentence_lenth_based_method
- position_based_method
- адаптация своих методов к pandas
- координация всех методов
## Актуальные вопросы
