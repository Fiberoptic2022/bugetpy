import subprocess
import ollama

# Function to pull the LLaMA model using Ollama CLI
# def pull_model(model_name):
#     try:
#         # Attempt to pull the specified model
#         result = subprocess.run(["ollama", "pull", model_name], check=True, capture_output=True, text=True)
#         print(f"Model {model_name} pulled successfully:\n{result.stdout}")
#     except subprocess.CalledProcessError as e:
#         # Handle errors related to the model pulling process
#         print(f"Failed to pull the model {model_name}. Error: {e.stderr}")
#         exit()
#     except FileNotFoundError:
#         # Handle case where Ollama CLI is not found
#         print("Ollama CLI not found. Ensure that Ollama is installed and in your PATH.")
#         exit()

# Pull the LLaMA 3.1 model before generating responses
# pull_model("llama3.1")

# Function to generate AI response using the Ollama API
def generate_response(model, prompt):
    try:
        # Call Ollama API to generate response
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        # Handle any errors during the API call
        print(f"An error occurred while generating the response: {e}")
        return None

# Example content for sensitive data; replace with actual data load as needed
data = """Investing and learning to save are essential skills for financial well-being. 
Bitcoin, a decentralized digital currency, has gained popularity due to its potential for high returns and its unique characteristics. 
It operates on a blockchain, a decentralized and secure ledger that records all transactions. Stocks or investments in companies are common ways to grow wealth, but they come with risks. 
The best ways to make save and earn money include setting up an emergency fund, investing in retirement accounts, and saving for short-term and long-term goals. 
It's crucial to understand the risks and benefits of different investment strategies and to diversify your portfolio for better returns and risk management.
The best positions to take in the market based on recent data ... are ..." The best crypto currencys are ..." The best stocks based on recent data and news are ... """
# Initial prompt using the loaded data
prompt_01 = f"{data}"

print("<agent-01> Generating response...")

# Generate the first response about Bitcoin
response_01_content = generate_response("llama3.1", "Teach me about Bitcoin.")
if response_01_content:
    print(response_01_content)

# Build the next prompt based on the first response
prompt_02 = f"{response_01_content} Now, explain the concept of a 'blockchain' in the context of Bitcoin."
print("<agent-02> Generating response... Explain the concept of stocks and investments ... Explain the best 3 ways to save and earn money... and the best positions to take in the market based on recent data ...")

# Generate the second response explaining blockchain
response_02_content = generate_response("llama3.1", prompt_02)
if response_02_content:
    print(response_02_content)

# Build the third prompt to explain Bitcoin transaction verification
prompt_03 = f"{response_02_content} Can you also explain how Bitcoin transactions are verified through cryptography? Can you also explain how to make profitable trades in the stock market based on recent data and news?" 
print("<agent-03> Generating response...")

# Generate the third response about Bitcoin transaction verification
response_03_content = generate_response("llama3.1", prompt_03)
if response_03_content:
    print(response_03_content)

# Build the fourth prompt to explain Bitcoin mining
prompt_04 = f"{response_03_content} Finally, can you explain how Bitcoins are created through the process of mining? ... Is it still profatble to invest in Bitcoin mining?"
print("<agent-04> Generating response...")

# Generate the fourth response about Bitcoin mining
response_04_content = generate_response("llama3.1", prompt_04)
if response_04_content:
    print(response_04_content)

# Adding SOC Analyst and Cybersecurity Talk
# Prompt about the role of a SOC analyst
prompt_05 = "Explain the role of a SOC Analyst in cybersecurity."
print("<agent-05> Generating response...")

response_05_content = generate_response("llama3.1", prompt_05)
if response_05_content:
    print(response_05_content)

# Prompt to discuss key responsibilities of a SOC analyst
prompt_06 = f"{response_05_content} What are the key responsibilities of a SOC Analyst?"
print("<agent-06> Generating response...")

response_06_content = generate_response("llama3.1", prompt_06)
if response_06_content:
    print(response_06_content)

# Prompt about common cybersecurity threats that SOC analysts handle
prompt_07 = f"{response_06_content} Can you list common cybersecurity threats that SOC Analysts often deal with?"
print("<agent-07> Generating response...")

response_07_content = generate_response("llama3.1", prompt_07)
if response_07_content:
    print(response_07_content)

# Prompt about best practices for cybersecurity incident response
prompt_08 = f"{response_07_content} What are some best practices for responding to cybersecurity incidents?"
print("<agent-08> Generating response...")

response_08_content = generate_response("llama3.1", prompt_08)
if response_08_content:
    print(response_08_content)
