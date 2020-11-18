from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response, send_file
from flask import current_app as app
import requests
from google.cloud import texttospeech
from google.oauth2 import service_account

from data.Clinic import Clinic
from data.Covid import Covid
from data.CovidResult import CovidResult
from data.Festival import Festival
from rule_loader import rule_loader
from rule_process import rule_process
import datetime
from dateutil.relativedelta import relativedelta

main = Blueprint('main', __name__, url_prefix='/')

rl = rule_loader(None)
rl.load('slotminer/rule/intent.rule')
rl.load('slotminer/rule/location.rule')
rl.load('slotminer/rule/timex3.rule')
if not rl.generate_rules():
    exit()
rp = rule_process(rules=rl.get_rules(), logger=None)

rp.indexing()
use_indexing = True

@main.route('/', methods=['GET'])
def index():
    return "It works!"


@main.route('/chat/<msg>', methods=['GET'])
def chat(msg: str):
    result, variables, matched = rp.process(msg, indexing=use_indexing)

    print(result)
    slot_types = {s['name']: s for s in result}

    if 'slot_covid' not in slot_types:
        return {'resp': '무슨 말씀이신지 잘 모르겠어요.'}

    slot_type = slot_types['slot_covid']['covid']
    if slot_type in ['확진', '사망']:
        date = datetime.date.today()
        if 'slot_timex3' in slot_types:
            time = slot_types['slot_timex3']
            if 'week' in time:
                date += datetime.timedelta(days=int(time['week']) * 7)
            if 'week_day' in time:
                weekday = (date.weekday() + 1) % 7
                date += datetime.timedelta(days=int(time['week_day']) - weekday)

            year, month, day = None, None, None
            if 'day' in time:
                if time['day'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['day']))
                else:
                    day = int(time['day'])
            if 'month' in time:
                if time['month'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['month']))
                else:
                    month = int(time['month'])
            if 'year' in time:
                if time['year'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['year']))
                else:
                    year = int(time['year'])

            if year or month or day:
                try:
                    date = datetime.date(year if year else date.year, month if month else date.month,
                                         day if day else date.day)
                except:
                    pass

        locale = '전국'
        if 'slot_location' in slot_types:
            locale = slot_types['slot_location']['location']
        result = Covid.get_by_date_locale(date, locale)
        if result is not None:
            return {
                'resp': '%s %s의 신규 확진자는 %s명, 누적 확진자는 %s명입니다' % (
                    date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                    locale, result.new_confirm, result.cum_confirm)
            } if slot_type == '확진' else {
                'resp': '%s %s의 신규 사망자는 %s명, 누적 사망자는 %s명입니다' % (
                    date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                    locale, result.new_dead, result.cum_dead)
            }
        else:
            result = CovidResult.get_by_date_locale(date, locale)
            if result is not None:
                return {
                    'resp': '%s %s의 신규 확진자는 %s명으로 예상됩니다.' % (
                    date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                    locale, result.confirm)
                } if slot_type == '확진' else {
                    'resp': '%s %s의 신규 사망자는 %s명으로 예상됩니다.' % (
                    date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                    locale, result.dead)
                }
            else:
                return {'resp': '해당 날짜의 데이터가 없습니다. 첫 확진자 발생일부터 오늘 기준 일주일 후까지의 날짜를 선택해주세요.'}
    elif slot_type == '진료소':
        locale = [slot_types['slot_location']['location'] if 'slot_location' in slot_types else None,
                  slot_types['slot_city']['city'] if 'slot_city' in slot_types else None]

        if locale[0] is not None or locale[1] is not None:
            ret = Clinic.get_from_locale(locale[0], locale[1])
            return {
                'resp': '%s의 선별진료소는 아래와 같습니다.\n\n\n%s' % (
                    ' '.join([l for l in locale if l is not None]), '\n\n'.join([
                        '진료소 이름: %s\n주소: %s\n운영시간: 주중 - %s, 토 - %s, 공휴일 - %s\n문의: %s' % (
                            clinic.name, clinic.address,
                            clinic.weekday, clinic.saturday, clinic.holiday, clinic.contact)
                        for clinic in ret])),
                'voice': '%s의 선별진료소는 %s곳 있습니다. 자세한 정보는 내용을 확인해주세요.' %(' '.join([l for l in locale if l is not None]), len(ret))
            } if len(ret) > 0 else {
                'resp': '%s의 선별진료소 정보가 없습니다.' % (' '.join([l for l in locale if l is not None]))
            }
        else:
            return {'resp': '지역을 알 수 없습니다. 더 넓은 지역으로 다시 물어봐주세요.'}
    elif slot_type == '축제':
        date = datetime.date.today()
        if 'slot_timex3' in slot_types:
            time = slot_types['slot_timex3']
            if 'week' in time:
                date += datetime.timedelta(days=int(time['week']) * 7)
            if 'week_day' in time:
                weekday = (date.weekday() + 1) % 7
                date += datetime.timedelta(days=int(time['week_day']) - weekday)

            year, month, day = None, None, None
            if 'day' in time:
                if time['day'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['day']))
                else:
                    day = int(time['day'])
            if 'month' in time:
                if time['month'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['month']))
                else:
                    month = int(time['month'])
            if 'year' in time:
                if time['year'][0] in ['+', '-']:
                    date += datetime.timedelta(days=int(time['year']))
                else:
                    year = int(time['year'])

            if year or month or day:
                try:
                    date = datetime.date(year if year else date.year, month if month else date.month,
                                         day if day else date.day)
                except:
                    pass

        locale = [slot_types['slot_location']['location'] if 'slot_location' in slot_types else None,
                  slot_types['slot_city']['city'] if 'slot_city' in slot_types else None]

        if locale[0] is not None or locale[1] is not None:
            ret = Festival.get_from_date_locale(date, locale[0], locale[1])
            return {
                'resp': '%s에 %s에서 열리는 축제는 아래와 같습니다.\n\n\n%s' % (
                    date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                    ' '.join([l for l in locale if l is not None]), '\n\n'.join([
                        '축제 이름: %s\n지역: %s\n기간: %s ~ %s%s\n문의: %s' % (
                            fest.name, ' '.join([l for l in [fest.province, fest.city] if l is not None]),
                            fest.start.strftime('%Y-%m-%d') if fest.start is not None else ' ',
                            fest.end.strftime('%Y-%m-%d') if fest.end is not None else ' ',
                            ', ' + fest.time if fest.time is not None else '', fest.contact)
                        for fest in ret])),
                'voice': '%s에 %s에서 열리는 축제는 %s건으로 자세한 정보는 내용을 확인해주세요.' % (
                date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                ' '.join([l for l in locale if l is not None]), len(ret))
            } if len(ret) > 0 else {
                'resp': '%s에 %s에서 열리는 축제 정보가 없습니다.' % (
                date.strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()).encode().decode('unicode-escape'),
                ' '.join([l for l in locale if l is not None]))
            }
        else:
            return {'resp': '지역을 알 수 없습니다. 더 넓은 지역으로 다시 물어봐주세요.'}
    elif slot_type == '증상':
        return {
            'resp': '코로나바이러스감염증-19의 가장 흔한 증상은 발열, 마른 기침, 피로이며 그 외에 후각 및 미각 소실, 근육통, 인후통, 콧물, 코막힘, 두통, 설사 등 다양한 증상이 나타날 수 있습니다.'}

    return {'resp': '무슨 말씀이신지 잘 모르겠어요.'}


@main.route('/voice/<msg>', methods=['GET'])
def voice(msg: str):
    print(msg)
    if len(msg) > 1000:
        msg = '문장이 너무 길어 음성 송출이 불가합니다.'
        print(msg)

    credentials = service_account.Credentials.from_service_account_file('covid-chatbot-295721-9fbe2c2b2008.json')
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    synthesis_input = texttospeech.SynthesisInput(text=msg)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ko_KR", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open('app/temp/output.mp3', 'wb') as f:
        f.write(response.audio_content)

    return send_file('temp/output.mp3', as_attachment=True)
