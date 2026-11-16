import {PublicClientApplication, InteractionRequiredAuthError} from '@azure/msal-browser';
import {config} from './config.js';

const app = new PublicClientApplication({
  auth: {
    clientId:config.clientId,
    authority:'https://login.microsoftonline.com/'+config.tenantId,
    redirectUri:window.location.origin,
    postLogoutRedirectUri:window.location.origin,
  },
  cache:{cacheLocation:'sessionStorage'},
});
await app.initialize();
await app.handleRedirectPromise();
const $ = (id)=>document.getElementById(id);
const request={scopes:[config.apiScope]};
const getAccount=()=>app.getActiveAccount() || app.getAllAccounts()[0];

function updateSession(){
  const account=getAccount();
  $('session').textContent=account?'Signed in: '+account.username:'Not signed in';
  for(const id of ['lookup','exceptions','create','cases']) $(id).disabled=!account;
}
async function getToken(){
  const account=getAccount();
  if(!account)throw new Error('Sign in first');
  try{
    const response=await app.acquireTokenSilent({...request,account});
    return response.accessToken;
  }catch(e){
    if(e instanceof InteractionRequiredAuthError){
      await app.acquireTokenRedirect({...request,account});
      return null;
    }
    throw e;
  }
}
async function call(path,method='GET',payload=null){
  $('output').textContent='Requesting authorized data...';
  try{
    const token=await getToken();
    if(!token)return;
    const response=await fetch(config.apiBase+path,{
      method,
      headers:{Authorization:'Bearer '+token,...(payload?{'Content-Type':'application/json'}:{})},
      body:payload?JSON.stringify(payload):undefined,
      cache:'no-store',
    });
    const body=await response.json();
    // Do not show token, credentials, exception stack trace or arbitrary HTML.
    $('output').textContent=JSON.stringify({http_status:response.status,response:body},null,2);
  }catch(e){
    $('output').textContent='Request failed: '+e.message;
  }
}
$('signin').onclick=async()=>{await app.loginRedirect(request);};
$('signout').onclick=async()=>{const account=getAccount();if(account)await app.logoutRedirect({account});};
$('lookup').onclick=()=>call('/api/v2/logistics/orders/'+encodeURIComponent($('order').value.trim()));
$('exceptions').onclick=()=>call('/api/v2/logistics/exceptions');
$('create').onclick=()=>call('/api/v2/logistics/investigations','POST',{
  order_id:$('order').value.trim(),note:$('note').value.trim(),
});
$('cases').onclick=()=>call('/api/v2/logistics/investigations');
updateSession();
