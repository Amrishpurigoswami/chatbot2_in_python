from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.chat.util import Chat, reflections

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Define conversation patterns (similar to the frontend responses)
pairs = [
    [r"(.*)browser(.*)", 
     ["A browser is like a magic door to the internet! It’s a program (like Google Chrome or Firefox) where you type a website’s address (like www.google.com) to visit it. To use it, open the browser on your phone or computer, type the address in the bar at the top, and press Enter!",
      "ब्राउज़र इंटरनेट का जादुई दरवाजा है! यह एक प्रोग्राम है (जैसे गूगल क्रोम या फ़ायरफ़ॉक्स) जहाँ आप वेबसाइट का पता (जैसे www.google.com) टाइप करते हैं। इसे इस्तेमाल करने के लिए, अपने फोन या कंप्यूटर पर ब्राउज़र खोलें, ऊपर की बार में पता टाइप करें, और Enter दबाएँ!"]],
    [r"(.*)email(.*)", 
     ["An email is like sending a letter, but instantly, across the world! To set up an email account: 1. Open Gmail or another email app. 2. Click 'Create Account'. 3. Enter your name, choose a username (like yourname@gmail.com), and set a password. 4. Follow the steps to verify your phone number. Now you can send emails to your family!",
      "ईमेल एक तुरंत भेजा जाने वाला पत्र है, जो पूरी दुनिया में जाता है! खाता बनाने के लिए: 1. Gmail या दूसरा ईमेल ऐप खोलें। 2. 'खाता बनाएँ' पर क्लिक करें। 3. अपना नाम डालें, एक उपयोगकर्ता नाम चुनें (जैसे yourname@gmail.com), और पासवर्ड सेट करें। 4. फोन नंबर सत्यापित करें। अब आप परिवार को ईमेल भेज सकते हैं!"]],
    [r"(.*)upi|pay bills(.*)", 
     ["UPI is like a digital wallet for quick payments! To pay bills online: 1. Download a UPI app like Google Pay or PhonePe. 2. Link your bank account. 3. Choose 'Pay Bills', select your bill (like electricity or mobile), enter the amount, and confirm with your PIN. Always check the recipient’s details to stay safe!",
      "UPI एक डिजिटल वॉलेट की तरह है! बिल भुगतान के लिए: 1. Google Pay या PhonePe जैसे UPI ऐप डाउनलोड करें। 2. अपने बैंक खाते को लिंक करें। 3. 'बिल भुगतान' चुनें, बिल (जैसे बिजली या मोबाइल) चुनें, राशि डालें, और अपने PIN से पुष्टि करें। हमेशा प्राप्तकर्ता के विवरण की जाँच करें!"]],
    [r"(.*)wifi|wi-fi(.*)", 
     ["Wi-Fi troubles? Don’t worry, I’ve got the 'mantra' to fix it! Try these: 1. Turn Wi-Fi off and on in your phone’s settings. 2. Check if the Wi-Fi password is correct. 3. Restart your router by unplugging it for 30 seconds. Still stuck? Let me know more!",
      "Wi-Fi में परेशानी? चिंता न करें, मेरे पास इसका 'मंत्र' है! 1. फोन की सेटिंग में Wi-Fi को बंद और चालू करें। 2. Wi-Fi पासवर्ड की जाँच करें। 3. राउटर को 30 सेकंड के लिए अनप्लग करके पुनः शुरू करें। अभी भी अटक गए? मुझे और बताएँ!"]],
    [r"(.*)app not opening(.*)", 
     ["App not opening? Let’s fix it like a pro! 1. Restart your phone. 2. Check if your phone has enough storage (Settings > Storage). 3. Update the app in the Play Store or App Store. If it’s still not working, try uninstalling and reinstalling the app.",
      "ऐप नहीं खुल रहा? चलो इसे प्रो की तरह ठीक करें! 1. फोन को रीस्टार्ट करें। 2. स्टोरेज की जाँच करें (सेटिंग्स > स्टोरेज)। 3. Play Store या App Store से ऐप अपडेट करें। अगर फिर भी नहीं चलता, ऐप को अनइंस्टॉल करके फिर से इंस्टॉल करें।"]],
    [r"(.*)safety|scam(.*)", 
     ["Online safety is like locking your home! Never share passwords or personal details. Watch out for messages asking for money or OTPs – they might be scams. Use strong passwords, like mixing your favorite ‘ladoo’ name with numbers (e.g., Ladoo1234).",
      "ऑनलाइन सुरक्षा घर को ताला लगाने जैसी है! पासवर्ड या निजी जानकारी कभी साझा न करें। पैसे या OTP माँगने वाले संदेशों से सावधान रहें – ये घोटाले हो सकते हैं। मजबूत पासवर्ड बनाएँ, जैसे अपनी पसंदीदा 'लड्डू' के नाम के साथ नंबर (जैसे Ladoo1234)।"]],
    [r"(.*)whatsapp(.*)", 
     ["Using WhatsApp is like chatting over chai! 1. Download WhatsApp from the Play Store or App Store. 2. Verify your phone number. 3. Find your family in Contacts, tap their name, and send a message or make a video call. Keep it simple and enjoy staying connected!",
      "व्हाट्सएप का उपयोग चाय पर गपशप करने जैसा है! 1. Play Store या App Store से व्हाट्सएप डाउनलोड करें। 2. अपने फोन नंबर को सत्यापित करें। 3. संपर्कों में अपने परिवार को ढूँढें, उनके नाम पर टैप करें, और संदेश भेजें या वीडियो कॉल करें। सरल रखें और जुड़े रहें!"]],
    [r"(.*)", 
     ["Learning is a lifelong journey, like a beautiful 'yatra' (pilgrimage). You’re doing amazing!",
      "सीखना एक आजीवन यात्रा है, जैसे एक सुंदर 'यात्रा'। आप शानदार कर रहे हैं!"]]
]

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

# Initialize NLTK chatbot
chatbot = Chat(pairs, reflections)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input', '')
    language = data.get('language', 'en')
    response = chatbot.respond(user_input)
    # Select response based on language (0 for English, 1 for Hindi)
    response_text = response[0] if language == 'en' else response[1]
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
