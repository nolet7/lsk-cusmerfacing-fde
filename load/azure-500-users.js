// k6 load profile for a 500-NAMED-USER population (not 500 concurrent by default).
// Usage: BASE_URL=https://... ACCESS_TOKEN=... k6 run load/azure-500-users.js
// The ACCESS_TOKEN must be a valid Entra JWT with Logistics.Read and an authorized
// customer_tenant_id claim. Dedicated sandbox identities, test data and load scope required.
import http from 'k6/http';
import { check, sleep } from 'k6';

const base = (__ENV.BASE_URL || '').replace(/\/$/, '');
const token = __ENV.ACCESS_TOKEN || '';
if (!base || !token) {
  throw Error('Provide BASE_URL and ACCESS_TOKEN. Never commit credentials.');
}
export const options = {
  scenarios: {
    nominal: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 10 },
        { duration: '3m', target: 50 },
        { duration: '5m', target: 50 },
        { duration: '2m', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1500'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  const headers={Authorization:'Bearer '+token};
  const result=http.get(base+'/api/v2/logistics/orders/SO-1001',{headers,timeout:'10s'});
  check(result,{
    'HTTP 200':r=>r.status===200,
    'expected source provenance':r=>{
      try {
        const value=r.json();
        return value.order?.order_id==='SO-1001' && value.sources?.erp && value.sources?.tms;
      }catch(e){return false;}
    },
  });
  sleep(20); // ~3 requests/min per active simulated user
}
