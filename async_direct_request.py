import requests
import asyncio
import aiohttp
import logging
from scrape import profile_request_params, country_request_params

# setup error message texts
BAD_RESPONSE_TEXT = "National Examination Agency system could not get your result data. " \
                    "Please be sure you used the right admission number and try again. "
CONN_TIMEOUT_TEXT = "National Examination Agency system could not be connected. " \
                    "Please, try again."
REQUEST_EXCEPTION_TEXT = "Connection with National Examination Agency system is not working. " \
                         "Please be sure you used the right admission number and try again."

# response json keys
STUDENT_ID = 'Id'
STUDENT_NAME = 'FullName'
CHOICE_NUMBER = 'ChoiceNumber'
IS_SELECTED = 'IsSelected'

# setup logging config
logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s: %(message)s")

# setup reusable request objects
profile_request = profile_request_params()
country_request = country_request_params()


async def on_request_start(session, trace_config_ctx, params):
    print('Starting request: ', params)


async def get_student_info(admission_number):
    """
    Get wanted student information from site directly

    Args:
        admission_number: str

    Returns:
        tuple: (
            bool: is there error?,
            str: student info message text or error message text
        )
    """
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
        # set student admission number for student profile request
        profile_request.data['admissionNumber'] = admission_number

        try:
            # request student profile to get system student id and student name
            profile_response = await session.request(
                profile_request.method, profile_request.url, headers=profile_request.headers,
                cookies=profile_request.cookies, data=profile_request.data, raise_for_status=True)

            # validate and extract profile data from response
            profile_json = await profile_response.json()
            if len(profile_json) != 1:  # unexpected profile json
                logging.warning(
                    f"Profile response json has unexpected structure: profile_json={profile_json}\n"
                    f"Request for admission_number: {admission_number}")
                return True, BAD_RESPONSE_TEXT
            else:
                profile_data = profile_json[0]

            # get system student id from profile data
            student_id = profile_data.get(STUDENT_ID)

            # validate extracted student id
            if student_id is None:  # could not get student id from profile json
                logging.warning(
                    f"Profile data doesn't contain expected id: profile_data={profile_data}\n"
                    f"Request for admission_number: {admission_number}")
                return True, BAD_RESPONSE_TEXT

            # set student id and setup country request
            country_request.params['id'] = student_id

            # send request to get country data of student
            country_response = await session.request(
                country_request.method, country_request.url, headers=country_request.headers,
                params=country_request.params, raise_for_status=True
            )

            # extract country data of student
            country_data = await country_response.json()

            # validate extracted country data
            if len(country_data) < 1:  # unexpected country json
                logging.warning(
                    f"Country response json has unexpected structure: country_data={country_data}\n"
                    f"Request for admission_number: {admission_number}, student_id: {student_id}")
                return True, BAD_RESPONSE_TEXT
        except requests.exceptions.ConnectTimeout:  # safe to retry connection
            logging.warning(f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, CONN_TIMEOUT_TEXT
        except requests.exceptions.ReadTimeout:  # server did not send any data in allotted time
            logging.warning(f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, BAD_RESPONSE_TEXT
        except requests.exceptions.ConnectionError:
            logging.warning(f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, REQUEST_EXCEPTION_TEXT
        except requests.exceptions.HTTPError:  # includes raise_for_status() errors
            logging.warning(f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, BAD_RESPONSE_TEXT
        except requests.exceptions.RequestException:  # catch all for requests exception
            logging.warning(f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, REQUEST_EXCEPTION_TEXT

        # create appropriate result message text
        message_text = create_result_text(profile_data, country_data)
        # print('text: ', message_text)

        # join the lines above to create the message text
        return False, message_text


def create_result_text(profile_data, country_data):
    """
    Create up appropriate text to be returned to user

    Args:
        profile_data: json dict
        country_data: json dict

    Returns:
        str: message text
    """
    # set up lines of text for response message text
    lines = [
        profile_data[STUDENT_NAME]
        # get_assigned_campus(country_data)   # uncomment this line if no change detected
    ]

    # get top choices of campus
    choices_lines = top_choices_lines(country_data)

    # append top choices lines
    lines.extend(choices_lines)

    return "\n".join(lines)


def top_choices_lines(country_data):
    """
    Get top three choices of campus from country data json dict
    formatted as message text line

    Args:
        country_data: json dict

    Returns:
        list of text lines
    """
    wanted_choices = {1, 2, 3}
    found_choices = 0
    lines = [
        None,  # 1 country choice
        None,  # 2 country choice
        None,  # 3 country choice
    ]
    for country in country_data:
        # search for wanted choices and setup text lines
        choice_number = country[CHOICE_NUMBER]
        if choice_number in wanted_choices:
            lines[choice_number - 1] = f"{choice_number}. {country['Name']}"
            found_choices += 1

            # break if we found all we came for
            if found_choices == 3:
                break

    return lines


def get_assigned_campus(country_data):
    """
    Get assigned campus from country_data json dict
    formatted as message text
    Args:
        country_data: json dict

    Returns:
        str: assigned campus name
    """
    for country in country_data:
        if country[IS_SELECTED] is True:
            return f'Your assigned campus is {country_data[Name]}'

    return 'National Examination Agency have not released campus information for new students yet.\n' \
           'Please, try again later.'


if __name__ == '__main__':
    asyncio.run(get_student_info('001001'))
