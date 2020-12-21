#!/usr/bin/python

import time
import datetime
import swagger_client


PROJECT_REPO_NAME = "TruePLMprojectsRep"


def load_properties(filepath, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(filepath, "rt") as file:
        for line in file:
            lin = line.strip()
            if lin and not lin.startswith(comment_char):
                key_value = lin.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props


def main():
    try:
        run()
    except Exception as ex:
        print(ex)


def login(user, group, password):
    """
    Returns user token by provided user credentials
    :param user: user name
    :param group: user group name. TruePLM has only 'sdai-group'
    :param password: user password
    :return: string token to be used in any other web requests
    """
    api = swagger_client.api.authorization_controller_api.AuthorizationControllerApi()
    # Normally web server (Tomcat, etc) and EDM server are on the same host
    # That is why "localhost" is hardcoded here.
    # However we may use any publicity available EDM server to connect to
    res = api.login_submit_using_post(
        user=user, group=group, _pass=password, port=9090, server='localhost')

    if res.error is not None:
        raise Exception("Login error")
    return res.token


def logout(token):
    """
    Closes existing token
    :param token: user token to be closed
    :return: nothing
    """
    api = swagger_client.api.authorization_controller_api.AuthorizationControllerApi()
    api.logout_using_delete(token)


def get_projects_for_user(token):
    """
    Retrieves detailed info about current TruePLM user
    Prints available project names
    :param token: user token
    :return: list[UsersProjectInfo]
    """
    api = swagger_client.api.admin_controller_api.AdminControllerApi()
    res = api.get_user_projects_using_get(token=token)

    if res is not None:
        print('Available projects:')
        for it in res:
            print('Name: ' + it.in_project.name)
    return res


def search_for_sensor_data_container(token, model_name, repo_name, user_type):
    """
    Searches breakdown element where required sensor data is stored
    :param token: user token
    :param model_name: PLCS model name
    :param repo_name: EDM repository name. Normally it is 'TruePLMprojectsRep'
    :param user_type: TruePLM user type: 'urn:rdl:epm-std:project_manager', 'urn:rdl:epm-std:project_admin', ...
    :return: BreakdownElementSearchResultInfo
    """
    api = swagger_client.api.breakdown_controller_api.BreakdownControllerApi()
    limit = 10
    property_name = "urn:rdl:Bike:serial number"  # the value depends on a project
    property_value = "13483027"  # the value depends on a project

    res = api.advanced_search_node_using_get(
        token=token, model=model_name, repository=repo_name, type=user_type,
        pattern='*', descr='*', limit=limit,
        prop_name=[property_name], prop_val=[property_value])

    return res[0]


def get_user_type_on_project(token, project_name):
    """
    Retrieves first (from possible multiple) user type on the  project
    :param token: user token
    :param project_name: PLCS model name (project name)
    :return: user type as string
        ('urn:rdl:epm-std:project_manager', 'urn:rdl:epm-std:project_admin', ...)
    """
    api = swagger_client.api.admin_controller_api.AdminControllerApi()
    res = api.get_user_projects_using_get(token)
    for it in res:
        if it.in_project.project_model_id == project_name:
            return it.user_registered_as[0]
    return None


def retrieve_sensor_data(token, repo_name, model_name, element_id):
    """
    Retrieves sensor data stored in the given breakdown element
    Property name and 'to' and 'from' values are hardcoded here
    :param token: user token
    :param repo_name: EDM repository name. Normally it is 'TruePLMprojectsRep'
    :param model_name: PLCS model name (project name)
    :param element_id: Breakdown element id
    :return: Nothing
    """
    api = swagger_client.api.breakdown_controller_api.BreakdownControllerApi()
    # Quite tricky way to get Unix timestamp from human readable time format
    tm = time.mktime(datetime.datetime.strptime(
        "2020/04/27 00:00:00", "%Y/%m/%d %H:%M:%S").timetuple())
    dt_from = str(int(tm))

    page = 1  # first page
    page_size = 3  # take just few rows
    property_uri = "urn:rdl:Bike:point list"

    aggr_prop = api.get_aggr_prop_using_get(
        token=token, repository=repo_name, model=model_name, node=element_id,
        prop=property_uri, _from=dt_from, to=None, page=page, size=page_size)

    print("Sensor data:")
    for val in aggr_prop.values:
        print(val)


def run():
    """
    Function that does all operations.
    But it goes not handle exceptions
    :return:
    """
    props = load_properties('./democli.properties')

    login_name = props['login_name']
    group_name = props['group_name']
    password = props['password']

    token = login(login_name, group_name, password)
    projects = get_projects_for_user(token)

    if len(projects) == 0:
        raise Exception("No projects found")

    proj_info = projects[0].in_project

    user_type = get_user_type_on_project(token, proj_info.project_model_id)

    # we expect only one single element to be found
    element = search_for_sensor_data_container(
        token, proj_info.project_model_id, PROJECT_REPO_NAME, user_type)

    retrieve_sensor_data(
        token, PROJECT_REPO_NAME, proj_info.project_model_id, element.bkdn_elem_info.instance_id)

    logout(token)


main()
