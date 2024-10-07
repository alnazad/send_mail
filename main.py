import firebase_admin
from firebase_admin import credentials, firestore
from firebase_functions import https_fn
import flask
from merchandise_test import MerchandiseTest
from user import User
from company import Company
from merchandise import Merchandise
from samplebook import SampleBook
from authentication import Authentication
from authmerchandise import Authmerchandise
from authorizationministernumber import Authorizationministernumber
from authjisnumber import Authjisnumber
from notification_mail import NotificationMail
from flask_cors import CORS
from fireproofingnumber import Fireproofingnumber
from certifiedproductsclassification import Certifiedproductsclassification


app = flask.Flask(__name__)
CORS(app)
cred = credentials.Certificate('permission.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

user_instance = User()
company_instance = Company()
marchendise_instance = Merchandise()
merchendise_instance_test = MerchandiseTest()

book=SampleBook()
authmerchandise=Authmerchandise()
authenticaion=Authentication()
authorizationministernumber_instance=Authorizationministernumber()
authjisnumber=Authjisnumber()
fireproof_instance=Fireproofingnumber()
certified_instance=Certifiedproductsclassification()



 
    

@app.route('/api/send-mail', methods=['POST'])
def send_mail():
    data = flask.request.get_json()
    response, status = NotificationMail.send_mail(data)
    return flask.jsonify(response), status

if __name__ == '__main__':
    app.run(debug=True)

# -------------------------------------------------------------------------------------------------------------------








# Expose Flask app as a single Cloud Function
@https_fn.on_request()
def httpsflaskexample(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
