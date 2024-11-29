import streamlit as st
import pandas as pd
import random
from openai import OpenAI

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("Country Guesser")
st.image("https://tse4.mm.bing.net/th?id=OIP.4cXjNUsskNTDylthxHqMFwHaDq&pid=Api")

col1, col2= st.columns([0.6,0.4], gap = "medium", vertical_alignment = "top")


key = st.text_input("Please put your OpenAI key here")
 

#use cache to only load the data once
@st.cache_data
def load_countries():
    df = pd.read_csv('world-data-2023.csv')
    return df
countries = load_countries()

#defining the guessing goal
def get_random_country():
    random_index = random.randint(0, len(countries) - 1)
    random_country = countries.iloc[random_index]['Country']
    return random_country
 
#pulling countries attributes out of dataframe
def searching_for_country_in_df(df, country, number):
    variable = df['Country'].str.contains(country)
    for index, var in enumerate(variable):
        if var is True:
            new = index
    coordinate = df.loc[new][number]
    return coordinate

#computing relative distance of two countries for evaluation
def evaluating_distance(country1, country2, country_df):
    latitude = searching_for_country_in_df(country_df, country1, -1) - searching_for_country_in_df(country_df, country2, -1)
    longitude = searching_for_country_in_df(country_df, country1, -2) - searching_for_country_in_df(country_df, country2, -2)
    distance = ((latitude**2) + (longitude**2))**0.5
    return round(distance)

st.session_state.hint_bool = False
st.session_state.win_bool = False


#storing goal in session
if 'country_to_guess' not in st.session_state:
    st.session_state.country_to_guess = get_random_country()

#storing stats in session
if 'hint_number' not in st.session_state:
    st.session_state.hint_number = 0
if 'question_number' not in st.session_state:
    st.session_state.question_number = 0
if 'total_number' not in st.session_state:
    st.session_state.total_number = 0
if 'country_guess_number' not in st.session_state:
    st.session_state.country_guess_number = 0

if 'distance' not in st.session_state:
    st.session_state.distance = []
if 'guessed_country_list' not in st.session_state:
    st.session_state.guessed_country_list = []

if 'distance_country' not in st.session_state:
    st.session_state.distance_country = pd.DataFrame({'Country': [ ], 'Distance': [ ]})
if 'stats_df' not in st.session_state:
    st.session_state.stats_df = pd.DataFrame({'Country': [ ], 'TotalInputs': [ ], 'Hints': [ ], 'QuestionAsked': [ ], 'CountryGuesses': [], 'DistanceTraveled': []})



# set up of input field and hint button in second column
with col2:
    message = st.chat_input("Ask me a question about a country or give a guess :)")
    if st.button("Please give me a hint!"):
        st.session_state.hint_bool = True

