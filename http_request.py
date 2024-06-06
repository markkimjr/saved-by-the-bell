import requests
import traceback
from typing import Union
from log import Logger

log = Logger.get_instance()


def get_request(url, params=None, headers=None, proxies=None, cookies=None, timeout=5, verify=True, max_retries=1,
                return_json=False, return_res_text=False, allow_redirects=True) -> Union[requests.Response, str, None]:
    res = None
    try:
        session = requests.Session()
        session.headers.update(headers or {})
        for i in range(max_retries):
            res = session.request(method="GET", url=url, params=params, proxies=proxies, cookies=cookies,
                                  timeout=timeout, verify=verify, allow_redirects=allow_redirects)
            if res.status_code == 200:
                if return_json:
                    return res.json()
                if return_res_text:
                    return res.text
                return res

        if res and isinstance(res, requests.Response):
            log.info(f"REQUEST INFO: {res.status_code}/{res.text}")
        return res
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR GETTING REQUEST: {e}")
        return res


def post_request(url, data=None, json=None, headers=None, proxies=None, cookies=None, timeout=5, max_retries=1,
                 return_json=False, return_res_text=False, allow_redirects=True) -> Union[requests.Response, str, None]:
    res = None
    try:
        session = requests.Session()
        session.headers.update(headers or {})
        for i in range(max_retries):
            res = session.request(method="POST", url=url, data=data, json=json, headers=headers, proxies=proxies,
                                  cookies=cookies, timeout=timeout, allow_redirects=allow_redirects)
            if res.status_code == 200 or res.status_code == 201:
                if return_res_text:
                    return res.text
                if return_json:
                    return res.json()
                return res

        if res and isinstance(res, requests.Response):
            log.info(f"REQUEST INFO: {res.status_code}/{res.text}")
        return res
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR POSTING REQUEST: {e}")
        return res
