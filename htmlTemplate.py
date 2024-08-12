import base64  
  
css = '''  
<style>  
.chat-message {  
    padding: 1.5rem;  
    border-radius: 0.5rem;  
    margin-bottom: 1rem;  
    display: flex;  
}  
.chat-message.user {  
    background-color: #2b313e;  
}  
.chat-message.bot {  
    background-color: #475063;  
}  
.chat-message .avatar {  
    width: 20%;  
}  
.chat-message .avatar img {  
    max-width: 78px;  
    max-height: 78px;  
    border-radius: 50%;  
    object-fit: cover;  
}  
.chat-message .message {  
    width: 80%;  
    padding: 0 1.5rem;  
    color: #fff;  
}  
</style>  
'''  
  
def load_image_as_base64(image_path):  
    with open(image_path, "rb") as image_file:  
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")  
    return encoded_image  
  
bot_image_base64 = load_image_as_base64("C:/Users/v-sukruthav/Downloads/llms/images/chat.jpg")  
user_image_base64 = load_image_as_base64("C:/Users/v-sukruthav/Downloads/llms/images/chat1.jpg")  
  
bot_template = f'''  
<div class="chat-message bot">  
    <div class="avatar">  
        <img src="data:image/jpeg;base64,{bot_image_base64}" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">  
    </div>  
    <div class="message">{{{{MSG}}}}</div>  
</div>  
'''  
  
user_template = f'''  
<div class="chat-message user">  
    <div class="avatar">  
        <img src="data:image/jpeg;base64,{user_image_base64}">  
    </div>  
    <div class="message">{{{{MSG}}}}</div>  
</div>  
'''  
  

