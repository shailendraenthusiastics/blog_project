function saveTokens(data){
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
}
function getAccess(){
    return localStorage.getItem("access");
}
function logout(){
    localStorage.clear();
    window.location.href="/login/";
}
async function refreshToken(){
    const refresh = localStorage.getItem("refresh");
    const response = await fetch("/api/token/refresh/",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({refresh})
    });

    if(response.ok){
        const data = await response.json();
        localStorage.setItem("access", data.access);
        return true;
    } else {
        logout();
        return false;
    }
}
async function authFetch(url, options={}){
    if(!options.headers) options.headers = {};
    options.headers["Authorization"] = "Bearer " + getAccess();
    let response = await fetch(url, options);
    if(response.status === 401){
        const refreshed = await refreshToken();
        if(refreshed){
            options.headers["Authorization"] = "Bearer " + getAccess();
            response = await fetch(url, options);
        }
    }
    return response;
}
