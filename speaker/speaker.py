# -*- coding: utf-8 -*-
"""
    MS Speaker Recognition
    ~~~~~~

    A microservice example application written as Flask tutorial with
    Flask and MS Speaker Recognition API.

    :copyright: (c) 2017 by touch@sruniverse.kr.
    :license: BSD, see LICENSE for more details.
"""

from speaker import app
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
from .msspeakerapi import MSSpeakerRecognition
import time

api = MSSpeakerRecognition('c5ab448b75ff4b86928f360dda77480b')

@app.route('/')
def show_profiles():
    profile = ''
    try:
        profile = request.args['profile']
    except:
        pass

    profiles = api.service_refreshProfiles()
    flash('프로파일 정보')
    flash('*** 음성은 16khz 모노 오디오형태로 WAV 포맷의 파일만 지원한다.')
    flash('*** 녹음은 보통 폰에서 하면 되고, 변환은 아래 링크에서 하면 된다.')
    flash('-*- 음성 등록 : 10초이상의 문구를 3번정도 반복 녹음해서 등록해주면 된다.')
    return render_template('show_profiles.html', profiles=profiles, match_profile=profile)

@app.route('/create', methods=['POST'])
def create_profile():
    name = request.form['name']
    print("===* NEW *===", name)
    if name:
        api.service_createProfile(name)
    return redirect(url_for('show_profiles'))

@app.route('/<profileId>/reset')
def reset_profile_enrollment(profileId):
    api.resetEnrolls(profileId)
    return redirect(url_for('show_profiles'))

@app.route('/<profileId>/delete')
def delete_profile(profileId):
    api.service_deleteProfile(profileId)
    return redirect(url_for('show_profiles'))

@app.route('/<profileId>/enroll', methods=['POST'])
def enroll_profile(profileId):
    fname = 'enrolldata_%s' % (profileId)
    f = request.files[fname]
    status, json = api.createEnroll(profileId, f)
    if status == 202:
        time.sleep(2)
    return redirect(url_for('show_profiles'))

@app.route('/identify', methods=['POST'])
def identify_profile():
    f = request.files['identifydata']
    profile = api.service_identify(f)

    profileId = ''
    try:
        profileId = profile['identificationProfileId']
    except:
        pass

    return redirect(url_for('show_profiles', profile=profileId))
