import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve and print the variables to verify they are set
groq_api_key = os.getenv("GROQ_API_KEY")
chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")

print("GROQ_API_KEY:", groq_api_key)
print("CHROME_PROFILE_PATH:", chrome_profile_path)
