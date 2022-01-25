import subprocess

com = 'curl --user-agent "dqcurl"  --cacert /etc/grid-security/certificates/usercert.pem --key /etc/grid-security/certificates/userkey.pem --compressed -H "Authorization: Bearer eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI0ZTkyMzgyZi03MDJmLTQ5MTktYTUzMy05ZjhmZTdiZjY5Y2YiLCJhdWQiOiJkYTFlYjY1Zi03NmUyLTQ5NTMtYTUwMy1iYjQ2ZTJhMjgxZDMiLCJraWQiOiJyc2ExIiwiaXNzIjoiaHR0cHM6XC9cL2F0bGFzLWF1dGgud2ViLmNlcm4uY2hcLyIsIm5hbWUiOiJUVUFOIE1JTkggUEhBTSIsImdyb3VwcyI6WyJhdGxhcyJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0dXBoYW0iLCJvcmdhbmlzYXRpb25fbmFtZSI6ImF0bGFzIiwiZXhwIjoxNjQyODY5Njk3LCJpYXQiOjE2NDI4NjkwOTcsImp0aSI6IjQ0OTJlZGU3LTQ5ZmMtNDg3NS04MGE4LTgyNWRiYzBiZGIxNiIsImVtYWlsIjoidHVhbi5taW5oLnBoYW1AY2Vybi5jaCJ9.fuiorfZau7OUpICxtXSyngNtY_QZcsK6MJjxl77J-tECSbkYSlEhzbtAI_XXMGrxjIaDSpl3JDRa8WV5Iukwp2ExoQ0XilMz_rWmTvofyvTA8fcYcJCfz7EFRFDxI25BlK7l6oWqqd3QDyaC6Bzp_kBN-QblA0MQhImaaUgyEZ8" -H "Origin: atlas" -F "file=@jobO.78cd9cdf-5837-4640-b253-b16eaeed82ca.tar" https://aipanda047.cern.ch:25443/server/panda/putFile -v'
p = subprocess.Popen(com, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# set_trace()
print(p)
data, unused_err = p.communicate()
retcode = p.poll()

print(f'data: {data}')
print(f'unused_err: {unused_err}')
print(f'retcode: {retcode}')
