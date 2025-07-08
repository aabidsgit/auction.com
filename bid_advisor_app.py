import streamlit as st
import pandas as pd
import openai
import os

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
from dotenv import load_dotenv
load_dotenv()

st.title("🏡 Auction Bid Advisor (MVP)")
st.write("Enter property details to get a smart bid estimate based on historical auction data.")

# --- User Inputs ---
zip_code = st.text_input("ZIP Code")
starting_bid = st.number_input("Starting Bid ($)", step=1000)
beds = st.number_input("Beds", step=1)
baths = st.number_input("Baths", step=1)
condition = st.selectbox("Condition", ["poor", "average", "good"])
occupancy = st.selectbox("Occupancy", ["vacant", "tenant"])
auction_type = st.selectbox("Auction Type", ["online", "live"])

# --- Load Data ---
df = pd.read_csv("ca_auction_data_100k.csv")

# --- Flexible Matching Logic ---
comps = df[
    (df['zip'] == zip_code) &
    (abs(df['beds'] - beds) <= 1) &
    (df['condition'].isin([condition, 'average']))
]

# Fallback: no ZIP match, but similar beds and condition
if comps.empty:
    comps = df[
        (abs(df['beds'] - beds) <= 1) &
        (df['condition'].isin([condition, 'average']))
    ]

# --- Trigger on Button Click ---
if st.button("Estimate Bid Range"):
    if comps.empty:
        st.warning("Still no similar properties found. Try changing inputs.")
    else:
        # Create prompt for GPT-4
        prompt = f"""
You are a Bid Advisor AI trained on historical foreclosure and auction data.

A user is considering bidding on a property with:
- ZIP: {zip_code}
- Beds: {beds}
- Baths: {baths}
- Condition: {condition}
- Starting Bid: ${starting_bid}
- Occupancy: {occupancy}
- Auction Type: {auction_type}

Here are some similar past properties:
{comps.head(5).to_string(index=False)}

Based on this data, recommend a smart bid range (low to high estimate) for this property and provide a brief 2-line rationale.
        """

        # --- Call OpenAI API ---
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            answer = response['choices'][0]['message']['content']
            st.success(answer)

        except Exception as e:
            st.error(f"OpenAI API call failed: {e}")
