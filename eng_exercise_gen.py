#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import pandas as pd
import spacy
import en_core_web_sm
import gensim.downloader as api

nlp = en_core_web_sm.load()
model = api.load("glove-wiki-gigaword-200")


# создаем класс
class EngExerciseGen:
    # создаем датасет
    def create_sentence(self, file):
        data = pd.DataFrame()
        for line in file:
            line = line.strip()
            if len(line)>0:
                doc = nlp(line)
                for sent in doc.sents:
                    data.loc[len(data), 'raw'] = sent.text
        return data

    # выбор упражнения случайным образом    
    def variant(row):
        random_variant = random.choice(
            [EngExerciseGen.select_word, EngExerciseGen.select_conjunction, EngExerciseGen.select_determiner,
             EngExerciseGen.noun_phrases, EngExerciseGen.select_sent, EngExerciseGen.missing_word]
        )    
        return random_variant(row)

    # выбор пропущенного слова (существительного, глагола, наречия, прилагательного)   
    def select_word(row):
        token_list = [token for token in nlp(row['raw']) if token.pos_ in ['NOUN', 'VERB', 'ADV', 'ADJ']]
        if len(token_list)==0:
            return row
        token_random = random.choice(token_list)
        try:
            options = [w[0] for w in model.similar_by_word(token_random.text.lower(), topn=2)] + [token_random.text]
            if token_random.text.istitle():
                options = [x.title() for x in options]
            random.shuffle(options)
            row['type'] = 'select_word'
            row['options'] = options
            row['object'] = token_random.text
            row['answer'] = token_random.text        
            row['description'] = 'Выберите правильное слово:'
            row['sent_ex'] = str.replace(row['raw'], row['object'], '___')
            row['result'] = []
            row['total'] = 0
        except:
            pass
        return row
    
    # выбор пропущенного союза
    def select_conjunction(row):
        token_list = [token for token in nlp(row['raw']) if token.pos_=='CCONJ']
        if len(token_list)==0:
            return row
        token_random = random.choice(token_list)
        options = [w[0] for w in model.similar_by_word(token_random.text.lower(), topn=2)] + [token_random.text]
        if token_random.text.istitle():
            options = [x.title() for x in options]
        random.shuffle(options)    
        row['type'] = 'select_conjunction'
        row['options'] = options
        row['object'] = token_random.text
        row['answer'] = token_random.text    
        row['description'] = 'Выберите правильный союз:'
        start_token_index = token_random.idx
        end_token_index = start_token_index+len(token_random)
        row['sent_ex'] = row['raw'][:start_token_index] + '___' + row['raw'][end_token_index:]
        row['result'] = []
        row['total'] = 0
        return row
    
    # определить пропущенный артикль
    def select_determiner(row):
        token_list = [token for token in nlp(row['raw']) if token.pos_=='DET' and token.dep_=='det' and token.text!='what']
        if len(token_list)==0:
            return row
        token_random = random.choice(token_list)
        options = [w[0] for w in model.similar_by_word(token_random.text.lower(), topn=2)] + [token_random.text]
        if token_random.text.istitle():
            options = [x.title() for x in options]
        random.shuffle(options)
        row['type'] = 'select_determiner'
        row['options'] = options
        row['object'] = token_random.text
        row['answer'] = token_random.text    
        row['description'] = 'Выберите пропущенный(ые) артикль(и):'
        start_token_index = token_random.idx
        end_token_index = start_token_index+len(token_random)
        row['sent_ex'] = row['raw'][:start_token_index] + '___' + row['raw'][end_token_index:]
        row['result'] = []
        row['total'] = 0
        return row
    
    # выбор существительных с зависимыми словами
    def noun_phrases(row):
        phrases_list = [phrase for phrase in nlp(row['raw']).noun_chunks if len(phrase)>=3]
        if len(phrases_list)<2:
            return row
        phrase_random = random.choice(phrases_list)
        options = [spacy.explain(option.root.dep_) for option in nlp(row['raw'] ).noun_chunks]
        options = list(set(options))
        random.shuffle(options)
        row['type'] = 'noun_phrases'
        row['options'] = options
        row['object'] = phrase_random.text
        row['answer'] = spacy.explain(phrase_random.root.dep_)    
        row['description'] = 'Чем в предложении являются эти слова?'
        row['sent_ex'] = row['object']
        row['result'] = []
        row['total'] = 0
        return row
    
    # выбор правильного предложения
    def select_sent(row):
        new_sent_1, new_sent_2 = row['raw'], row['raw']
        i=5
        token_list = [token for token in nlp(row['raw']) if token.pos_ in ['NOUN', 'PRON', 'VERB', 'ADV', 'ADJ']]
        if len(token_list)==0:
            return row
        for token in token_list:
            try:
                new_word_1 = random.choice(model.most_similar(token.text.lower(), topn=i))[0]
                new_word_2 = random.choice(model.most_similar(positive = [token.text.lower(), 'bad'], negative = ['good'], topn=i))[0]

                new_word_1 = new_word_1.title() if token.text.istitle() else new_word_1
                new_word_2 = new_word_2.title() if token.text.istitle() else new_word_2  

                new_sent_1 = new_sent_1.replace(token.text, new_word_1)
                new_sent_2 = new_sent_2.replace(token.text, new_word_2)
            except:
                pass

        options = []
        if new_sent_1!=row['raw']:
            options.append(new_sent_1)
        if new_sent_2!=row['raw']:
            options.append(new_sent_2)
        if len(options)>0:
            options.append(row['raw'])
            random.shuffle(options)
            row['type'] = 'select_sent'
            row['options'] = options
            row['object'] = row['raw']
            row['answer'] = row['raw']        
            row['description'] = 'Какое предложение верно?'
            row['sent_ex'] = 'Вспомните текст и выберите предложение'
            row['result'] = []
            row['total'] = 0
        return row
    
    # определить пропущенное слово
    def missing_word(row):
        token_list = [token for token in nlp(row['raw']) if token.pos_ in ['NOUN', 'VERB', 'ADV', 'ADJ']]
        if len(token_list)==0:
            return row
        token_random = random.choice(token_list)
        row['type'] = 'missing_word'
        row['options'] = []
        row['object'] = token_random.text
        row['answer'] = token_random.text    
        row['description'] = 'Напишите пропущенное(ые) слово(а):'
        row['sent_ex'] = str.replace(row['raw'], row['object'], '___')
        row['result'] = []
        row['total'] = 0
        return row
    
    # создание датафрейма упражнений
    def create_df(self, data):        
        data = data.apply(EngExerciseGen.variant, axis=1)
        data = data.dropna().reset_index(drop=True)
        data = data.sample(10).reset_index(drop=True)
        return data

