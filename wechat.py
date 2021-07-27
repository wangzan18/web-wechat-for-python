from flask import Flask, render_template, session, jsonify
import time, requests, re
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'wangzan18'
QCODE = ""
TIP = "1"

def xml_parser(text):
    """
    格式化xml数据，修改成我们需要的格式
    :param text:
    :return:
    """
    dic = {}
    soup = BeautifulSoup(text, 'html.parser')
    for item in soup.find(name='error').children:
        dic[item.name] = item.text
    return dic


@app.route('/login')
def login():
    global QCODE
    ctime = time.time()
    response = requests.get(url="https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&fun=new&lang=zh_CN&_={}".format(ctime))
    QCODE = re.findall('QRLogin.uuid = "(.*)";',response.text)[0]
    return render_template('login.html', qcode = QCODE)


@app.route('/check-login')
def check_login():
    global TIP
    res_code = { 'code': 408}
    ctime = time.time()
    response = requests.get(url="https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={}&tip={}&r=511134484&_={}".format(QCODE, TIP, ctime))
    if 'code=201' in response.text:
        userAvatar = re.findall("window.userAvatar = '(.*)';", response.text)
        res_code['code'] = 201
        TIP = "0"
        res_code['avatar'] = userAvatar
        return jsonify(res_code)

    elif 'code=200' in response.text:
        redirect_uri = re.findall('window.redirect_uri="(.*)";', response.text)[0] + "&fun=new&version=v2&lang=zh_CN"
        res_ticket = requests.get(url=redirect_uri)
        session['ticket'] = xml_parser(res_ticket.text)
        res_code['code'] = 200
        return jsonify(res_code)
    else:
        return jsonify(res_code)



@app.route('/index')
def index():
    ticket = session.get('ticket')
    data_dict = {
        "BaseRequest": {
                "Sid": ticket.get('wxsid'),
                "Uin": ticket.get('wxuin'),
                "Skey": ticket.get('skey'),
            }
    }
    response = requests.post(url='https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=497741509&pass_ticket='+ticket['pass_ticket'], json= data_dict)
    response.encoding = 'utf-8'
    user_dict = response.json()
    session['current_user_info'] = user_dict['User']
    return render_template('index.html', user_dict=user_dict)

@app.route('/contactlist')
def contactlist():
    ticket = session.get('ticket')
    pass
    return "200"




if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')