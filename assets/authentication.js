
local_storage = window.localStorage;
session_storage = window.sessionStorage;

container = document.getElementById('authentication-button-container');

function decodeIdToken(idToken) {
    try {
        enc = idToken.split('.')[1];
        enc += '='.repeat(((-enc.length % 4) + 4) % 4);
        // console.log(enc)
        dec = JSON.parse(window.atob(enc))
        // console.log(dec)
        return dec
    }
    catch (e) {
        console.log(e)
        return null
    }
}

// window.addEventListener('load', (event) => {
//     console.log('page is fully loaded');

//     token = local_storage.getItem('local-storage');

//     token = JSON.parse(token);
    
//     button = document.getElementById('profile-button');
//     console.log(button)

//     if (('id_token' in token)) {
//         dec = decodeIdToken(token['id_token']);
//         if (dec != null) { 
//             button.innerText = dec['preferred_username']
//         }
//     }
// });