import requests
import asyncio
import aiohttp
import logging
from scrape import profile_request_params, country_request_params, campus_request_params

# setup error message texts
NO_MDEBA_DATA_TEXT = "There is no data regarding your assigned university on National Examination Agency system. Please, try again later"
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
# profile_request = profile_request_params()
# country_request = country_request_params()
campus_request = campus_request_params(None)


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
        # campus_request = await campus_request_params(session)
        # print('s.cookies: ', session.cookie_jar)
        # set student admission number for student profile request
        campus_request.data['Registration_Number'] = str(admission_number)

        try:
            # request student profile to get system student id and student name
            response = await session.request(
                campus_request.method, campus_request.url, headers=campus_request.headers,
                data=campus_request.data, cookies=campus_request.cookies, raise_for_status=True)

            # validate and extract profile data from response
            result_json = await response.json()
            student_data = result_json.get('s')
            if student_data is None:  # unexpected profile json
                logging.warning(
                    f"Student data in response json has unexpected structure: student_data={result_json}\n"
                    f"Request for admission_number: {admission_number}")
                return True, BAD_RESPONSE_TEXT
            else:
                # get system student id from profile data
                full_name = student_data.get('fn')

            mdeba_data = result_json.get('m')
            if mdeba_data is None:
                logging.warning(
                    f"No mdeba in response json has unexpected structure: mdeba_data={result_json}\n"
                    f"Request for admission_number: {admission_number}")
                return True, NO_MDEBA_DATA_TEXT
            if isinstance(mdeba_data, list):
                if len(mdeba_data) != 1:
                    logging.warning(
                        f"No mdeba in response json has unexpected structure: mdeba_data={result_json}\n"
                        f"Request for admission_number: {admission_number}")
                    return True, NO_MDEBA_DATA_TEXT
                mdeba_data = mdeba_data[0]
                hager = mdeba_data.get('U').strip()
                hager_choice = mdeba_data.get('U_n')
                field = mdeba_data.get('FoS')
                field_choice = mdeba_data.get('FS_n')
                simple = False
            else:
                hager = mdeba_data.get('U')
                simple = True
                hager_choice = None
                field = None
                field_choice = None

        except requests.exceptions.ConnectTimeout:  # safe to retry connection
            logging.warning(
                f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, CONN_TIMEOUT_TEXT
        except requests.exceptions.ReadTimeout:  # server did not send any data in allotted time
            logging.warning(
                f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, BAD_RESPONSE_TEXT
        except requests.exceptions.ConnectionError:
            logging.warning(
                f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, REQUEST_EXCEPTION_TEXT
        except requests.exceptions.HTTPError:  # includes raise_for_status() errors
            logging.warning(
                f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, BAD_RESPONSE_TEXT
        except requests.exceptions.RequestException:  # catch all for requests exception
            logging.warning(
                f"RequestException for admission_number: {admission_number}", exc_info=True)
            return True, REQUEST_EXCEPTION_TEXT
        except Exception:
            logging.warning(
                f"Exception for admission_number: {admission_number}", exc_info=True)
            return True, REQUEST_EXCEPTION_TEXT

        # create appropriate result message text
        message_text = create_mdeba_text(
            full_name, hager, hager_choice, field, field_choice, simple)
        # print('text: ', message_text)

        # join the lines above to create the message text
        return False, message_text


def create_mdeba_text(full_name, hager, hager_choice, field, field_choice, simple=False):
    if not simple:
        return f"Name: {full_name}\n- You are assigned at **{hager}**, your number {hager_choice} country choice.\n - Your assigned field is **{field}**, your number {field_choice} field choice"
    else:
        return f"Name: {full_name}\n- You are assigned at **{hager}**"


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
