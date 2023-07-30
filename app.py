from flask import Flask, render_template, request, redirect, url_for
import chatbot

def format_messages(messages):
    conv = [{"role": "system", "content": "You are KFUPMBot your task is to help KFUPM university students to know more about the university's registrar, rules and regulations based on the registrar handbook. You can look up dates from the academic calendar. You can only answer question that are related to KFUPM."}]
    for i in range(len(messages)):
        if i % 2 == 0:
            conv.append({"role": "assistant", "content": messages[i]})
        else:
            conv.append({"role": "user", "content": messages[i]})
    return conv


app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for('chat'))

@app.get('/chat')
def chat():
    return render_template('chat.html')

@app.post('/chat')
def chat_post():
    messages = request.get_json('messages')['messages']
    messages = format_messages(messages)
    response = chatbot.chat(messages, verbose=True)
    return {"message": response}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') 

