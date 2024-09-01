import os
from flask import Flask, render_template,request,redirect, url_for
from werkzeug.utils import secure_filename
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import PyPDF2  #

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/',methods=['GET','POST'])
def home():
    messages=''
    if request.method == 'POST':
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('process', filename=filename))
    
    return render_template('index.html',message=messages)


@app.route('/process/<filename>',methods=['GET'])
def process(filename):
    filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    GROQ_API_KEY = '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'
    groq_api_key = GROQ_API_KEY
    llm = ChatGroq(groq_api_key=groq_api_key,
                model_name="Llama3-8b-8192")
    prompt_template = """
    Extract the following details from the resume in each line with headings like Name, Email, Phone number Experience avoid Unnecessary ***:
    - Name
    - Email
    - Phone Number
    - Experience

    <Context>
    {context}
    <Context>
    """

   
    uploaded_file = filepath

    if uploaded_file:
        
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        
       
        prompt = prompt_template.format(context=text)
        
        
        response = llm.invoke(input=prompt)
        
       
        print("Extracted Information:")
        print(response.content)
        lst=response.content.split('\n')
        # print(lst)
        # print(lst[2])
        Name=lst[2]
        Email=lst[4]
        Phone_Number=lst[6]
        Experience=''.join(lst[8:])
        print(Experience)
        # print(lst[8:])

    return render_template('result.html',content=response.content,Name=Name,Email=Email,Phone_Number=Phone_Number,Experience=Experience)

# Run the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=True)