with col1:
    #making it look like its from chat bot
    with st.chat_message("assistant"):
        st.markdown("Helloooo! I am thinking of a country. You have to guess which country it is. You can ask me questions to help you guess the country. You can also ask for hints.")

    #adding the chat history to be able to put in the prompt
    chat_history_string = "\n".join(st.session_state.chat_history)

    #Prompt gpt-4o-mini
    template = f"You are playing a guessing game with a user. You act as the game master who thought of a country. The country to be guessed is {st.session_state.country_to_guess}. The user will ask you questions about the country and you will answer them. If the user input is not related to the game you kindly inform them that you can only answer questions about the country. If they make a false guess you tell them that this is not the right answer. Please always be polite and eloquent. You will evalute the users guesses or questions. That means if they ask general questions early in the game, like: Is the country in Africa? or: what is the official language of the country? You will praise their question. If they guess without having much information you will kindly encourage them to start with more generell questions and they should slowly try to narrow down the country they are supposed to guess. But if they guess a country that is really close to {st.session_state.country_to_guess} you tell them that they are really close. Your chat history with the user is: {chat_history_string}"  
    template_2 = f"I set up a game. The goal of the game is to guess the right country. You will know the answer and act as game master. The answer is {st.session_state.country_to_guess}. I do not know the answer. Refer to the counry in the answer as 'The Country I am thinking of'. There are two types of questions allowed. The first possible question/statement is a guess for the right solution. If the country is guessed correctly, your output is 'Congratulations! Your guessed the country correctly!'. If the country is not guessed correctly, your answer begins with 'Your answer is incorrect!'. After this give an evaluation how far the stated guess is away from the answer. The second possible question is a question that narrows the scope of the guesser. The answer should begin with 'Fact: ' and then state the correct answer to the question about the country while not revealing the name of the country. If the stated question do not pass as one of this two types of question or the question is not about finding the country, then nicely state that the goal of the game is to find the right country. Your chat history with the user is: {chat_history_string}"
    template_3 = f"I set up a game. The goal of the game is to guess the right country. You will know the answer and act as game master. The answer is {st.session_state.country_to_guess}. I do not know the answer. Refer to the counry in the answer as 'The Country I am thinking of'. State a fact about the country. Your answer starts with: 'Hint: '. This is our chat history {chat_history_string}. Do not give the same hint twice!"
    
    #setting up OpenAi API
    client = OpenAI(api_key = key)
    model = "gpt-4o-mini"

    if message:

        with st.chat_message("user"):
            st.markdown(message)

        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": template_2 + "The users newest input: " + message},
            ],
        )
        with st.chat_message("assistant"):
            st.markdown(chat_completion.choices[0].message.content)

 
        # appending the chat to chat history
        st.session_state.chat_history.append(f"User: {message}")
        st.session_state.chat_history.append(f"Your answer: {chat_completion.choices[0].message.content}")
        
        #counting guesses/inputs for stats
        st.session_state.total_number = st.session_state.total_number + 1

        #evaluating the guess by looking at longitude and latitude
        if chat_completion.choices[0].message.content[0:25] == "Your answer is incorrect!":
            #making sure the guessed country is the right one and is spelled correctly
            guessed_country = client.chat.completions.create( model=model, messages=[ {"role": "user", "content": f"Give me the name of the country the user incorrectly guessed in this conversation: {message}. The answer can not possibly be: {st.session_state.country_to_guess} The answer only consists of the name of the country. The only possible country names are in this list: {countries['Country'].to_list()}. If the name of the country is not in this list, take the name that is closest to the name out of the list" },],)
            guessed_countr_string = guessed_country.choices[0].message.content
            distance_value_in_km = evaluating_distance(st.session_state.country_to_guess, guessed_countr_string, countries)*110
            st.session_state.country_guess_number = st.session_state.country_guess_number + 1
            st.session_state.distance.append(distance_value_in_km)

            with st.chat_message("assistant"):
                st.markdown(f"The capital of the country you guessed is roughly {distance_value_in_km} km away from the capital of my country!")


            new_row2 = pd.DataFrame({'Country': [guessed_countr_string], 'Distance': [distance_value_in_km]})
            st.session_state.distance_country = pd.concat([st.session_state.distance_country, new_row2], ignore_index=True)

            

        #capturing questions that narrow down the scope
        if chat_completion.choices[0].message.content[0:5] == "Fact:":
            st.session_state.question_number = st.session_state.question_number + 1
            
        #capturing winning 
        if chat_completion.choices[0].message.content[0:15] == "Congratulations":
            st.session_state.win_bool = True
            #giving the number og guesses to a statistics dataframe
            new_row = pd.DataFrame({'Country': [st.session_state.country_to_guess], 'TotalInputs': [st.session_state.total_number], 'Hints': [st.session_state.hint_number], 'QuestionAsked': [st.session_state.hint_number], 'CountryGuesses': [st.session_state.country_guess_number], 'DistanceTraveled': [sum(st.session_state.distance)]})
            st.session_state.stats_df = pd.concat([st.session_state.stats_df, new_row], ignore_index=True)

            st.balloons()

            #winnig text display
            with st.chat_message("assistant"):
                st.markdown(f"Look at your stats or guess the next country :)")
                st.page_link("pages/2_stats.py", label="Stats", icon="1️⃣")


    #hint display if button is pressed
    elif st.session_state.hint_bool is True:
        st.session_state.hint_number = st.session_state.hint_number + 1
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": template_3 + "The user is asking for a hint."},],)

        with st.chat_message("assistant"):
            st.markdown(chat_completion.choices[0].message.content)
         
        # appending the chat to chat history
        st.session_state.chat_history.append(f"User: {message}")
        st.session_state.chat_history.append(f"Your answer: {chat_completion.choices[0].message.content}")

#resetting game if country is guessed correctly or if askey by the user
with col2:
    if (st.session_state.win_bool is True) or (st.button("New Country")):
            st.session_state.country_to_guess = get_random_country()
            st.write(st.session_state.country_to_guess)
            st.session_state.distance_country = pd.DataFrame({'Country': [ ], 'Distance': [ ]})
            del st.session_state.chat_history
            st.session_state.hint_number = 0
            st.session_state.question_number = 0
            st.session_state.total_number = 0
            st.session_state.country_guess_number = 0
            st.session_state.distance = []
            st.session_state.guessed_country_list = []
    if st.button("Reveal Answer"):
        st.write(st.session_state.country_to_guess)
        
    


#looking for the answer
#st.write("Solution: ", st.session_state.country_to_guess)
#myenv\Scripts\activate
#pip install -r requirements.txt





        