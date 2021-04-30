def main_cue_words_method(t):
    list_ofcuewords = {('следовательно', 'примечательно', 'отметим', 'отсюда вытекает',
'разумеется', 'дело в том', 'наиболее', 'видно из примеров', 'в то же время',
'при этом', 'можно заметить','однако', 'интересно', 'так,', 'в ряде случаев', 'связано с'): 1, ('итак', 'подытожим', 'в заключение', 
'важно', 'подводя итоги', 'таким образом', 'подводя итоги', 'подведем итоги', 'в результате'): 2}
    #! что исправить: слово "так" в очищенных от пунктуации пр-ниях не будет считаться как нужно (такой, таковы и т.д.)
    list_of_scores = []
    for each_sentence in t:
        list_of_scores.append(0)
        for s in each_sentence:
            for cue_word_dict in list_ofcuewords:
                for cue_word in cue_word_dict:
                    if cue_word in s.lower(): 
                        list_of_scores[-1] += list_ofcuewords[cue_word_dict] #начисляю индекс пр-нию при встрече с cue word в нем
    return list_of_scores

text = [['Можно сказать, что композициональность в данном случае играет большую роль'],['Подытожим, что наш эксперимент не удался'],
        ['Это связано с тем, что так работает']]

print(main_cue_words_method(text))
