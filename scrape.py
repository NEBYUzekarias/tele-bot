from collections import namedtuple
import requests
import aiohttp
from parsel import Selector

from utils import timer


def setup_profile_request():
    headers = {
        'user-agent': ('Mozilla/5.0'),
    }

    response = requests.get(
        'http://portal.neaea.gov.et/Home/Student', headers=headers)

    must_cookies = {}  # can be cookie jar
    must_cookies_names = ['__RequestVerificationToken']
    for cookie_name in must_cookies_names:
        must_cookies[cookie_name] = response.cookies.get(cookie_name)

    html = Selector(text=response.text)
    csrf_token = html.xpath("/html/body/div[2]/div/form/input/@value").get()

    form_data = {
        '__RequestVerificationToken': csrf_token,
        'admissionNumber': None  # to be set
    }
    request = requests.Request('POST', url='http://portal.neaea.gov.et/Student/StudentDetailsx',
                               headers=headers, data=form_data, cookies=must_cookies)

    return request


request_params_fields = ('method', 'url', 'headers',
                         'cookies', 'params', 'data')
RequestParams = namedtuple(
    'RequestParams',
    request_params_fields,
    # to make fields optional when creating object
    defaults=(None,) * len(request_params_fields)
)


def campus_request_params(session):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'http://twelve.neaea.gov.et/Home/Placement',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.get(
        'http://twelve.neaea.gov.et/Home/Placement')

    must_cookies = {}  # can be cookie jar
    must_cookies_names = ['__RequestVerificationToken']
    for cookie_name in must_cookies_names:
        must_cookies[cookie_name] = response.cookies.get(cookie_name)
    # print('must_cookies:', must_cookies)

    html_text = response.text

    html = Selector(text=html_text)
    csrf_token = html.xpath(
        '//*[@id="searchform"]/div[1]/div[2]/form/input/@value').get()

    form_data = {
        '__RequestVerificationToken': csrf_token,
        'Registration_Number': None  # to be set
    }
    # print('form_data:', form_data)

    return RequestParams(
        method='POST',
        url='http://twelve.neaea.gov.et/Home/Placement',
        headers=headers,
        cookies=must_cookies,
        data=form_data
    )


def profile_request_params():
    headers = {
        'user-agent': ('Mozilla/5.0'),
    }

    response = requests.get(
        'http://portal.neaea.gov.et/Home/Student', headers=headers)

    must_cookies = {}  # can be cookie jar
    must_cookies_names = ['__RequestVerificationToken']
    for cookie_name in must_cookies_names:
        must_cookies[cookie_name] = response.cookies.get(cookie_name)

    html = Selector(text=response.text)
    csrf_token = html.xpath("/html/body/div[2]/div/form/input/@value").get()

    form_data = {
        '__RequestVerificationToken': csrf_token,
        'admissionNumber': None  # to be set
    }

    return RequestParams(
        method='POST',
        url='http://portal.neaea.gov.et/Student/StudentDetailsx',
        headers=headers,
        cookies=must_cookies,
        data=form_data
    )


def extract_profile_data(profile_response):
    return profile_response.json()[0]


def setup_country_request():
    headers = {
        'user-agent': ('Mozilla/5.0'),
    }

    query_params = {
        'id': None  # to be set
    }
    request = requests.Request('GET', url='http://portal.neaea.gov.et/Student/Institute',
                               headers=headers, params=query_params)
    return request


def country_request_params():
    headers = {
        'user-agent': ('Mozilla/5.0'),
    }

    query_params = {
        'id': None  # to be set
    }
    request = requests.Request('GET', url='http://portal.neaea.gov.et/Student/Institute',
                               headers=headers, params=query_params)
    return RequestParams(
        method='GET',
        url='http://portal.neaea.gov.et/Student/Institute',
        headers=headers,
        params=query_params
    )


def extract_country_data():
    pass


def get_student_ids():
    return range(317885, 317895)


@timer
def scrape():
    for student_id in get_student_ids():
        profile_request = setup_profile_request()
        country_request = setup_country_request()
        with requests.Session() as session:
            # set student admission number in request
            profile_request.data['admissionNumber'] = student_id
            student_profile_request = profile_request.prepare()

            profile_response = session.send(student_profile_request)
            profile_data = extract_profile_data(profile_response)
            print(profile_data)

            # set student id
            country_request.params['id'] = profile_data['Id']
            student_country_request = country_request.prepare()

            country_response = session.send(student_country_request)
            # print(country_response)


def get_student_country(student_id):
    profile_request = setup_profile_request()
    country_request = setup_country_request()
    with requests.Session() as session:
        # set student admission number in request
        profile_request.data['admissionNumber'] = student_id
        student_profile_request = profile_request.prepare()

        profile_response = session.send(student_profile_request)
        profile_data = extract_profile_data(profile_response)
        print(profile_data)

        # set student id
        country_request.params['id'] = profile_data['Id']
        student_country_request = country_request.prepare()

        country_response = session.send(student_country_request)
        print(country_response)


if __name__ == "__main__":
    scrape()
