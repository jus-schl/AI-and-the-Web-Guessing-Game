import streamlit as st
import pandas as pd

st.title( "Statistics Page")
if len(st.session_state.distance_country) > 0:
    st.subheader(f"Your last guess was {st.session_state.distance_country.iloc[-1][1]} km away.")

    st.line_chart(st.session_state.distance_country, x = 'Country', y = 'Distance')


st.write(f"Average amount of inputs needed: {round(st.session_state.stats_df['TotalInputs'].mean(), 2)}")
st.write(f"Average amount of hints needed: {round(st.session_state.stats_df['Hints'].mean(), 2)}")
st.write(f"Average amount of questions needed: {round(st.session_state.stats_df['QuestionAsked'].mean(), 2)}")
st.write(f"Average amount of country guesses needed: {round(st.session_state.stats_df['CountryGuesses'].mean(), 2)}")


# creating line chart (we do not know why it is sorted alphabetically)
st.bar_chart(st.session_state.stats_df, x = 'Country', y = ['TotalInputs','Hints','QuestionAsked', 'CountryGuesses'], stack = False)
st.line_chart(st.session_state.stats_df, x = 'Country', y = ['DistanceTraveled'])

st.write(st.session_state.stats_df)

