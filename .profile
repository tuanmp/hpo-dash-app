# set dynamic config variables 
export PATH=/app/.heroku/python/bin:$PATH
export PYTHONPATH=/app/.heroku/python/lib/python3.9/site-packages${PYTHONPATH:+:$PYTHONPATH}
export PANDA_CONFIG_ROOT=~/.pathena
export PANDA_SYS=/app/.heroku/python
export PANDA_PYTHONPATH=/app/.heroku/python/lib/python3.9/site-packages