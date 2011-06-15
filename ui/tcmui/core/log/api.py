import logging



log = logging.getLogger("tcmui.core.log.api")



def log_api_call(request, response, content, cache_key=None):
    # log cached api calls at "debug" level and non-cached at "info"
    log_method = cache_key and log.debug or log.info
    log_method(
        "%(method)s %(uri)s",
        {
            "method": request.get("method", "GET"),
            "uri": request["uri"],
            "request": request,
            "response": response,
            "content": content,
            "cache_key": cache_key,
            }
        )
