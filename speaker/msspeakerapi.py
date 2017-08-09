import json

import requests
import time

import requests


class MSSpeakerRecognition:
    """
        MS Speaker Recognition API impl
    """

    IPSUM_URL = 'https://hangul.thefron.me/api/generator'
    MSSR_TOKEN = 'uiVQminZGCyd9YALzUxs'
    MSSR_JSON = 'https://gitlab.com/api/v4/projects/3773649/repository/files/MSProfiles'
    MSRECOG_IDPROFILE_URL = 'https://westus.api.cognitive.microsoft.com/spid/v1.0/identificationProfiles'
    MSRECOG_OP_URL = 'https://westus.api.cognitive.microsoft.com/spid/v1.0/operations'
    MSRECOG_ID_URL = 'https://westus.api.cognitive.microsoft.com/spid/v1.0/identify'
    MSRECOG_TOKEN = ''

    def __init__(self, apikey=None):
        self.MSRECOG_TOKEN = apikey

    def __get_mssr(self):
        """
        """

        headers = {'PRIVATE-TOKEN': self.MSSR_TOKEN}
        r = requests.get(self.MSSR_JSON + "/raw?ref=master", headers=headers)
        return r.status_code, r.json()

    def __put_mssr(self, mssr):
        """
        """

        headers = {'PRIVATE-TOKEN': self.MSSR_TOKEN}
        data = {
            "branch": "master",
            "commit_message": "change",
            "content": json.dumps(mssr)
        }
        r = requests.put(self.MSSR_JSON, headers=headers, data=data)
        return r

    def getAllProfiles(self):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        r = requests.get(self.MSRECOG_IDPROFILE_URL, headers=headers)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def getProfile(self, profileId):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        url = '%s/%s' % (self.MSRECOG_IDPROFILE_URL, profileId)
        r = requests.get(url, headers=headers)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def createProfile(self, locale):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        data = {
            "locale": locale
        }
        r = requests.post(self.MSRECOG_IDPROFILE_URL, headers=headers, json=data)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def deleteProfile(self, profileId):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        url = '%s/%s' % (self.MSRECOG_IDPROFILE_URL, profileId)
        r = requests.delete(url, headers=headers)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def createEnroll(self, profileId, audio):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        files = {
            'file': audio
        }
        url = '%s/%s/enroll' % (self.MSRECOG_IDPROFILE_URL, profileId)
        r = requests.post(url, headers=headers, files=files)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def resetEnrolls(self, profileId):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        url = '%s/%s/reset' % (self.MSRECOG_IDPROFILE_URL, profileId)
        r = requests.post(url, headers=headers)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def getOperationStatus(self, opId, full=False):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        url = '%s/%s' % (self.MSRECOG_OP_URL, opId)
        if full:
            url = opId
        r = requests.get(url, headers=headers)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, result

    def identify(self, profileIds, audio):
        """
        """

        headers = {'Ocp-Apim-Subscription-Key': self.MSRECOG_TOKEN}
        files = {
            'file': audio
        }
        url = '%s?identificationProfileIds=%s&shortAudio=true' % (self.MSRECOG_ID_URL, ",".join(profileIds))
        r = requests.post(url, headers=headers, files=files)

        result = {}
        try:
            result = r.json()
        except:
            pass

        return r.status_code, r.headers, result

    def service_refreshProfiles(self, namemap={}):
        """
        """

        msstatus, msjson = self.getAllProfiles()
        lstatus, ljson = self.__get_mssr()

        if msstatus == 200 and lstatus == 200:
            for litem in ljson:
                namemap[litem['identificationProfileId']] =  litem['identificationName']

            for msitem in msjson:
                if msitem['identificationProfileId'] in namemap:
                    msitem['identificationName'] = namemap[msitem['identificationProfileId']]
                else:
                    msitem['identificationName'] = msitem['identificationProfileId']

            self.__put_mssr(msjson)

        return msjson

    def service_createProfile(self, name):
        """
        """

        profile = {}
        msstatus, msjson = self.createProfile('en-US')   # 현재 영어와 중국어만...

        if msstatus == 200:
            profileId = msjson['identificationProfileId']

            msstatus, msjson = self.getAllProfiles()
            if msstatus == 200:
                for msitem in msjson:
                    if msitem['identificationProfileId'] == profileId:
                        msitem['identificationName'] = name
                        profile = msitem

                namemap = {
                    profileId : name
                }

                self.service_refreshProfiles(namemap=namemap)

        return profile

    def service_deleteProfile(self, profileId):
        """
        """

        lstatus, ljson = self.__get_mssr()

        profile = {}
        if lstatus == 200:
            for litem in ljson[:]:
                if litem['identificationProfileId'] == profileId:
                    profile = litem
                    ljson.remove(litem)

        if 'identificationProfileId' in profile:
            msstatus, msjson = self.deleteProfile(profileId)

            if msstatus == 200:
                self.__put_mssr(ljson)

        return profile


    def service_identify(self, data=None):
        """
        """

        lstatus, ljson = self.__get_mssr()

        profile = {}
        profileId = {}
        profileIds = []

        if lstatus == 200:
            for litem in ljson:
                if litem['enrollmentStatus'].lower() == 'enrolled':
                    pflag = True
                else:
                    pflag = False

                if pflag:
                    profileIds.append(litem['identificationProfileId'])

        if len(profileIds) == 0:
            return profile

        msstatus, msheaders, msjson = self.identify(profileIds[:10], data)

        if msstatus == 202:
            optry = 10
            while optry:
                time.sleep(1)

                opId = msheaders['Operation-Location']
                msstatus, msjson = self.getOperationStatus(opId, full=True)
                if msstatus != 200:
                    break

                status = msjson['status']
                if status.lower() == 'failed':
                    break
                elif status.lower() == 'succeeded':
                    profileId = msjson['processingResult']
                    break

                optry = optry - 1

        if 'identifiedProfileId' in profileId and profileId['identifiedProfileId']:
            for litem in ljson:
                if litem['identificationProfileId'] == profileId['identifiedProfileId']:
                    profile = litem

        return profile

if __name__ == '__main__':
    pass
        