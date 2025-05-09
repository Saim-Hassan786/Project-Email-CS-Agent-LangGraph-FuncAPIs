from langgraph.func import entrypoint, task
from litellm import completion
from dotenv import load_dotenv , find_dotenv
from typing import TypedDict, List, Dict
import os

_: bool = load_dotenv(find_dotenv(".env"))
api_key = os.getenv('GOOGLE_API_KEY')


@task
def extract_issue(customer_email: str) -> str:
    """The Main Goal of this function is to extract the main issue from the customer email"""
    response = completion(
        model = "gemini/gemini-2.0-flash-exp",
        api_key = api_key,
        messages = [{
            "role": "user",
            "content": f"Extract the main issues and concerns from the following customer email: {customer_email}"
        }]
    )
    result = response["choices"][0]["message"]["content"]
    return result

@task
def draft_response(issue: str) -> str:
    """The Main Goal of this function is to draft a response to the customer based on the issue"""
    response = completion(
        model = "gemini/gemini-2.0-flash-exp",
        api_key = api_key,
        messages = [{
            "role": "user", 
            "content": f"""
            You are a very experienced customer support agent.
            Always be professional, friendly and empathetic in all of your responses to the customers emails
            Draft a response to the customer based on the following issue: {issue}"""
        }]
    )
    result = response["choices"][0]["message"]["content"]
    return result

def check_tone(response: str) -> str:
    """The Main Goal of this function is to check the tone of the response whether its response is empathetic or not"""
    if "sorry" in response.lower() or "thank" in response.lower():
        return True
    else:
        return False
    
@task
def refine_response(response: str) -> str:
    """The Main Goal of this function is to refine the response based on the tone of the response to make it more empathetic and apologetic"""
    response = completion(
        model = "gemini/gemini-2.0-flash-exp",
        api_key = api_key,
        messages = [{
            "role": "user",
            "content": f"""
                    Your role is to refine responses to customer emails. 
                    You focuses on enhancing the professionalism, friendliness, and empathy in the communication. 
                    The goal is to ensure that every customer feels heard, valued, and supported. 
                    Your main aim is to transform a standard response into one that acknowledges the customer's situation with genuine understanding, expressing sincere apologies where necessary, and maintains a helpful, positive tone throughout.
                    Refine the following response to make it more empathetic and apologetic: {response}"""
        }]
    )
    result = response["choices"][0]["message"]["content"]
    return result


@task
def polish_response(response: str) -> str:
    """The Main Goal of this function is to polish the response to make it more professional , friendly and effective"""
    response = completion(
        model = "gemini/gemini-2.0-flash-exp",
        api_key = api_key,
        messages = [{
            "role": "user",
            "content": f"""
                      Please enhance the following customer support response to ensure it is more professional, empathetic, and friendly.
                      The goal is to make the response sound warm, understanding, and considerate, while maintaining professionalism. 
                      Aim to improve the overall tone, ensuring the customer feels valued and supported, and that the message is clear, effective, and solution-focused.
                      Just Give your response in the form of an Email not any other details
                      Company Name : HappyMart
                      Your Name : Saim Hassan
                      Response to refine: {response}"""
        }]
    )
    result = response["choices"][0]["message"]["content"]
    return result   

@task
def save_response(response: str) -> str:
    """The Main Goal of this function is to save the response to the database"""
    with open("CustomerSupportResponse.md","w") as f:
        f.write(response)
    print("Response Saved Successfully")
    return response



@entrypoint()
def complete_workflow(customer_email=None):
    """The Main Goal of this function is to complete the workflow"""
    customer_email = input("Enter Your Email Here : ")
    issues = extract_issue(customer_email).result()
    drafted_response = draft_response(issues).result()
    if check_tone(drafted_response) == True:
        final_response = polish_response(drafted_response).result()
    else:
        refined_response = refine_response(drafted_response).result()
        final_response = polish_response(refined_response).result()
    save_response(final_response).result()
    return {
        "Issues" : issues,
        "Draft Response" : drafted_response,
        "Final Response" : final_response
    }

def main_flow():
    obj = complete_workflow.invoke("I recently dined at your hotel and was thoroughly impressed by both the exquisite cuisine and the impeccable service. The menu showcased a variety of innovative dishes, blending bold flavors and beautiful presentation. The attentive and knowledgeable staff ensured that our meal was a memorable one, providing excellent recommendations and ensuring our satisfaction. I cannot recommend your hotel enough for a fantastic dining experience.")
    print(obj)












