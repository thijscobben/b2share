import reqwest from 'reqwest'


const DEFAULT_TIMEOUT_GET_MS = 10 * 1000; // 10 seconds
const DEFAULT_TIMEOUT_POST_MS = 10 * 1000; // 10 seconds


export let errorHandler = {fn:function(text){}};


export function ajaxGet({url, params, etag, successFn, errorFn, completeFn}) {
    console.log("--- ajaxGet:", url, params);
    const aobj = {
        url: url,
        type: 'json',
        contentType: 'application/json',
        success: successFn,
        error: errorFn,
        complete: completeFn,
        timeout: DEFAULT_TIMEOUT_GET_MS,
    }
    if (params) {
        aobj.data = params;
    }
    if (etag) {
        aobj.headers = {'If-None-Match': etag};
    }
    return ajaxWithError(aobj);
}


export function ajaxPost({url, params, successFn, errorFn, completeFn}) {
    console.log("--- ajaxPost:", url, params);
    const aobj = {
        method: 'post',
        url: url,
        type: 'json',
        contentType: 'application/json',
        success: successFn,
        error: errorFn,
        complete: completeFn,
        timeout: DEFAULT_TIMEOUT_POST_MS,
    }
    if (params) {
        aobj.data = JSON.stringify(params);
    }
    return ajaxWithError(aobj);
}


function ajaxWithError(ajaxObject) {
    if (!ajaxObject.error) {
        ajaxObject.error = function(xhr) {
            console.error("ajax error, xhr: ", xhr);
            if (!xhr) {
                errorHandler.fn("Unexpected error");
                return;
            }
            if (xhr.readyState === 0) {
                errorHandler.fn("Network error, please check your internet connection");
            } else {
                errorHandler.fn(`Error: ${xhr.statusText}`);
            }
        };
    }

    ajaxWithToken(ajaxObject);
};


let userToken = "";
function getSessionUserToken() { return userToken; }
function setSessionUserToken(token) { userToken = token; }


function ajaxWithToken(ajaxObject) {
    let request = null;

    const token = getSessionUserToken();
    if (token && ajaxObject.url.startsWith("http")) {
        ajaxObject.headers = ajaxObject.headers || {};
        ajaxObject.headers['Authorization'] = 'B2SHARE ' + token;
    }

    const oldSuccess = ajaxObject.success;
    ajaxObject.success = function(data) {
        const prefix = "B2SHARE";
        if (ajaxObject.url.startsWith("http")) {
            var token = request.getResponseHeader('x-token');
            if (token && token.startsWith(prefix)) {
                token = token.substring(prefix.length +1, token.length);
                setSessionUserToken(token);
            }
        }
        var etag = request.getResponseHeader('ETag');
        console.log('  > ajaxRet:', ajaxObject.url, data, {etag: etag});
        return oldSuccess(data, etag);
    }

    const oldError = ajaxObject.error;
    ajaxObject.error = function(xhr) {
        if (xhr.status == 401) {
            setSessionUserToken("");
        }
        return oldError(xhr);
    }

    request = reqwest(ajaxObject).request;
};