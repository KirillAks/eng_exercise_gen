#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st
from io import StringIO
from eng_exercise_gen import EngExerciseGen

eeg = EngExerciseGen()

st.header('Генератор упражнений по английскому языку')
'---'
st.header('Прочитайте текст и выполните упражнения')

uploaded_file = st.file_uploader("Выберите и загрузите файл с текстом:")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    st.write(string_data)
    
# generation = st.radio(
#     "Сгенерировать упражнения?",
#     ('Да, я хочу выполнить упражнения', 'Нет, хочу прочитать текст ещё раз'))

# if generation == 'Нет, хочу прочитать текст ещё раз':
#     st.write("Повторите текст")
# else:
#     st.write('Пожалуйста, подождите, пока сгенерируются упражнения...')


# if st.button('Сгенерировать упражнения'):
#     st.write('Пожалуйста, подождите, пока сгенерируются упражнения...')
#     df = eeg.create_sentence('Little_Red_Cap_ Jacob_and_Wilhelm_Grimm.txt')    
#     tasks = eeg.create_df(df)
    
if 'button' not in st.session_state:
    st.session_state.button = False

def click_button():
    st.session_state.button = not st.session_state.button

st.button('Сгенерировать упражнения', on_click=click_button)

if st.session_state.button:
    st.write('Пожалуйста, подождите, пока сгенерируются упражнения...')
    df = eeg.create_sentence('Little_Red_Cap_ Jacob_and_Wilhelm_Grimm.txt')
    tasks = eeg.create_df(df) 
    '---'
    for i, row in tasks.iterrows():
        st.subheader(row['description']) 

        col1, col2 = st.columns(2)
        with col1:
            st.write('')
            st.write(row['sent_ex'])

        with col2:
            option = row['options']
            if row['type']=='missing_word':
                text = '–––'
                row['result'] = st.text_area("Напишите ответ:", text, key=f"{i+20}")
            else:
                row['result'] = st.selectbox(
                    'nolabel',
                    ['–––'] + option,
                    key = f"{i}",
                    label_visibility="hidden",
                ) 
            if row['result'] == '–––':
                pass
            elif row['result'] == row['answer']:
                st.success('Correctly', icon="💪")
            else:
                st.error('Mistake', icon="🤷‍♂️")

#         tasks['total'] = row['result'] == row['answer']
        '---'    

#     total_sum = sum(tasks['total'])

#     if total_sum == len(tasks):
#         st.success('Поздравляем! Вы ответили на все вопросы!')
#         st.balloons()
else:
    st.write('Button is off!')    

